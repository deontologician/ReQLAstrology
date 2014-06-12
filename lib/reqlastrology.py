from __future__ import print_function

from itertools import izip
import re
import json
import copy
import weakref

import rethinkdb as r


class Field(object):
    '''Specifies a top level field in an object.
    '''
    def __init__(
            self,
            type_=str,
            name=None,
            primary_key=False,
            required=False):
        self.type_ = _convert_from_builtin(type_)
        self.name = name
        self.required = required
        self.primary_key = primary_key

        self.value = None

    def __get__(self, parent, type_=None):
        if parent is None:
            return self.name
        else:
            return parent.state[self.name]

    def __set__(self, parent, value):
        if self.type_.validate(value):
            parent.state[self.name] = value
        else:
            raise ValueError(
                '{} did not validate against the spec: {}'
                .format(value, self.type_)
            )


class Validating(object):
    '''Base class for validating field types'''

    def validate(self, data):
        raise NotImplemented 

    def __eq__(self, other):
        return self.arg == other.arg

    def __repr__(self):
        if hasattr(self, 'arg'):
            fmt = '{classname}({self.arg})'
        else:
            fmt = '{classname}()'
        return fmt.format(
            classname=self.__class__.__name__,
            self=self,
        )

class ValidationError(Exception):
    '''Raised when a validation fails'''
    def __init__(self, msg, expected, received):
        self.msg = msg
        self.expected = expected
        self.received = received
        super(ValidationError, self).__init__(msg)


class InvalidSpec(Exception):
    '''Raised when a spec is malformed'''
    
    def __init__(self, msg, *args, **kwargs):
        super(InvalidSpec, self).__init__(msg.format(*args, **kwargs))


def _convert_from_builtin(spec):
    '''Converts from a primitive type shorthand to the internal
    objects.
    '''
    if hasattr(spec, 'validate'):
        return spec
    elif hasattr(spec, 'to_validating'):
        return spec.to_validating()
    elif spec is None:
        return Whatever()
    elif isinstance(spec, list) and len(spec) == 1:
        return List(*spec)
    elif isinstance(spec, set):
        return Enum(*spec)
    elif isinstance(spec, dict):
        return Object(**spec)
    elif spec in (str, int, float, bool):
        try:
            return Primitive(spec)
        except TypeError as te:
            raise InvalidSpec(te.message)
    elif isinstance(spec, (str, int, float, bool, object)):
        try:
            return Literally(spec)
        except TypeError as te:
            raise InvalidSpec(te.message)
    else:
        raise InvalidSpec("{} isn't valid in a spec", spec)


class Whatever(Validating):
    '''Just kinda says yes to whatever'''

    def validate(self, _):
        return True


class Nullable(Validating):
    def __init__(self, spec):
        self.arg = _convert_from_builtin(spec)

    def validate(self, value):
        return value is None or self.arg.validate(value)


class Primitive(Validating):
    def __init__(self, type_):
        self.arg = type_

    def validate(self, value):
        return isinstance(value, self.arg)

    def __str__(self):
        return self.arg.__name__

    def __repr__(self):
        return 'Primitive({})'.format(self.arg.__name__)


class UUID(Validating):
    '''Validates a string, ensuring it is a valid UUID'''
    
    regex = re.compile(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)

    def validate(self, value):
        return bool(self.regex.match(value))


class Literally(Validating):
    '''Matches a primitive exactly (rather than ensuring a type'''
    def __init__(self, value):
        self.arg = json.loads(json.dumps(value))

    def validate(self, value):
        return self.arg == value


class AnyOf(Validating):
    '''Matches if any of several subspecs matches.
    '''
    def __init__(self, *subspecs):
        self.subspecs = map(_convert_from_builtin, subspecs)

    def validate(self, value):
        return any(subspec.validate(value) for subspec in self.subspecs)


class Enum(AnyOf):
    '''Similar to AnyOf, but accepts literals as constructor arguments'''

    def __init__(self, *subspecs):
        self.subspecs = map(Literally, subspecs)


