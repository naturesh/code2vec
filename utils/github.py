from dotenv import load_dotenv;
import os
import requests
import time
load_dotenv()


# constant 

TOKEN = os.environ.get('GITHUB_TOKEN')

def get_headers(token):
    return {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}



# repository name to sha[]
def repository_to_shas(repository, max_page=3, token=TOKEN):

    commits = []

    for i in range(1,max_page+1):
        url = f'https://api.github.com/repos/{repository}/commits'

        resp = requests.get(url, headers=get_headers(token), params={'per_page' : 100,'page' : i})

        if resp.status_code != 200:
            raise ValueError(f"error: {resp.status_code}, {resp.text}")
        
        data = resp.json()

        if not data: break
       
        commits.extend(data)
        
    return list(reversed(list(map(lambda x: x['sha'], commits))))



# sha to detail infomation
def sha_to_detail(repository, sha, token=TOKEN):

    url = f'https://api.github.com/repos/{repository}/commits/{sha}'

    resp = requests.get(url, headers=get_headers(token)).json()
    username = resp['commit']['author']['name']

    details = []

    for f in resp.get('files', []):

        patch = f.get('patch')
        ext, check = verify_filename(f['filename'])

        if patch and check:
            added = patch_to_added(patch)

            for ad in added:
                details.append([username, ad, ext])

    return details



def patch_to_added(patch, min_block_size=5):

    added_blocks = []
    current_block = []

    for line in patch.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            current_block.append(line[1:])
        else:
            if len(current_block) >= min_block_size:
                added_blocks.append('\n'.join(current_block))
            current_block = []

    if len(current_block) >= min_block_size:
        added_blocks.append('\n'.join(current_block))

    return added_blocks




def username_to_repositorys(username, token=TOKEN): # retur
    
    repos = []
    page = 1
    
    while True:
        url = f"https://api.github.com/users/{username}/repos"
        params = {
            'page': page,
            'per_page': 100,
            'type': 'owner',  # 소유한 레포지토리만
            'sort': 'updated',
            'direction': 'desc'
        }
        
        response = requests.get(url, headers=get_headers(token), params=params)
        if response.status_code != 200:
            print(f"error: {response.status_code}, {response.text}")
            break
            
        page_repos = response.json()
        if not page_repos:
            break
        
        own_repos = [repo for repo in page_repos if not repo['fork']]
        repos.extend(own_repos)
        
        page += 1
    
    return [i['full_name'] for i in repos]




def verify_filename(filename):

    code_extensions = {'.py', '.js', '.ts', '.c', '.cpp', '.java', '.go'}

    config_files = {
        # Package managers & dependencies
        'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
        'tsconfig.json', 'jsconfig.json', 'webpack.config.js', 'vite.config.js',
        'pyproject.toml', 'requirements.txt', 'Pipfile', 'Pipfile.lock', 'poetry.lock',
        'Cargo.toml', 'Cargo.lock', 'go.mod', 'go.sum', 'composer.json', 'composer.lock',
        'Gemfile', 'Gemfile.lock', 'pom.xml', 'build.gradle', 'build.gradle.kts',
        
        # Git & version control
        '.gitignore', '.gitattributes', '.gitmodules', '.gitkeep',
        
        # Code quality & formatting
        '.editorconfig', '.eslintrc', '.eslintrc.js', '.eslintrc.json', '.eslintrc.yml',
        '.prettierrc', '.prettierrc.js', '.prettierrc.json', '.prettierignore',
        '.flake8', '.pylintrc', '.black', '.isort.cfg', 'mypy.ini', 'tox.ini',
        '.pre-commit-config.yaml', '.clang-format', '.rustfmt.toml',
        
        # Build & deployment
        'Makefile', 'CMakeLists.txt', 'setup.py', 'setup.cfg', 'Dockerfile',
        'docker-compose.yml', 'docker-compose.yaml', '.dockerignore',
        'Jenkinsfile', '.travis.yml', '.github', 'azure-pipelines.yml',
        'vercel.json', 'netlify.toml', 'next.config.js', 'nuxt.config.js',
        
        # Environment & configuration
        '.env', '.env.example', '.env.local', '.env.development', '.env.production',
        'config.json', 'config.yml', 'config.yaml', 'settings.json',
        '.vscode', '.idea', '*.ini', '*.conf', '*.cfg',
        
        # Documentation & README
        'README.md', 'README.rst', 'README.txt', 'CHANGELOG.md', 'LICENSE',
        'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md', 'SECURITY.md',
        
        # Others
        '.nvmrc', '.node-version', '.python-version', '.ruby-version',
        'babel.config.js', 'rollup.config.js', 'jest.config.js',
        'tailwind.config.js', 'postcss.config.js'
    }


    base = os.path.basename(filename)
    ext = os.path.splitext(base)[1]

    return ext, (ext in code_extensions) and (base not in config_files)


