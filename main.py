from github import GitHub
from flask import Flask, request
import json
import os
from load_env import load_dotenv


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def foo():
	data = json.loads(request.data)
	print: "New commit by: {}".format[data['commits'][0]['author']['name']]
	return "OK"


#user = "douglaswcastro"

#token = os.getenv("TOKEN")
#typesearch = "#Quais"
#search = "Correios"


#github = GitHub(token)
#github.process_user_followings(user, typesearch, search)