class List(Validating):
    '''Validates if every element in the incoming array validates in
    the correct order. The lengths must also match'''
    def __init__(self, *subspecs):
        self.subspecs = map(_convert_from_builtin, subspecs)

    def validate(self, value):
        try:
            if len(value) != len(self.subspecs):
                return False
            return all(spec.validate(val)
                       for spec, val in izip(self.subspecs, value))
        except TypeError:
            return False

    def __repr__(self):
        arglist = ', '.join(repr(spec) for spec in self.subspecs)
        return 'List({})'.format(arglist)


class Object(object):
    '''Validates an object spec. Only checks keys that are specified,
    won't complain about extra keys. If you want to ensure keys aren't
    present, create a model class and validate against that.'''

    def __init__(self, **subspecs):
        self.kwargs = {attr: _convert_from_builtin(spec)
                       for attr, spec in subspecs.iteritems()}


class Table(object):
    '''Holds metadata about a table'''
    
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
        self.secondary_indexes = {}
        self.id_field = None
        for field in self.fields:
            if field.primary_key:
                self.id_field = field
            if field.index:
                self.secondary_index[field.name] = field


class DataBase(object):
    '''Holds information about a RethinkDB database, including a
    collection of tables that belong to it
    '''
    def __init__(self, name, connection=None):
        self.name = name
        self.conn = None
        self.db = r.db(self.name)
        self.tables = {}

    def create(self):
        if self.name not in r.db_list().run(self.conn):
            r.db_create(self.name).run(self.conn)

    def create_all(self):
        self.create()
        existing = self.db.table_list().run(self.conn)
        for tablename in set(self.tables) - set(existing):
            self.db.table_create(tablename)

    def __repr__(self):
        return '''DataBase({.name!r})'''.format(self)


class Session(object):
    '''Associates objects with a connection and database. Maintains
    the identity map of objects
    '''
    def __init__(self, database, connection):
        self.conn = connection
        self.database = database
        self.to_insert = []
        self.to_delete = []
        self.objects = []
        self.id_map = weakref.WeakValueDictionary()

    def add(self, doc):
        self.to_insert.append(doc)

    def delete(self, doc):
        self.to_delete(doc)

    def query(self, cls):
        pass

    def commit(self):
        pass


class AstrologyMeta(type):
    '''Metaclass for model base classes'''

    child_counter = 0

    def __new__(mcls, classname, bases, dict_):
        mcls.child_counter += 1
        if '__init__' in dict_:
            old_init = dict_['__init__']
            def __init__(self, *args, **kwargs):
                if not hasattr(self, 'metadata'):
                    # metadata meant to be inherited
                    self.__table__ = Table(
                        name=self.__tablename__,
                    )
                self.state = {}
                old_init(self, *args, **kwargs)
            dict_['__init__'] = __init__
        return type.__new__(mcls, classname, bases, dict_)

    def __init__(cls, classname, bases, dict_):
        cls._model_registry['classname'] = cls
        for attr, value in dict_.iteritems():
            if isinstance(value, Field) and value.name is None:
                value.name = attr
                metadata.fields[attr] = value


def astrology_base(db_name, baseclasses=(object,)):
    '''
    Call this function to create a Base class for all of your models.
    '''

    @classmethod
    def from_json(cls, json_dict):
        new_obj = cls()
        new_obj.state = json_dict
        return new_obj

    def to_json(self):
        new = copy.deepcopy(self.state)
        for key, value in new.items():
            if self.metadata.fields[key].required and \
               value is None:
                del new[key]
        return new

    def __init__(self, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def __repr__(self):
        classname = self.__class__.__name__
        json_dict = self.to_json()
        return '{class_}.from_json({json})'.format(
            class_=classname,
            json=json_dict)
    
    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=True)
    
    return AstrologyMeta(
        'AstrologyBase',
        baseclasses,
        {'from_json': from_json,
         'to_json': to_json,
         '__init__': __init__,
         '__repr__': __repr__,
         '__str__': __str__,
         '_model_registry': {},
        },
    )