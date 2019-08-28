import requests
import json
import os
import time
import threading

API_URL = "https://api.github.com"
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

class GitHub:

    def __init__(self, token=None):
        self.token = token

    def process_user_followings(self, user, typesearch, search):
        following_list = self.get_following(user)

        following_list_order = []
        for following_user in following_list:
            # t = threading.Thread(target=self.process_user_repositories, args=(following_user,))
            # t.start()
            self.process_user_repositories(following_user, search)
            following_list_order.append(tuple(following_user, self.process_user_repositories(following_user, search)))
        # while threading.active_count() != 1:
        # pass

        if typesearch == '#Quem':
            print(search)
            print(typesearch)
            print(following_list_order.sort(key=lambda x: x[1])[0])

        elif typesearch == '#Quais':
            print(search)
            print(typesearch)
            for users in following_list_order.sort(key=lambda x: x[1]):
                print(users)

        else:
            print('parametro de pesquisa fora do padrão, por favor informe a pesquisa novamente')

    def process_user_repositories(self, user, search):
        repositories = self.get_repositories_by_user(user)
        print("Getting {user} repositories".format(user=user))
        countrepository = 0
        countreadme = 0
        for repository in repositories:
            repo_language = self.get_repository_languages(user, repository)
            for language in repo_language:
                if search.upper() == language.upper():
                    countrepository += 1

            print("{user}/{repo} {lang}".format(user=user, repo=repository, lang=repo_language))
            readme = self.get_repository_readme(user, repository)

            if readme.str().upper().contains(search.upper):
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
        print(readme)
        return readme

    def _download_readme(self, readme_url, user, repo):
        readme_folder = os.path.abspath(os.path.join(SCRIPT_PATH, os.pardir)) + "/HelpBoot/readmes"

        self._check_rate_limit()

        response = requests.get(readme_url, headers=self._get_auth_header())
        print(response.content)
        #readme_filename = "{folder}/README+{user}+{repo}.md".format(folder=readme_folder, user=user, repo=repo)
        #with open(readme_filename, 'wb') as readme_file:
            #readme_file.write(response.content)
        return response.content

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