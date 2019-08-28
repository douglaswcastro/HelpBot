from github import GitHub

user = "douglaswcastro"
repo = "DAD-Parking---Back"

token = '752ad7fc02a60df65fb8f31a30ba2bdab58880f7'
typesearch = "#Quem"
search = "C#"
github = GitHub(token)
github.process_user_followings(user, typesearch, search)
