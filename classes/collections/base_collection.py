"""This module is created to organize mongodb Collections"""

__all__ = ("BaseCollection",)

from typing import (TYPE_CHECKING, TypeVar, Type, Any,
                    ClassVar)

from classes.collections.tools import Field
from abc import ABCMeta, ABC
import logging

from bson import ObjectId

if TYPE_CHECKING:
    from classes.bot import Bot

_vt = TypeVar("_vt")
_obj = TypeVar("_obj", bound="BaseCollection")
_log = logging.getLogger(__name__)


class MetaCollection(ABCMeta):
    def __new__(mcs, name, bases, dct):
        cls = super(MetaCollection, mcs).__new__(mcs, name, bases, dct)
        cls.fields = {}
        for base in bases:
            cls.fields.update(getattr(base, "fields", {}))
        cls.keys = set()
        for obj_name, obj in dct.items():
            if isinstance(obj, Field):
                cls.fields[obj_name] = obj
                cls.keys.add(obj_name)
        return cls


class BaseCollection(ABC, metaclass=MetaCollection):
    """mongodb collection

    if you are using __slots__ add a _ to fields and add it into
    __slots__ like below

    pycharm didn't understand what is user-property but reminder each
    field is a property so when you get them in objects of class you
    are going to reach value not the a Field object to get the field
    object use class variable of it instead or use fields dict

    :param bot: :class:`classes.bot.Bot` the bot that you are using

    ClassAttributes
    -----------
    __collection_name__: :class:`str`
        name of collection in db

    """
    __slots__ = ("_bot", "_meta_values")
    __collection_name__: ClassVar[str]
    if TYPE_CHECKING:
        fields: ClassVar[dict[str, Field]]
        keys: ClassVar[set[str]]
        _meta_values: dict[str, Any]
        _bot: "Bot"

    id = Field(name="_id", type_=ObjectId, required=False)

    def __init__(self, bot: "Bot", *, id: ObjectId | None = None,
                 **kwargs):
        self._bot = bot
        self._meta_values = {}
        self._id = id
        for key, value in kwargs.items():
            if key not in self.__class__.keys:
                raise AttributeError(f"{key} not found")
            setattr(self, key, value)

    @classmethod
    async def create_complete_object(
            cls: Type[_obj], bot: "Bot", **kwargs) -> _obj:
        """create a complete object and insert it into database

        other args that not a valid field name will be ignore

        all params same as __init__
        :return: object that created and inserted into database
        """
        self = cls(bot, **kwargs)

        await self.save()
        return self

    @classmethod
    def from_data(cls: Type[_obj], bot: "Bot", data: dict[str, Any]) -> _obj:
        """convert data that got from database to python instance

        :param data: the data that got from database
        :param bot: the bot that you're using

        :return: the instance that made
        """
        self: _obj = cls.__new__(cls)
        self._bot = bot
        self._meta_values = data.copy()
        assert self.is_complete(), f"something wrong"

        return self

    def to_data(self) -> dict[str, Any]:
        """convert collection to mongodb query

        Returns
        --------
        a dict that ready to upload in database
        """
        assert self.is_complete(), f"something wrong about {self}"
        data = self._meta_values.copy()
        del data[self.__class__.id]
        return data

    def is_complete(self, warning: bool = True) -> bool:
        """check all required field are filled

        :return: :class:`bool` ``True`` if all required field are
        filled otherwise ``False``
        """
        values = set(self._meta_values.keys())
        for field in self.__class__.fields.values():
            try:
                field.validate(self)
            except Exception as e:
                if warning:
                    _log.warning(e)
                return False
            values.discard(field.name)
        if values:
            if warning:
                _log.warning(f"extras values: {values}")
            return False
        return True

    def __repr__(self):
        return f"<{self.__class__.__name__} id={str(self.id)}>"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, __o: "BaseCollection") -> bool:
        if self is __o:
            return True
        return (isinstance(__o, self.__class__)
                and self.id is not None
                and self.id == __o.id)

    def __ne__(self, __o: "BaseCollection") -> bool:
        return not self.__eq__(__o)

    async def save(self) -> None:
        """save object in database1
        object must be completed (see :class:`BaseCollection`.is_complete)

        :return: None
        """
        data = self.to_data()
        if self.id is None:
            print(self.__class__.__collection_name__)
            self.id = (await self._bot.db[self.__class__.__collection_name__]
                       .insert_one(data)).inserted_id
            print(self.id)
            return
        await self._bot.db[self.__class__.__collection_name__].update_one(
            filter={self.__class__.id: self.id},
            update={"$set": data}
        )

