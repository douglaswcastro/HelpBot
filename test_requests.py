import unittest
import os
import requests
from github import GitHub

token = os.getenv("TOKEN")
github = GitHub(token)
API_URL = "https://api.github.com"


class MyTestCase(unittest.TestCase):

	def test_something(self):
		self.assertEqual(True, False)

	def test_get_followings(self):
		user = os.getenv('OWNER')
		followers_url = "{url}/users/{user}/followers".format(url=API_URL, user=user)
		response = requests.get(followers_url, headers=github._get_auth_header())
		self.assertTrue(response.status_code, "200")

	def test_get_following(self):
		user = os.getenv('OWNER')
		following_url = "{url}/users/{user}/following".format(url=API_URL, user=user)
		response = requests.get(following_url, headers=github._get_auth_header())
		self.assertTrue(response.status_code, "200")

	def test_get_readme(self):
		user = os.getenv('OWNER')
		repository = os.getenv('REPOSITORY_BOT')
		repo_url = "{url}/repos/{user}/{repo}/readme".format(url=API_URL, user=user, repo=repository)
		response = requests.get(repo_url, headers=github._get_auth_header())
		self.assertTrue(response.status_code, "200")

	def test_lasted_commit(self):
		owner = os.getenv("OWNER")
		reposity_bot = os.getenv("REPOSITORY_BOT")
		repos_url = "{url}/repos/{owner}/{repository_bot}/commits".format(url=API_URL, owner=owner,repository_bot=reposity_bot)
		response = requests.get(repos_url, headers=github._get_auth_header())
		self.assertTrue(response.status_code, "200")

	def test_last_commit(self):
		owner = os.getenv("OWNER")
		reposity_bot = os.getenv("REPOSITORY_BOT")
		repos_url = "{url}/repos/{owner}/{repository_bot}/commits".format(url=API_URL, owner=owner,
		                                                                  repository_bot=reposity_bot)
		response = requests.get(repos_url, headers=github._get_auth_header())
		self.assertTrue(response.status_code, "200")

if __name__ == '__main__':
	unittest.main()
