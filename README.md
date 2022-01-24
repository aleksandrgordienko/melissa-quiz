# melissa-quiz

**OS environment parameters:**

- MELISSA_QUIZ_BOT_KEY - Telegram Bot API key 
- MELISSA_QUIZ_TG_CHANNEL - Telegram Channel
- MELISSA_QUIZ_TG_ADMINS - UserIDs of Bot administrators (for using /setparameter)
- MELISSA_QUIZ_SQLALCHEMY_DB_CONN - SQLAlchemy connection string
- MELISSA_QUIZ_DEFAULT_LANG - Default language for new chat

**Using Docker image:**

`docker run --env MELISSA_QUIZ_BOT_KEY="" --env MELISSA_QUIZ_TG_CHANNEL="" --env MELISSA_QUIZ_SQLALCHEMY_DB_CONN="" datadiving/melissa-quiz`

**Links to repositories:**

[GitHub repository](https://github.com/aleksandrgordienko/melissa-quiz)

[DockerHub repository](https://hub.docker.com/r/datadiving/melissa-quiz)