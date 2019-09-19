from github import GitHub
import os
from load_env import load_dotenv

user = "douglaswcastro"

token = os.getenv("TOKEN")
typesearch = "#Quais"
search = "Correios"
github = GitHub(token)
github.process_user_followings(user, typesearch, search)
