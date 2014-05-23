'''This module contains all 'magic' usage in ReQLAstrology. Each class
or method uses magic in some way. The idea is that this module be as
small as possible, and other modules make controlled use of magic by
using this module to gain access to special abilities.
'''

from .meta_facilities import translate_class_attr, class_init

class AstrologyMeta(type):
    '''Metaclass for model base classes'''
    def __init__(cls, classname, bases, dict_):
        if '_model_registry' not in cls.__dict__:
            cls._model_registry = {}
            class_init(cls, classname, cls.__dict__)
        super(AstrologyMeta, cls).__init__(classname, bases, dict_)

    def __setattr__(cls, key, value):
        translate_class_attr(cls, key, value)

def astrology_base(name='Base', baseclasses=(object,)):
    '''
    Call this function to create a Base class for all of your models.
    '''
    return AstrologyMeta(name, baseclasses, {})