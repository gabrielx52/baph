import json
import os
import sys

from django.core.cache import get_cache
from MySQLdb.converters import conversions, escape
from sqlalchemy import inspect
from sqlalchemy import *
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.orm import lazyload, contains_eager, class_mapper
from sqlalchemy.orm.util import identity_key
from sqlalchemy.sql import compiler

from baph.core.management.base import NoArgsCommand
from baph.db.orm import ORM


orm = ORM.get()
Base = orm.Base

def get_namespaced_models():
    nsmap = {}
    for k,v in Base._decl_class_registry.items():
        if k.startswith('_'):
            # skip internal SA attrs
            continue
        ns = v().get_cache_namespaces()
        if not ns:
            continue
        for k2, v2 in ns:
            if k2 not in nsmap:
                nsmap[k2] = set()
            nsmap[k2].add(k)
    return nsmap

class Command(NoArgsCommand):
    requires_model_validation = True

    def handle_noargs(self, **options):
        ns_models = get_namespaced_models()
        while True:
            cmd = raw_input('\nIncrement which ns key? (ENTER to list, Q to quit): ').strip()
            if not cmd:
                for key, models in ns_models.items():
                    print '\t%s (triggers reloads on %s)' % (key, ', '.join(models))
                continue            
            if cmd in ('q', 'Q'):
                break
            if not cmd in ns_models:
                print 'Invalid ns key: %s' % cmd
                continue
            key = cmd

            while True:
                cmd = raw_input('Enter the value for "%s" (ENTER to cancel): ' % key).strip()
                if not cmd:
                    break

                cache = get_cache('objects')
                version_key = '%s_%s' % (key, cmd)
                version = cache.get(version_key)
                print '\tcurrent value of %s: %s' % (version_key, version)
                if version is None:
                    version = 0
                version += 1
                cache.set(version_key, version)
                version = cache.get(version_key)
                print '\tnew value of %s: %s' % (version_key, version)

