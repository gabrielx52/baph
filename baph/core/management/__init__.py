from argparse import ArgumentParser
import os
import sys

import django
from django.conf import settings
from django.core import management
from django.core.exceptions import ImproperlyConfigured

import baph
from baph.core.management.base import handle_default_options, CommandError
from baph.core.preconfig.loader import PreconfigLoader
from .utils import get_command_options, get_parser_options


def get_subcommand(args):
  " returns the first item in args which doesn't begin with a hyphen "
  for arg in args:
    if arg and arg[0] != '-':
      return arg
  return 'help'

class ManagementUtility(management.ManagementUtility):
  """
  Encapsulates the logic of the django-admin and manage.py utilities.

  A ManagementUtility has a number of commands, which can be manipulated
  by editing the self.commands dictionary.
  """
  def execute(self):
    """
    Given the command-line arguments, this figures out which subcommand is
    being run, creates a parser appropriate to that command, and runs it.
    """
    # Preprocess options to extract --settings and --pythonpath.
    # These options could affect the commands that are available, so they
    # must be processed early.
    #parser = CommandParser(None, usage="%(prog)s subcommand [options] [args]", add_help=False)
    #
    preconfig = PreconfigLoader.load()
    if preconfig:
      parser = preconfig.get_parser()
    else:
      parser = ArgumentParser()
    parser.add_argument('--settings')
    parser.add_argument('--pythonpath')
    parser.add_argument('args', nargs='*')  # catch-all
    options, args = parser.parse_known_args(self.argv[1:])
    subcommand = get_subcommand(options.args)
    try:
      handle_default_options(options)
    except CommandError:
      pass  # Ignore any option errors at this point.

    args = options.args

    try:
      settings.INSTALLED_APPS
    except ImproperlyConfigured as exc:
      self.settings_exception = exc

    if settings.configured:
      # Start the auto-reloading dev server even if the code is broken.
      # The hardcoded condition is a code smell but we can't rely on a
      # flag on the command class because we haven't located it yet.
      if subcommand == 'runserver' and '--noreload' not in self.argv:
        try:
          autoreload.check_errors(django.setup)()
        except Exception:
          # The exception will be raised later in the child process
          # started by the autoreloader. Pretend it didn't happen by
          # loading an empty list of applications.
          apps.all_models = defaultdict(OrderedDict)
          apps.app_configs = OrderedDict()
          apps.apps_ready = apps.models_ready = apps.ready = True

      # In all other cases, baph.setup() is required to succeed.
      else:
        baph.setup()

    self.autocomplete()

    if subcommand == 'help':
      if '--commands' in options.args:
        sys.stdout.write(self.main_help_text(commands_only=True) + '\n')
      elif len(options.args) < 2:
        sys.stdout.write(self.main_help_text() + '\n')
      else:
        self.fetch_command(options.args[1]) \
            .print_help(self.prog_name, options.args[1])
    # Special-cases: We want 'django-admin --version' and
    # 'django-admin --help' to work, for backwards compatibility.
    elif subcommand == 'version' or self.argv[1:] == ['--version']:
      sys.stdout.write(django.get_version() + '\n')
    elif self.argv[1:] in (['--help'], ['-h']):
      sys.stdout.write(self.main_help_text() + '\n')
    else:
      command = self.fetch_command(subcommand)
      '''
      if getattr(command, 'allow_unknown_args', False):
        argv = self.argv
      else:
        #preconfig = PreconfigLoader.load()
        #parser = preconfig.get_parser()

        preconf_opts = get_parser_options(parser)
        print 'preconf opts:', preconf_opts
        supported_opts = get_command_options(command)
        print 'supported:', supported_opts
        ignorable = preconf_opts - supported_opts
        print 'ignorable:', ignorable
        options, args = parser.parse_known_args(self.argv[1:])
        print 'opts:', options
        print 'args:', args
        argv = []
        for item in self.argv:
          if item.startswith('-'):
            key = item.split('=')[0]
            if key in ignorable:
              continue
          argv.append(item)
      '''
      command.run_from_argv(self.argv)

def execute_from_command_line(argv=None):
  """
  A simple method that runs a ManagementUtility.
  """
  utility = ManagementUtility(argv)
  utility.execute()