from flask import Flask, request
from github import GitHub
import os
import json
from rq import Queue
from worker import conn

app = Flask(__name__)


@app.route('/', methods=['POST'])
def foo():
    q = Queue(connection=conn)
    print('inicio processamento')
    token = os.getenv("TOKEN")
    data = json.loads(request.data)
    user = data['comment']['user']['login']
    comentary = data['comment']['body']
    bot = comentary[1:8]
    typesearch = comentary[9:15].strip()
    search = comentary[14:].lstrip()
    result = ""
    print(bot)
    if bot.upper() == "HELPBOT":
    # return "O Robô não foi citado no comentário, por favor cite o robô"
        github = GitHub(token)
        result = q.enqueue(github.process_user_followings, user, typesearch, search)
    # text_return =

    # github.response_comment(user, text_return)

    return result


if __name__ == '__main__':
    app.run()
