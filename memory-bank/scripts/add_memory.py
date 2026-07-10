import sys
import os
import json
import urllib.request
import argparse
from resolve_scope import resolve_user_id, resolve_project_id
from config import get_plugin_config

def add_memory(project, location, engine_id, user_hash, project_hash, fact):
    url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines/{engine_id}/memories"
    payload = {
        "scope": {
            "user": user_hash,
            "project": project_hash
        },
        "fact": fact,
        "ttl": "2592000s" # 30 days
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-User-Project": project
    }
    try:
        import subprocess
        p = subprocess.run(['gcloud', 'auth', 'application-default', 'print-access-token'], 
                           capture_output=True, text=True, check=True)
        token = p.stdout.strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
    except Exception as e:
        print(f"Warning: failed to print access token via gcloud: {e}", file=sys.stderr)

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Error adding memory: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Add a new memory fact to the GCP Memory Bank.")
    parser.add_argument("fact", help="The text of the memory fact to store.")
    parser.add_argument("--scope", choices=["global", "project"], default="global",
                        help="Whether to store this memory globally or only for the current project scope. Defaults to global.")
    args = parser.parse_args()

    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_hash = resolve_user_id()
    project_hash = "global" if args.scope == "global" else resolve_project_id(workspace_path)

    cfg = get_plugin_config()
    gcp_project = cfg["project"]
    location = cfg["location"]
    engine_id = cfg["reasoning_engine_id"]

    print(f"Attempting to add memory with fact content: '{args.fact[:60]}...'")
    print(f"Scope: User={user_hash[:10]}... Project={project_hash[:10]}...")
    
    res = add_memory(gcp_project, location, engine_id, user_hash, project_hash, args.fact)

    if res is not None and (res.get('done') or 'fact' in res or 'name' in res or isinstance(res, dict)):
        name = res.get('name', 'N/A')
        memory_id = name.split('/')[-1] if '/' in name else name
        print(f"Successfully added memory '{memory_id}'.")
    else:
        print("Failed to add memory.")

if __name__ == '__main__':
    main()
