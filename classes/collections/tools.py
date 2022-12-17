from typing import (Generic, Type, Callable, TYPE_CHECKING, TypeVar, overload)
import logging

__all__ = ("MISSING", "Field")

_vt = TypeVar("_vt")
MISSING = object()
_log = logging.getLogger(__file__)

if TYPE_CHECKING:
    from .base_collection import BaseCollection


class Field(Generic[_vt]):
    """A class that use for manage fields in a collection

    :param name: :class:`str`
        name of field in mongodb

    :param required: :class:`bool`
        if True the value of field can be None
        else the value must be :attr:`_type_`

    :param type_: :class:`Object`
        the type of value it can't be Union or Optional

    :param validators:
        a list of validator that valid the value.
        each validator get a value and return nothing (means valid)
        or raise a error (means not valid)
    """
    __slots__ = (
        "name", "_required", "_type_", "_validators", "_value", "_default")
    if TYPE_CHECKING:
        name: str
        required: bool
        _type_: Type[_vt]
        _value: _vt | None
        _validators: list[Callable[[_vt], None]]
        _collection: "BaseCollection"

    def __init__(
            self,
            name: str,
            type_: Type[_vt] = object,
            required: bool = True,
            default=None,
            validators: list[Callable[[_vt], None]] | None = None):

        self.name = name
        self._default = default
        self._required = default is None and required
        self._type_ = type_
        self._validators = validators or []

    def __repr__(self):
        return f"<Field name={self.name}>"

    def __str__(self):
        return self.name

    @overload
    def __get__(self, instance: None, owner: Type["BaseCollection"]) -> str:
        pass

    def __get__(self, instance: "BaseCollection",
                owner: Type["BaseCollection"]) -> _vt:
        if instance is None:
            return self.name
            # require to access a private attribute
        return instance._meta_values.setdefault(self.name, self._default)  # type: ignore

    def _validate(self, value) -> None:
        if not self._required and value is None:
            return

        assert isinstance(value, self._type_), \
            f"type not match for {self.name} (needed: {self._type_}, gotten: {repr(value)})"
        for validator in self._validators:
            validator(value)

    def __set__(self, instance: "BaseCollection", value):
        self._validate(value)
        # require to access a private attribute
        instance._meta_values[self.name] = value  # type: ignore

    def validate(self, instance: "BaseCollection"):
        """validate the instance (just this field

        :raise: when validation failed
        """
        # require to access a private attribute
        self._validate(
            instance._meta_values.setdefault(self.name, self._default))  # type: ignore
