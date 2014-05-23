'''
Classes comprising the field specification/validation DSL
'''

from itertools import izip
import re

class Field(object):
    '''Specifies a top level field in an object.
    '''
    def __init__(self, type=str, id=False, name=None):
        self.type_ = type
        self.id_ = id
        self.name = name


class Validating(object):
    '''Base class for validating field types'''
    def validate(self, data):
        raise NotImplemented


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
    if isinstance(Validating, spec):
        return spec
    elif issubclass(Validating, spec):
        return spec()
    elif spec in (str, int, float, bool, object):
        return Primitive(spec)
    elif isinstance(spec, (str, int, float, bool, object)):
        return Literally(spec)
    elif spec is object:
        return Whatever()
    elif isinstance(spec, list):
        return Exactly(*spec)
    elif isinstance(spec, set):
        return Enum(*spec)
    elif isinstance(spec, object):
        return Object(**spec)
    else:
        raise InvalidSpec("{} isn't valid in a spec", spec)


class Whatever(Validating):
    '''Just kinda says yes to whatever'''

    def validate(self, _):
        return True


class Maybe(Validating):
    def __init__(self, spec):
        self.spec = _convert_from_builtin(spec)

    def validate(self, value):
        return value is None or self.spec.validate(value)


class Primitive(Validating):
    def __init__(self, type):
        self.type = type

    def validate(self, value):
        return isinstance(self.type, value)


class UUID(Validating):
    '''Validates a string, ensuring it is a valid UUID'''
    regex = re.compile(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)

    def validate(self, value):
        return bool(self.regex.match(value))


class Literally(Validating):
    '''Matches a primitive exactly (rather than ensuring a type'''
    def __init__(self, literal):
        self.literal = literal

    def validate(self, value):
        return self.literal == value


class Enum(object):
    def __init__(self, *subspecs):
        self.subspecs = map(_convert_from_builtin, subspecs)

    def validate(self, value):
        return any(subspec.validate(value) for subspec in self.subspecs)


AnyOf = Enum


class Exactly(Validating):
    '''Validates if every element in the incoming array validates in
    the correct order. The lengths must also match'''
    def __init__(self, *subspecs):
        self.subspecs = map(_convert_from_builtin, subspecs)

    def validate(self, value):
        if len(value) != len(self.subspecs):
            return False
        return all(spec.validate(val)
                   for spec, val in izip(self.subspecs, value))


class Object(object):
    '''Validates an object spec. Only checks keys that are specified,
    won't complain about extra keys. If you want to ensure keys aren't
    present, create a model class and validate against that.'''

    def __init__(self, **subspecs):
        self.kwargs = {attr: _convert_from_builtin(spec)
                       for attr, spec in subspecs.iteritems()}
