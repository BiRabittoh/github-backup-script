from github import Github, Auth
from git import Repo
from git.exc import GitCommandError
from pathlib import Path
from os.path import join
import logging, json
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

with open("config.json", "r") as in_file:
    config = json.loads("".join(in_file.readlines()))
    
def get_config(key, default=None):
    try:
        return config[key]
    except KeyError:
        if default is None:
            logger.error("Missing config key: {}.".format(key))
            exit(1)
        return default
github_user = get_config("github_username")
github_token = get_config("github_auth_token")
repo_dir = get_config("repo_dir")
blacklist = set(get_config("blacklist", []))

g = Github(auth=Auth.Token(github_token))
repos = g.get_user().get_repos()

def handle_repo(r):
    repo_name = r.name
    repo_path = Path(join(repo_dir, repo_name + ".git"))
    if repo_path.exists():
        return
        logger.info("Updating " + repo_name)
        repo = Repo(repo_path)
        repo.remote().fetch("+refs/heads/*:refs/heads/*")
        return repo
    url = f"https://{github_user}:{github_token}@github.com/{r.owner.login}/{repo_name}.git"
    logger.info("Cloning " + repo_name)
    return Repo.clone_from(url, repo_path, bare=True)

results = [ handle_repo(repo) for repo in repos if repo.name not in blacklist ]
logger.info(results)
