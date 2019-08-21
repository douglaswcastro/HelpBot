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

    def process_user_followings(self, user):
        following_list = self.get_following(user)

        for following_user in following_list:
            t = threading.Thread(target=self.process_user_repositories, args=(following_user,))
            t.start()

        while threading.active_count() != 1:
            pass

    def process_user_repositories(self, user):
        repositories = self.get_repositories_by_user(user)
        print("Getting {user} repositories".format(user=user))

        for repository in repositories:
            repo_language = self.get_repository_languages(user, repository)
            print("{user}/{repo} {lang}".format(user=user, repo=repository, lang=repo_language))
            self.get_repository_readme(user, repository)

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

        if response.status_code != 404:
            json_response = json.loads(response.text)
            readme_url = json_response["download_url"]
            self._download_readme(readme_url, user, repo)
        else:
            print("Doesn't have README")

    def _download_readme(self, readme_url, user, repo):
        readme_folder = os.path.abspath(os.path.join(SCRIPT_PATH, os.pardir)) + "/HelpBoot/readmes"

        self._check_rate_limit()

        response = requests.get(readme_url, headers=self._get_auth_header())
        readme_filename = "{folder}/README+{user}+{repo}.md".format(folder=readme_folder, user=user, repo=repo)
        with open(readme_filename, 'wb') as readme_file:
            readme_file.write(response.content)

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