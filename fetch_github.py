import requests
import urllib.request
import subprocess
import json
from bs4 import BeautifulSoup
import re

# get the list of the python modules in a repo
def get_python_file_path(github_user, github_repo):
	python_file_paths = []
	get_file_path_request = "https://api.github.com/repos/{}/{}/git/trees/master?recursive=1".format(github_user, github_repo)
	r = requests.get(get_file_path_request)
	res = r.json()
	print(res)
	for file in res["tree"]:
		# only contain .py file but not .pyc file
		if ".py" in file["path"] and ".pyc" not in file["path"]:
			python_file_paths.append(file["path"])
	return python_file_paths

# get the code of a file based on its github path, username and repo name
def get_content(github_file_path, github_user, github_repo):
	get_content_request ="https://raw.githubusercontent.com/{}/{}/master/{}".format(github_user, github_repo, github_file_path)
	response = urllib.request.urlopen(get_content_request)
	content = response.read()
	content = content.decode("utf-8")
	return content

# Return true if a script uses any ML library
def contain_ML_library(content):
	ml_import_libs = ["keras", "tensorflow", "numpy", "pandas"] 
	lines_of_code = content.split("\n")
	for line in lines_of_code:
		# skip commented line. This is when there is an import of ML library but it was commented out
		if line != "" and line[0] == "#":
			continue
		for ml_lib in ml_import_libs:
			if line[0:7] == "import " and ml_lib in line:
				return True
	return False

# all commits ID (sha) of a file are included in the return json
def get_commits(github_file_path, github_user, github_repo):
	commits_sha = []
	get_content_request = "http://api.github.com/repos/{}/{}/commits?path={}".format(github_user,github_repo, github_file_path)
	response = urllib.request.urlopen(get_content_request)
	content = response.read()
	content = content.decode("utf-8")
	commits_json = json.loads(content)
	for i in range(len(commits_json)):
		commits_sha.append(commits_json[i]["sha"])
	return commits_sha

# not working atm
def get_content_at_commit(github_user, github_repo, commit_id):
	get_content_request = "https://api.github.com/repos/{}/{}/git/commits/{}".format(github_user,github_repo, commit_id)
	response = urllib.request.urlopen(get_content_request)
	content = response.read()
	content = content.decode("utf-8")
	return content

# get the PR number associated to a commit ID
def get_PR_of_commit(github_user, github_repo, commit_sha):
	url = "https://api.github.com/repos/{}/{}/commits/{}/pulls".format(github_user,github_repo, commit_sha)
	hdr = {'Accept':'application/vnd.github.groot-preview+json'}
	req = urllib.request.Request(url, headers = hdr)
	response = urllib.request.urlopen(req)
	content = response.read()
	content = content.decode("utf-8")
	pull_json = json.loads(content)
	if len(pull_json) == 0:
		print("No PR is associated with the commit " + commit_sha)
		return -1
	pr_number = pull_json[0]["number"] # Assumption: each commit has 1 PR
	return pr_number

# Get the issue numbers associated with a PR number
def find_issue_of_PR(github_user, github_repo,pr_number):
	# https://stackoverflow.com/questions/60717142/getting-linked-issues-and-projects-associated-with-a-pull-request-form-github-ap
	r = requests.get("https://github.com/{}/{}/pull/{}".format(github_user, github_repo, pr_number))
	soup = BeautifulSoup(r.text, 'html.parser')
	issueForm = soup.find("form", { "aria-label": re.compile('Link issues')})
	issue_list = [ i["href"] for i in issueForm.find_all("a")] 
	issue_number = []
	for link in issue_list:
		issue_number.append(link.split("/")[-1])
	print(issue_number)
	return issue_number

# for debuging purposes
def test_function():

	user = "a2i2"
	repo = "surround"
	file = "surround_cli/surround_cli/cli.py"	
	sha_commit = "81fec18d001f40b83da43b60fe0df6ae04eb3a07"
	content = find_issue_of_PR(user, repo, 273)
	print(content)
	# commits_sha = get_commits(user,repo, file)
	# print(commits_sha)
	# for commit_sha in commits_sha:
	# 	pr_of_commit = get_PR_of_commit(user, repo, commit_sha)
	# 	print(pr_of_commit)
	# res = find_issue_of_PR(user,repo,273)
	# res = get_content("surround/setup.py", user, repo)
	# print(res)

def main():
	user = "a2i2"
	repo = "surround"
	data = []
	py_files = get_python_file_path(user, repo)
	# print("List of python file in {}/{}".format(user,repo))
	# print(py_files)

	# python_scripts_with_ML = []
	# python_scripts_without_ML = []

	# i = 0
	# for file in py_files:
	# 	print(i)
	# 	i+=1
	# 	content = get_content(file, user, repo)
	# 	if contain_ML_library(content):
	# 		python_scripts_with_ML.append(file)
	# 	else:
	# 		python_scripts_without_ML.append(file)

	# print(python_scripts_with_ML)
	# print('---')
	i = 0
	for file in py_files:
		if i == 5:
			break
		i = i+1
		file_dict = {}
		file_dict["file"] = file
		file_dict["commits"] = []
		commits = get_commits(file, user, repo)
		for sha in commits:
			commit_dict = {}
			commit_dict["sha"] = sha
			# commit_dict["pr"] = get_PR_of_commit(user,repo,sha)
			file_dict["commits"].append(commit_dict)
		data.append(file_dict)
		# data["file"][-1]["commits"] = []
		# commits = get_commits(file, user, repo)
		# for commit in commits:
		# 	get_PR_of_commit(user,repo,commit)
	print(data)

main()
# test_function()

# curl -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/pierluigiferrari/ssd_keras/git/commits/4ddee4b9c54f0cf0247f20dc7762baba7d50c005

# file commit PR issue

# get commit need to return list of sha (still doing this)
