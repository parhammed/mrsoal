"""fill database from json"""

from os.path import isfile, join
from os import listdir
import asyncio
import json

from motor.motor_asyncio import AsyncIOMotorClient

from classes.collections import Account, Topic, Question, Option
from utils import root, get_or_create


async def main():
    from main import bot

    for file in listdir(path := join(root, "questions")):
        if isfile(file_path := join(path, file)):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_id = (await get_or_create(bot, Account, {
                    Account.discord_id: data["maker"]})).id
                topic_id = (
                    await get_or_create(bot, Topic, {Topic.name: data["topic"]})).id
                for question in data['questions']:
                    question_id = (await Question.create_complete_object(
                        bot,
                        content=question['content'],
                        topic_id=topic_id,
                        maker_id=user_id,
                        complete_answer=question["complete_answer"],
                        is_maker_hidden=question["is_maker_hidden"],
                        is_spoiler=question["is_spoiler"],
                        is_active=True
                    )).id
                    await Option.create_complete_object(
                        bot,
                        content=question["correct_option"],
                        is_correct=True,
                        question_id=question_id
                    )
                    for option in question["incorrect_options"]:
                        await Option.create_complete_object(
                            bot,
                            content=option,
                            is_correct=False,
                            question_id=question_id
                        )


if __name__ == '__main__':
    asyncio.run(main())
