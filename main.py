import os
import json
from flask import Flask, request
from github import GitHub

app = Flask(__name__)


@app.route('/', methods=['POST'])
def foo():
	data = json.loads(request.data)
	print: "New commit by: {}".format(data['commits'][0]['author']['name'])
	return "OK"


if __name__ == '__main__':
	app.run()


#user = "douglaswcastro"

token = os.getenv("TOKEN")
#typesearch = "#Quais"
#search = "Correios"
#github = GitHub(token)
#github.process_user_followings(user, typesearch, search)
