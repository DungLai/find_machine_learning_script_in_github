import requests
import urllib.request

# get the list of the python modules in a repo
def get_python_file_path(github_user, github_repo):
	python_file_paths = []
	get_file_path_request = "https://api.github.com/repos/{}/{}/git/trees/master?recursive=1".format(github_user, github_repo)
	r = requests.get(get_file_path_request)
	res = r.json()
	for file in res["tree"]:
		# only contain .py file but not .pyc file
		if ".py" in file["path"] and ".pyc" not in file["path"]:
			python_file_paths.append(file["path"])
	return python_file_paths

# get the code of a file based on its github path, username and repo name
def get_content(github_file_path, github_user, github_repo):
	get_content_request ="https://raw.githubusercontent.com/{}/{}/master/{}".format(github_user, github_repo, github_file_path)
	response = urllib.request.urlopen(get_content_request)
	# Do what you need to with the speech
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

def main():
	user = "pierluigiferrari"
	repo = "ssd_keras"
	py_files = get_python_file_path(user, repo)
	print("List of python file in {}/{}".format(user,repo))
	print(py_files)

	python_scripts_with_ML = []
	python_scripts_without_ML = []

	for file in py_files:
		content = get_content(file, user, repo)
		if contain_ML_library(content):
			# print(file)
			# print(content)
			python_scripts_with_ML.append(file)
		else:
			python_scripts_without_ML.append(file)

	print(python_scripts_with_ML)
	print('---')
	print(python_scripts_without_ML)

# for debuging purposes
def test_function():
	user = "pierluigiferrari"
	repo = "ssd_keras"
	file = "data_generator/data_augmentation_chain_satellite.py"
	content = get_content(file, user, repo)
	print(contain_ML_library(content))

main()
# test_function()