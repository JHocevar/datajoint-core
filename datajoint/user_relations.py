"""
Hosts the table tiers, user relations should be derived from.
"""

from .base_relation import BaseRelation
from .autopopulate import AutoPopulate
from .utils import from_camel_case

_base_regexp = r'[a-z]+[a-z0-9]*(_[a-z]+[a-z0-9]*)*'


class classproperty:
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class UserRelation(BaseRelation):
    """
    A subclass of UserRelation is a dedicated class interfacing a base relation.
    UserRelation is initialized by the decorator generated by schema().
    """
    _connection = None
    _context = None
    _heading = None
    _regexp = None
    _prefix = None

    @classproperty
    def connection(cls):
        return cls._connection

    @classproperty
    def full_table_name(cls):
        return r"`{0:s}`.`{1:s}`".format(cls.database, cls.table_name)


class Manual(UserRelation):
    """
    Inherit from this class if the table's values are entered manually.
    """

    _prefix = r''
    _regexp = r'(?P<manual>' + _prefix + _base_regexp + ')'

    @classproperty
    def table_name(cls):
        """
        :returns: the table name of the table formatted for SQL.
        """
        return from_camel_case(cls.__name__)


class Lookup(UserRelation):
    """
    Inherit from this class if the table's values are for lookup. This is
    currently equivalent to defining the table as Manual and serves semantic
    purposes only.
    """

    _prefix = '#'
    _regexp = r'(?P<lookup>' + _prefix + _base_regexp.replace('TIER', 'lookup') + ')'

    @classproperty
    def table_name(cls):
        """
        :returns: the table name of the table formatted for mysql.
        """
        return cls._prefix + from_camel_case(cls.__name__)

    def _prepare(self):
        """
        Checks whether the instance has a property called `contents` and inserts its elements.
        """
        if hasattr(self, 'contents'):
            self.insert(self.contents, skip_duplicates=True)


class Imported(UserRelation, AutoPopulate):
    """
    Inherit from this class if the table's values are imported from external data sources.
    The inherited class must at least provide the function `_make_tuples`.
    """

    _prefix = '_'
    _regexp = r'(?P<imported>' + _prefix + _base_regexp + ')'

    @classproperty
    def table_name(cls):
        """
        :returns: the table name of the table formatted for mysql.
        """
        return cls._prefix + from_camel_case(cls.__name__)


class Computed(UserRelation, AutoPopulate):
    """
    Inherit from this class if the table's values are computed from other relations in the schema.
    The inherited class must at least provide the function `_make_tuples`.
    """

    _prefix = '__'
    _regexp = r'(?P<computed>' + _prefix + _base_regexp + ')'

    @classproperty
    def table_name(cls):
        """
        :returns: the table name of the table formatted for SQL.
        """
        return cls._prefix + from_camel_case(cls.__name__)


class Part(UserRelation):
    """
    Inherit from this class if the table's values are details of an entry in another relation
    and if this table is populated by this relation. For example, the entries inheriting from
    dj.Part could be single entries of a matrix, while the parent table refers to the entire matrix.
    Part relations are implemented as classes inside classes.
    """

    _regexp = r'(?P<master>' + '|'.join(
        [c._regexp for c in [Manual, Imported, Computed, Lookup]]
    ) + r'){1,1}' + '__' + r'(?P<part>' + _base_regexp + ')'

    _master = None

    @classproperty
    def master(cls):
        return cls._master

    @classproperty
    def table_name(cls):
        return cls.master.table_name + '__' + from_camel_case(cls.__name__)
