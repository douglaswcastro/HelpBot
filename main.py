from flask import Flask, request
from github import GitHub
import os
import json

app = Flask(__name__)

@app.route('/', methods=['POST'])
def foo():
	token = os.getenv("TOKEN")
	data = json.loads(request.data)
	user = data['comment']['user']['login']
	comentary = data['comment']['body']
	bot = comentary[1:8]
	typesearch = comentary[9:15].strip()
	search = comentary[16:].lstrip()
	text_return = ""
	if bot.upper() != "HELPBOT":
		return "O Robô não foi citado no comentário, por favor cite o robô"
	github = GitHub(token)
	text_return = github.process_user_followings(user, typesearch, search)
	return text_return


if __name__ == '__main__':
	app.run()
