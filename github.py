import requests
import json
import os
import time

API_URL = "https://api.github.com"
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


class GitHub:
    def __init__(self, token=None):
        self.token = token

    def process_user_followings(self, user, typesearch, search):
        user_return = ""
        List_return = []
        if typesearch.upper() == '#QUAIS':
            following_list_order = []
            following_list = self.get_following(user)

            for following_user in following_list:
                following_list_order.append(
                    {'user': following_user, 'value': self.process_user_repositories(following_user, search)})

            user_return = self.process_list(following_list_order)

        elif typesearch.upper() == '#QUEM':
            followers_list_order = []
            followers_list = self.get_followers(user)

            for followers_user in followers_list:
                followers_list_order.append(
                    {'user': followers_user, 'value': self.process_user_repositories(followers_user, search)})

            user_return = self.process_list(sorted(followers_list_order, key=lambda x: x['value'], reverse=True)[0])
        else:
            user_return = 'parametro de pesquisa fora do padrao, por favor informe a pesquisa novamente'

        #self.response_comment(user, user_return)
        return user_return

    def process_list(self, lst_users):
        List_return = []
        user_return = ""

        for users in sorted(lst_users, key=lambda x: x['value'], reverse=True):
            if users['value'] > 0:
                List_return.append(users['user'])

        user_return = " - ".join(List_return)
        if user_return == "":
            user_return = "Nao existe nenhum resultado com a pesquisa informada"
        return user_return

    def process_user_repositories(self, user, search):
        repositories = self.get_repositories_by_user(user)
        countrepository = 0
        countreadme = 0
        countmessage = 0
        for repository in repositories:
            repo_language = self.get_repository_languages(user, repository)
            for language in repo_language:
                if search.upper() == language.upper():
                    countrepository += 1

            readme = self.get_repository_readme(user, repository)

            if readme != "Doesn't have README" and search.upper() in readme.upper():
                countreadme += 1

            #list_messages_commits = self.get_message_commits_repository(user, repository)
            #for message in list_messages_commits:
                #if search.upper() in message.upper():
                    #countmessage += 1
                    
        return countrepository + countreadme + countmessage

    def get_following(self, user):
        following_url = "{url}/users/{user}/following".format(url=API_URL, user=user)

        self._check_rate_limit()

        response = requests.get(following_url, headers=self._get_auth_header())
        following_list = [user["login"] for user in json.loads(response.text)]
        return following_list

    def get_followers(self, user):
        followers_url = "{url}/users/{user}/followers".format(url=API_URL, user=user)
        self._check_rate_limit()

        response = requests.get(followers_url, headers=self._get_auth_header())
        followers_list = [user["login"] for user in json.loads(response.text)]
        return followers_list

    def get_repositories_by_user(self, user):
        repos_url = "{url}/users/{user}/repos".format(url=API_URL, user=user)

        self._check_rate_limit()

        response = requests.get(repos_url, headers=self._get_auth_header())
        repos_name = [repo["name"] for repo in json.loads(response.text)]
        return repos_name

    def get_repository_languages(self, user, repo):
        repo_url = "{url}/repos/{user}/{repo}/languages".format(url=API_URL, user=user, repo=repo)

        #self._check_rate_limit()

        response = requests.get(repo_url, headers=self._get_auth_header())
        repository_languages = [key for key in json.loads(response.text)]
        return repository_languages

    def get_repository_readme(self, user, repo):
        repo_url = "{url}/repos/{user}/{repo}/readme".format(url=API_URL, user=user, repo=repo)

        #self._check_rate_limit()

        response = requests.get(repo_url, headers=self._get_auth_header())
        readme = ""
        if response.status_code != 404:
            json_response = json.loads(response.text)
            readme_url = json_response["download_url"]
            readme = self._download_readme(readme_url, user, repo)

        return readme

    def _download_readme(self, readme_url, user, repo):
        self._check_rate_limit()
        response = requests.get(readme_url, headers=self._get_auth_header())
        return response.text

    def _check_rate_limit(self):
        if self._remaining_rate_limit() == 0:
            time.sleep(10)
            self._check_rate_limit()

    def _remaining_rate_limit(self):
        rate_url = "{url}/rate_limit".format(url=API_URL)
        response = requests.get(rate_url, headers=self._get_auth_header())
        json_response = json.loads(response.text)
        return json_response["rate"]["remaining"]

    def _get_auth_header(self):
        if self.token is not None:
            return {'Authorization': 'token {token}'.format(token=self.token)}
        return {}

    def get_last_commit_repo(self):
        owner = os.getenv("OWNER")
        reposity_bot = os.getenv("REPOSITORY_BOT")
        repos_url = "{url}/repos/{owner}/{repository_bot}/commits".format(url=API_URL, owner=owner,
                                                                          repository_bot=reposity_bot)

        self._check_rate_limit()

        response = requests.get(repos_url, headers=self._get_auth_header())
        json_response = json.loads(response.text)
        return json_response[0]["sha"]

    def get_message_commits_repository(self, user, repository):
        repos_url = "{url}/repos/{user}/{repository}/commits".format(url=API_URL, user=user, repository=repository)

        self._check_rate_limit()
        response = requests.get(repos_url, headers=self._get_auth_header())

        return [repo['commit']['message'] for repo in json.loads(response.text)]

    def response_comment(self, user, text):
        owner = os.getenv("OWNER")
        reposity_bot = os.getenv("REPOSITORY_BOT")
        token = os.getenv("TOKEN")
        headers = {
            'accept': "application/vnd.github.v3+json",
            'authorization': "token " + token
        }
        sha_comment = self.get_last_commit_repo()
        url = "{url}/repos/{owner}/{repository_bot}/commits/{sha}/comments".format(url=API_URL, owner=owner,
                                                                                  repository_bot=reposity_bot,
                                                                                  sha=sha_comment)
        payload = "{\n  \"body\": \" @" + user + " \n " + text + " \"}"
        requests.request("POST", url, data=payload, headers=headers)