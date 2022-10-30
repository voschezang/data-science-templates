from typing import _GenericAlias

from object_parser.errors import ErrorMessages, SpecError
from object_parser.errors import BuildError, BuildErrors, ErrorMessages, SpecError
from util import has_annotations, has_method, infer_inner_cls, is_enum, is_valid_method_name


def init_recursively(cls, data={}):
    fields: dict = init_values(cls, data)

    if hasattr(cls, '__dataclass_fields__'):
        instance = cls(**fields)

    else:
        if issubclass(cls, Spec):
            instance = super(Spec, cls).__new__(cls)
        else:
            instance = cls()

        if has_annotations(cls):
            # assume instance of Spec
            for k in cls.__annotations__:
                if k not in fields:
                    raise SpecError()
                setattr(instance, k, fields[k])

    if has_method(cls, '__post_init__'):
        instance.__post_init__()

    return instance


def init_values(cls, data: dict) -> dict:
    """Instantiate all values in `data`, based on the type annotations in `cls`.
    """
    data = parse_field_keys(cls, data)

    result = {}
    if not data:
        return result
    elif not has_annotations(cls):
        raise SpecError(ErrorMessages.no_type_annotations())

    for key in cls.__annotations__:
        result[key] = _init_field(cls, key, data)

    return result


def _init_field(cls, key, data):
    if key in data:
        return init(cls.__annotations__[key], data[key])
    elif hasattr(cls, key):
        return getattr(cls, key)

    raise SpecError(ErrorMessages.missing_mandatory_key(cls, key))


def init(cls, args):
    if getattr(cls, '_name', '') == 'Dict':
        inner_cls = infer_inner_cls(cls)
        return {k: inner_cls(v) for k, v in args.items()}
    elif isinstance(cls, _GenericAlias):
        # assume typing.List
        assert len(cls.__args__) == 1

        list_item = cls.__args__[0]
        return [list_item(v) for v in args]

    if has_method(cls, 'parse_value'):
        args = cls.parse_value(args)

    if is_enum(cls):
        try:
            return cls[args]
        except KeyError:
            raise SpecError(f'Invalid value for {cls}(Enum)')

    try:
        obj = cls(args)

    except ValueError as e:
        raise SpecError(e)

    if has_method(cls, '__post_init__'):
        obj.__post_init__()

    return obj


def parse_field_keys(cls, data) -> dict:
    # note that dict comprehensions ignore duplicates
    return {parse_field_key(cls, k): v for k, v in data.items()}


def parse_field_key(cls, key: str) -> str:
    if getattr(cls, '_name', '') in ['Dict', 'List']:
        if cls._name == 'Dict':
            inner_cls = cls.__args__[1]
        elif cls._name == 'List':
            inner_cls = cls.__args__[0]

        return f'{{{inner_cls.__name__}}}'

    if has_method(cls, 'verify_key_format'):
        cls.verify_key_format(key)
    else:
        verify_key_format(cls, key)

    if has_method(cls, 'parse_key'):
        key = cls.parse_key(key)

    if has_annotations(cls) and key in cls.__annotations__:
        return key

    return find_synonym(cls, key)


def find_synonym(cls, key: str):
    if hasattr(cls, '_key_synonyms'):
        for original_key, synonyms in cls._key_synonyms.items():
            if key in synonyms:
                return original_key

    raise BuildError(ErrorMessages.unexpected_key(cls, key))


def verify_key_format(cls, key: str):
    # TODO rm duplicate func
    if not is_valid_method_name(key):
        raise SpecError(ErrorMessages.invalid_key_format(cls, key))


class Spec():
    """Example class

    Initialize with either:
    ```py
    Spec( {'a': 1, 'b': 2} )
    Spec(a=1, b=2)
    ```

    See object_parser_example.py for a larger usecase as an example.
    """

    _key_synonyms = {}

    def __init__(self, data=None, **kwds):
        """"Init
        This stub is included to show which args are used.
        """
        pass

    def verify(self):
        """Verify this object.
        Note that this method can do verifications that are based on multiple fields.
        Raise `SpecError` in case of a failed verification.
        """
        pass

    @staticmethod
    def parse_value(value):
        """Transform the raw input value of this object, before calling `.__init__()`
        This is mainly useful for Enums, but it is applied to all datatypes for consistency.

        E.g. use this to change the casing of an input string.
        """
        return value

    @staticmethod
    def parse_key(key):
        """Transform a raw input key (attribute) of this object
        This can be used to for example convert an input to lowercase.
        Note that this method is applied to all keys (attributes).
        """
        return key

    @classmethod
    def verify_key_format(cls, key: str):
        return verify_key_format(cls, key)

    def items(self):
        return {k: getattr(self, k) for k in self.__annotations__}

    ############################################################################
    # Internals
    ############################################################################

    def __new__(cls, data={}, **kwds):
        """ Generic constructor that validates the keys before initializing the object.
        """
        if data:
            # merge all arguments
            kwds.update(data)
        return init_recursively(cls, kwds)

    def __repr__(self) -> str:
        cls = str(self.__class__)[1:-1]
        repr = f'<{cls} object at {hex(id(self))}>'
        data = vars(self)
        return f'{repr} {data}'
