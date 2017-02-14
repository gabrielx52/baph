from __future__ import unicode_literals

import logging
import sys
import types
import warnings

from django.conf import settings
from django.core import signals
from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed
from django.core.urlresolvers import get_urlconf, set_urlconf, RegexURLResolver
from django.db import connections, transaction
from django.utils import six
from baph.utils.module_loading import import_string

from .exception import (
    convert_exception_to_response, get_exception_response,
    handle_uncaught_exception,
)
from utils import get_resolver

logger = logging.getLogger('django.request')


class BaseHandler(object):
  middleware_setting_key = 'MIDDLEWARE'
  urlconf_setting_key = 'ROOT_URLCONF'

  def __init__(self):
    self._request_middleware = None
    self._view_middleware = None
    self._template_response_middleware = None
    self._response_middleware = None
    self._exception_middleware = None
    self._middleware_chain = None

  def load_middleware(self):
    """
    Populate middleware lists from settings

    Must be called after the environment is fixed (see __call__ in subclasses).
    """
    self._request_middleware = []
    self._view_middleware = []
    self._template_response_middleware = []
    self._response_middleware = []
    self._exception_middleware = []

    handler = convert_exception_to_response(self._get_response)
    middleware_paths = getattr(settings, self.middleware_setting_key, ())
    for middleware_path in reversed(middleware_paths):
      middleware = import_string(middleware_path)
      try:
        mw_instance = middleware(handler)
      except MiddlewareNotUsed as exc:
        if settings.DEBUG:
          if six.text_type(exc):
            logger.debug('MiddlewareNotUsed(%r): %s', middleware_path, exc)
          else:
            logger.debug('MiddlewareNotUsed: %r', middleware_path)
        continue

      if mw_instance is None:
        raise ImproperlyConfigured(
          'Middleware factory %s returned None.' % middleware_path
        )

      if hasattr(mw_instance, 'process_view'):
        self._view_middleware.insert(0, mw_instance.process_view)
      if hasattr(mw_instance, 'process_template_response'):
        self._template_response_middleware.append(
          mw_instance.process_template_response)
      if hasattr(mw_instance, 'process_exception'):
        self._exception_middleware.append(mw_instance.process_exception)

      handler = convert_exception_to_response(mw_instance)

    # We only assign to this when initialization is complete as it is used
    # as a flag for initialization being complete.
    self._middleware_chain = handler

  def make_view_atomic(self, view):
    non_atomic_requests = getattr(view, '_non_atomic_requests', set())
    for db in connections.all():
      if db.settings_dict['ATOMIC_REQUESTS'] and \
         db.alias not in non_atomic_requests:
        view = transaction.atomic(using=db.alias)(view)
    return view

  def get_exception_response(self, request, resolver, status_code, exception):
    return get_exception_response(request, resolver, status_code, exception,
                                  self.__class__)

  def get_response(self, request):
    """Return an HttpResponse object for the given HttpRequest."""
    # Setup default url resolver for this thread
    urlconf = getattr(settings, self.urlconf_setting_key)
    set_urlconf(urlconf)

    response = self._middleware_chain(request)
    response._closable_objects.append(request)

    # If the exception handler returns a TemplateResponse that has not
    # been rendered, force it to be rendered.
    if not getattr(response, 'is_rendered', True) \
        and callable(getattr(response, 'render', None)):
      response = response.render()

    if response.status_code == 404:
      logger.warning(
        'Not Found: %s', request.path,
        extra={'status_code': 404, 'request': request},
      )

    return response

  def get_resolver(self, urlconf=None):
    if urlconf is None:
      from django.conf import settings
      urlconf = getattr(settings, self.urlconf_setting_key)
    return get_resolver(urlconf)

  def _get_response(self, request):
    """
    Resolve and call the view, then apply view, exception, and
    template_response middleware. This method is everything that happens
    inside the request/response middleware.
    """
    response = None

    if hasattr(request, 'urlconf'):
      urlconf = request.urlconf
      set_urlconf(urlconf)
      resolver = self.get_resolver(urlconf)
    else:
      resolver = self.get_resolver()

    resolver_match = resolver.resolve(request.path_info)
    callback, callback_args, callback_kwargs = resolver_match
    request.resolver_match = resolver_match

    # Apply view middleware
    for middleware_method in self._view_middleware:
      response = middleware_method(request, callback, callback_args,
                                   callback_kwargs)
      if response:
        break

    if response is None:
      wrapped_callback = self.make_view_atomic(callback)
      try:
        response = wrapped_callback(request, *callback_args, **callback_kwargs)
      except Exception as e:
        response = self.process_exception_by_middleware(e, request)

    # Complain if the view returned None (a common error).
    if response is None:
      if isinstance(callback, types.FunctionType):    # FBV
        view_name = callback.__name__
      else:                                           # CBV
        view_name = callback.__class__.__name__ + '.__call__'

      raise ValueError(
        "The view %s.%s didn't return an HttpResponse object. It "
        "returned None instead." % (callback.__module__, view_name)
      )

    # If the response supports deferred rendering, apply template
    # response middleware and then render the response
    elif hasattr(response, 'render') and callable(response.render):
      for middleware_method in self._template_response_middleware:
        response = middleware_method(request, response)
        # Complain if the template response middleware returned None
        # (a common error).
        if response is None:
          raise ValueError(
            "%s.process_template_response didn't return an "
            "HttpResponse object. It returned None instead."
            % (middleware_method.__self__.__class__.__name__)
          )

      try:
        response = response.render()
      except Exception as e:
        response = self.process_exception_by_middleware(e, request)

    return response

  def process_exception_by_middleware(self, exception, request):
    """
    Pass the exception to the exception middleware. If no middleware
    return a response for this exception, raise it.
    """
    for middleware_method in self._exception_middleware:
      response = middleware_method(request, exception)
      if response:
        return response
    raise

  def handle_uncaught_exception(self, request, resolver, exc_info):
    """Allow subclasses to override uncaught exception handling."""
    return handle_uncaught_exception(request, resolver, exc_info)

  def _legacy_get_response(self, request):
    """
    Apply process_request() middleware and call the main _get_response(),
    if needed. Used only for legacy MIDDLEWARE_CLASSES.
    """
    response = None
    # Apply request middleware
    for middleware_method in self._request_middleware:
      response = middleware_method(request)
      if response:
        break

    if response is None:
      response = self._get_response(request)
    return response