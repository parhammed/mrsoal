from .base_collection import BaseCollection
from .tools import Field

topic_name = str


class Account(BaseCollection):
    """python class for `accounts` collection

    Attributes
    ----------
    :attr discord_id: id of person in discord
    """
    __collection_name__ = "accounts"

    discord_id = Field(name="discord_id", type_=int, required=True)

    async def get_all_question_counts(self) -> dict[topic_name, int]:
        """get question count group by topic name"""
        from .question import Question
        from .topic import Topic

        items = self._bot.db[Question.__collection_name__].aggregate([
            {"$match": {
                Question.maker_id: self.id,
                Question.is_active: True,
                Question.is_maker_hidden: False}},
            {"$project": {Question.topic_id: True}},
            {"$lookup": {
                "from": Topic.__collection_name__,
                "localField": Question.topic_id,
                "foreignField": Topic.id,
                "as": "topic"}},
            {"$unwind": {"path": "$topic", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": {"$ifNull": [f"$topic.{Topic.name}", "general"]},
                "count": {"$count": {}}}}
        ])
        return {item["_id"]: item["count"] async for item in items}
