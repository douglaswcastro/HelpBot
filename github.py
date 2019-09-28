import requests
import json
import os
import time

API_URL = "https://api.github.com"
owner = os.getenv("OWNER")
reposity_bot = os.getenv("REPOSITORY_BOT")
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


class GitHub:
    def __init__(self, token=None):
        self.token = token

    def process_user_followings(self, user, typesearch, search):
        following_list = self.get_following(user)
        user_return = ""
        following_list_order = []
        for following_user in following_list[0:2]:
            # t = threading.Thread(target=following_list_order.append({'user': following_user, 'value': self.process_user_repositories(following_user, search)}))
            # t.start()
            following_list_order.append(
                {'user': following_user, 'value': self.process_user_repositories(following_user, search)})
        # while threading.active_count() != 1:
        # pass

        if typesearch.upper() == '#QUEM':
            user_return = sorted(following_list_order, key=lambda x: x['value'], reverse=True)[0]['user']

        elif typesearch.upper() == '#QUAIS':
            for users in sorted(following_list_order, key=lambda x: x['value'], reverse=True):
                user_return.append(users['user']+"\n  \"")

        else:
            user_return = 'parametro de pesquisa fora do padrao, por favor informe a pesquisa novamente'

        self.response_comment(user, user_return)
        return user_return

    def process_user_repositories(self, user, search):
        repositories = self.get_repositories_by_user(user)
        countrepository = 0
        countreadme = 0
        for repository in repositories:
            repo_language = self.get_repository_languages(user, repository)
            for language in repo_language:
                if search.upper() == language.upper():
                    countrepository += 1

            readme = self.get_repository_readme(user, repository)

            if readme != "Doesn't have README" and search.upper() in readme.upper():
                countreadme += 1
        return countrepository + countreadme

    def get_following(self, user):
        following_url = "{url}/users/{user}/following".format(url=API_URL, user=user)

        self._check_rate_limit()

        response = requests.get(following_url, headers=self._get_auth_header())
        following_list = [user["login"] for user in json.loads(response.text)]
        return following_list

    def get_repositories_by_user(self, user):
        repos_url = "{url}/users/{user}/repos".format(url=API_URL, user=user)

        self._check_rate_limit()

        response = requests.get(repos_url, headers=self._get_auth_header())
        repos_name = [repo["name"] for repo in json.loads(response.text)]
        return repos_name

    def get_repository_languages(self, user, repo):
        repo_url = "{url}/repos/{user}/{repo}/languages".format(url=API_URL, user=user, repo=repo)

        self._check_rate_limit()

        response = requests.get(repo_url, headers=self._get_auth_header())
        repository_languages = [key for key in json.loads(response.text)]
        return repository_languages

    def get_repository_readme(self, user, repo):
        repo_url = "{url}/repos/{user}/{repo}/readme".format(url=API_URL, user=user, repo=repo)

        self._check_rate_limit()

        response = requests.get(repo_url, headers=self._get_auth_header())
        readme = ""
        if response.status_code != 404:
            json_response = json.loads(response.text)
            readme_url = json_response["download_url"]
            readme = self._download_readme(readme_url, user, repo)
        else:
            readme = "Doesn't have README"

        return readme

    def _download_readme(self, readme_url, user, repo):
        self._check_rate_limit()
        response = requests.get(readme_url, headers=self._get_auth_header())
        return response.text

    def _check_rate_limit(self):
        if self._remaining_rate_limit() == 0:
            print("Wait a minute")
            time.sleep(5)
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
        repos_url = "{url}/repos/{owner}/{repository_bot}/commits".format(url=API_URL, owner=owner,
                                                                          repository_bot=reposity_bot)

        self._check_rate_limit()

        response = requests.get(repos_url, headers=self._get_auth_header())
        json_response = json.loads(response.text)
        return json_response[0]["sha"]

    def response_comment(self, user, text):
        token = os.getenv("TOKEN")
        headers = {
            'accept': "application/vnd.github.v3+json",
            'authorization': "token " + token
        }
        sha_comment = self.get_last_commit_repo()
        url = "{url}/repos/{owner}/{repository_bot}/commits/{sha}/comments".format(url=API_URL, owner=owner,
                                                                                  repository_bot=reposity_bot,
                                                                                  sha=sha_comment)
        payload = "{\n  \"body\": \" @" + user + " \\n " + text + " \"}"
        requests.request("POST", url, data=payload, headers=headers)