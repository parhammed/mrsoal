# mrsoal

***warning***: development of this bot is stopped <br>
**Run at your own risk**

## requirements

python >= 3.10.5 <br>
setup mongodb server<br>
packages in [requirements.txt](requirements.txt)

```shell
pip install -r requirements.txt
```

## preparation

### confining [settings.json](settings.json):

| name                   | type              | description                                                                                                      |
|------------------------|-------------------|------------------------------------------------------------------------------------------------------------------|
| token                  | string            | the token of your bot (not your application) [here](https://discord.com/developers/applications)                 |
| default_prefix         | string            | default prefix of bot                                                                                            |
| debug                  | boolean           | if bot is in development or no                                                                                   |
| engine_url             | string            | url of mongo db server [here](https://www.mongodb.com/resources/products/fundamentals/mongodb-connection-string) |
| test_guilds            | array of integers | IDs of test guilds that enabled when debug is true                                                               |
| main_guild             | integer           | ID of the management discord server                                                                              |
| question_query_channel | integer           | ID of the channel from main_guild that new quesation goes to                                                     |
| admin                  | integer           | ID of the role from main_guild that manage the bot                                                               |

### upload questions to database

```shell
python migrate.py
```

## how to run

```shell
python main.py
```
