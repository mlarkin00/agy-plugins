import re
import hashlib
import subprocess
import os

def normalize_git_url(url):
    if not url:
        return ""
    # Strip username part if present (e.g. git@ or ssh://git@)
    url = url.split('@')[-1]
    # Strip protocols
    url = re.sub(r'^(https?|git|ssh)://', '', url)
    # Normalize colons to slashes
    url = url.replace(':', '/')
    # Strip .git suffix
    if url.endswith('.git'):
        url = url[:-4]
    return url.strip().lower()

def hash_string(text):
    h = hashlib.sha256(text.encode('utf-8')).hexdigest()
    return f"sha256:{h}"

def resolve_user_id():
    try:
        p = subprocess.run(['gcloud', 'config', 'get-value', 'account', '--quiet'], 
                           capture_output=True, text=True, check=True)
        email = p.stdout.strip()
        if email:
            return hash_string(email)
    except Exception:
        pass
    import getpass
    import socket
    fallback = f"{getpass.getuser()}@{socket.gethostname()}"
    return hash_string(fallback)

def resolve_project_id(workspace_path):
    if workspace_path and os.path.exists(os.path.join(workspace_path, '.git')):
        try:
            p = subprocess.run(['git', '-C', workspace_path, 'config', '--get', 'remote.origin.url'], 
                               capture_output=True, text=True, check=True)
            url = p.stdout.strip()
            if url:
                return hash_string(normalize_git_url(url))
        except Exception:
            pass
    return hash_string(workspace_path or "/default/workspace")
