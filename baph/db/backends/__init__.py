from __future__ import absolute_import
from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.utils.functional import cached_property
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool

from baph.db import DEFAULT_DB_ALIAS


def django_backend_to_sqla_drivername(backend):
    if backend.find('.') == -1:
        # not a django backend, pass it through
        return backend
    backend = backend.rsplit('.',1)[-1]
    if backend == 'sqlite3':
        return 'sqlite'
    elif backend == 'postgresql_psycopg2':
        return 'postgresql'
    return backend

def django_config_to_sqla_config(config):
    """
    Takes a dict of django db config params and converts the keys
    to be useable by sqla's URL() function. If 'DRIVERNAME' is not present,
    it will attempt to guess based on the value of ENGINE
    """
    drivername = config.get('DRIVERNAME', 
        django_backend_to_sqla_drivername(config['ENGINE']))
    params = {
        'drivername': drivername,
        'username': config.get('USER', None),
        'password': config.get('PASSWORD', None),
        'host': config.get('HOST', None),
        'port': config.get('PORT', None),
        'database': config.get('NAME', None),
        'query': config.get('OPTIONS', None),
        }
    for k, v in params.items():
        if not v:
            del params[k]
    return params

def load_engine(config):
    url = URL(**django_config_to_sqla_config(config))
    try:
        engine = create_engine(url, poolclass=NullPool,
                               echo=getattr(settings, 'BAPH_DB_ECHO', False))
        return engine
    except ArgumentError:
        error_msg = "%r isn't a valid dialect/driver" % url
        raise ImproperlyConfigured(error_msg)

def find_circular_dependencies(metadata):
    dependencies = defaultdict(set)
    fks = defaultdict(set)
    rsp = defaultdict(set)

    for t in metadata.sorted_tables:
        for fk in t.foreign_key_constraints:
            dependencies[t.name].add(fk.referred_table.name)
            fks[(t.name, fk.referred_table.name)].add(fk)

    def walk_graph(name, path=None):
        if path is None:
            path = []
        for dependency in dependencies[name]:
            if dependency in path:
                #print "Circular dependency:","->".join(path+[dependency])
                for fk in fks[(path[-1], dependency)]:
                    rsp[fk.table].update(fk.column_keys)
                continue
            walk_graph(dependency,path+[dependency])

    for name in dependencies.keys():
        walk_graph(name)

    return rsp

def scopefunc():
    return 'single'

class DatabaseWrapper(object):
    def __init__(self, settings_dict, alias=DEFAULT_DB_ALIAS):
        # `settings_dict` should be a dictionary containing keys such as
        # NAME, USER, etc. It's called `settings_dict` instead of `settings`
        # to disambiguate it from Django settings modules.
        from baph.db.models.base import get_declarative_base
        self.settings_dict = settings_dict
        self.alias = alias
        self.engine = load_engine(settings_dict)
        self.Base = get_declarative_base(bind=self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.sessionmaker = scoped_session(sessionmaker(
            bind=self.engine, autoflush=False))
        # TODO: uncomment line below once transactional tests are ready
        #    bind=self.engine, autoflush=False), scopefunc=scopefunc)
    '''
        self._connection = None
        #self.session_factory = sessionmaker(bind=self.engine)
        #self.sessionmaker = scoped_session(sessionmaker(
        #    bind=self.engine, autoflush=False))
        self._sessionmaker = None
        self._session_factory = None

    @property
    def connection(self):
        print 'orm.connection called'
        if self._connection is None:
            print '  init'
            #if connections[self.alias].connection is None:
            #    connections[self.alias].connect()
            self._connection = connections[self.alias].connection
            #self._connection = self.engine.connect()
        print 'returning ', self._connection
        return self._connection

    @property
    def sessionmaker(self):
        connection = connections[self.alias]
        return connection.sessionmaker
        print 'orm.sessionmaker called'
        print connection
        #assert False
        if self._sessionmaker is None:
            print '  init'
            self._sessionmaker = scoped_session(sessionmaker(
                bind=self.connection, autoflush=False))
        print 'returning ', self._sessionmaker
        print '  bind:', self._sessionmaker.bind
        return self._sessionmaker

    @property
    def session_factory(self):
        connection = connections[self.alias]
        return connection.session_factory
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.connection)
        return self._session_factory
    '''

    def __eq__(self, other):
        return self.alias == other.alias

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.alias)

    def cursor(self):
        return self.sessionmaker()

    def get_base_engine(self):
        """ Return an engine with no schema, to allow operations before 
            schemas have been setup """
        url = deepcopy(self.engine.url)
        url.database = None
        return create_engine(url)

    @cached_property
    def circular_dependencies(self):
        return find_circular_dependencies(self.Base.metadata)

    @cached_property
    def supports_transactions(self):
        """ Confirm support for transactions."""
        session = self.sessionmaker()
        session.execute('CREATE TABLE ROLLBACK_TEST (X INT)')
        session.execute('INSERT INTO ROLLBACK_TEST (X) VALUES (8)')
        session.rollback()
        results = session.execute('SELECT COUNT(X) FROM ROLLBACK_TEST')
        count, = results.fetchone()
        session.execute('DROP TABLE ROLLBACK_TEST')
        return count == 0

    def check_constraints(self, table_names=None):
        # TODO: implement this
        """
        Checks each table name in `table_names` for rows with invalid foreign key references. This method is
        intended to be used in conjunction with `disable_constraint_checking()` and `enable_constraint_checking()`, to
        determine if rows with invalid references were entered while constraint checks were off.

        Raises an IntegrityError on the first invalid foreign key reference encountered (if any) and provides
        detailed information about the invalid reference in the error message.

        Backends can override this method if they can more directly apply constraint checking (e.g. via "SET CONSTRAINTS
        ALL IMMEDIATE")
        """
        cursor = self.cursor()
        if table_names is None:
            table_names = self.introspection.table_names(cursor)
        for table_name in table_names:
            primary_key_column_name = self.introspection.get_primary_key_column(cursor, table_name)
            if not primary_key_column_name:
                continue
            key_columns = self.introspection.get_key_columns(cursor, table_name)
            for column_name, referenced_table_name, referenced_column_name in key_columns:
                cursor.execute("""
                    SELECT REFERRING.`%s`, REFERRING.`%s` FROM `%s` as REFERRING
                    LEFT JOIN `%s` as REFERRED
                    ON (REFERRING.`%s` = REFERRED.`%s`)
                    WHERE REFERRING.`%s` IS NOT NULL AND REFERRED.`%s` IS NULL"""
                    % (primary_key_column_name, column_name, table_name, referenced_table_name,
                    column_name, referenced_column_name, column_name, referenced_column_name))
                for bad_row in cursor.fetchall():
                    raise utils.IntegrityError("The row in table '%s' with primary key '%s' has an invalid "
                        "foreign key: %s.%s contains a value '%s' that does not have a corresponding value in %s.%s."
                        % (table_name, bad_row[0],
                        table_name, column_name, bad_row[1],
                        referenced_table_name, referenced_column_name))
