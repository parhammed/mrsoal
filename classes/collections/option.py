from bson import ObjectId

from .base_collection import BaseCollection
from .tools import Field


class Option(BaseCollection):
    __collection_name__ = "options"

    content = Field(name="content", type_=str, required=True)
    is_correct = Field(name="is_correct", type_=bool, required=True)
    question_id = Field(name="question", type_=ObjectId, required=True)
