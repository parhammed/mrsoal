from bson import ObjectId

from .base_collection import BaseCollection
from .tools import Field
from utils import Point

topic_name = str


class Answer(BaseCollection):
    """python class for `Answers` collection

    Attributes
    ----------
    :attr user_id: id of account that answered the question
    :attr topic_id: id of topic of question of answer
    :attr option_id: id of option that answered
    """
    __collection_name__ = "answers"

    user_id = Field(name="user", type_=ObjectId, required=True)
    question_id = Field(name="question", type_=ObjectId, required=True)
    option_id = Field(name="option", type_=ObjectId, required=False)

    @classmethod
    async def get_point(cls, db, user: ObjectId, topic: ObjectId) -> Point:
        from .option import Option
        from .question import Question

        items = db[cls.__collection_name__].aggregate([
            {"$match": {cls.user_id: user}},
            {"$lookup": {
                "from": Question.__collection_name__,
                "localField": cls.question_id,
                "foreignField": Question.id,
                "as": "question",
                "pipeline": [
                    {"$project": {Question.topic_id: True}}
                ]
            }},
            {"$unwind": {"path": "$question"}},
            {"$match": {Question.topic_id: topic}},
            {"$lookup": {
                "from": Option.__collection_name__,
                "localField": cls.option_id,
                "foreignField": Option.id,
                "as": "option",
                "pipeline": [
                    {"$project": {Option.is_correct: True}}
                ]}},
            {"$unwind": {"path": "$option",
                         "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": {"$ifNull": [f"$option.{Option.is_correct}",
                                    "None"]},
                "count": {"$count": {}}}}
        ])
        point = Point()
        async for item in items:
            # if the answer is not idk it's incorrect
            point.count += item["count"]
            if not item["_id"]:
                point.incorrect = item["count"]

            elif item["_id"] != "None":
                point.correct = item["count"]
        return point

    @classmethod
    async def get_all_points(cls, db, user: ObjectId) \
            -> dict[topic_name, Point]:
        from .option import Option
        from .topic import Topic
        from .question import Question

        points: dict[topic_name, Point] = {}
        items = db[cls.__collection_name__].aggregate([
            {"$match": {"user": user}},
            {"$lookup": {
                "from": Option.__collection_name__,
                "localField": cls.option_id,
                "foreignField": Option.id,
                "as": "option",
                "pipeline": [
                    {"$project": {"is_correct": True}}
                ]}},
            {"$unwind": {"path": "$option",
                         "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": Question.__collection_name__,
                "localField": cls.question_id,
                "foreignField": Question.id,
                "as": "question",
                "pipeline": [
                    {"$project": {Question.topic_id: True}}
                ]
            }},
            {"$unwind": {"path": "$question"}},
            {"$lookup": {"from": Topic.__collection_name__,
                         "localField": f"question.{Question.topic_id}",
                         "foreignField": Topic.id,
                         "as": "topic"}},
            {"$unwind": {"path": "$topic", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": {
                    "topic": {"$ifNull": [f"$topic.{Topic.name}", "general"]},
                    "correct": f"$option.{Option.is_correct}"},
                "count": {"$count": {}}}}
        ])

        async for item in items:
            correct = item["_id"].get("correct", None)
            point = points.setdefault(item["_id"]["topic"], Point())
            point.count += item["count"]
            if correct:
                point.correct = item["count"]
            elif correct is not None:
                # if the answer is not idk it's incorrect
                point.incorrect = item["count"]

        return points
