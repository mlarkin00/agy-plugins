import sys
import os
import json
import urllib.request
import argparse
from resolve_scope import resolve_user_id, resolve_project_id
from config import get_plugin_config

def get_memory(project, location, engine_id, memory_id):
    url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines/{engine_id}/memories/{memory_id}"
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
        pass

    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=10) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching memory {memory_id}: {e}", file=sys.stderr)
        return None

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
        pass

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        print(f"Error creating memory: {e}", file=sys.stderr)
        return None

def delete_memory(project, location, engine_id, memory_id):
    url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines/{engine_id}/memories/{memory_id}"
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
        pass

    try:
        req = urllib.request.Request(url, headers=headers, method='DELETE')
        with urllib.request.urlopen(req, timeout=10) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        print(f"Error deleting old memory {memory_id}: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Re-scope an existing global memory to the current project.")
    parser.add_argument("memory_id", help="The ID of the memory to re-scope to the current project.")
    args = parser.parse_args()

    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_hash = resolve_user_id()
    project_hash = resolve_project_id(workspace_path)

    cfg = get_plugin_config()
    gcp_project = cfg["project"]
    location = cfg["location"]
    engine_id = cfg["reasoning_engine_id"]

    print(f"Attempting to re-scope memory '{args.memory_id}' to project scope...")
    
    # 1. Fetch
    memory = get_memory(gcp_project, location, engine_id, args.memory_id)
    if not memory:
        print(f"Failed to fetch memory '{args.memory_id}'.")
        return
        
    fact = memory.get('fact')
    if not fact:
        print(f"Memory '{args.memory_id}' does not have a fact.")
        return

    # 2. Re-create
    print(f"Creating new memory in project scope: Project Hash={project_hash[:10]}...")
    new_memory = add_memory(gcp_project, location, engine_id, user_hash, project_hash, fact)
    if not new_memory:
        print("Failed to create new project-scoped memory.")
        return
        
    new_name = new_memory.get('name', 'N/A')
    new_id = new_name.split('/')[-1] if '/' in new_name else new_name
    print(f"Created new memory with ID '{new_id}'.")

    # 3. Delete old
    print(f"Deleting old global memory '{args.memory_id}'...")
    delete_memory(gcp_project, location, engine_id, args.memory_id)
    
    print(f"Successfully re-scoped memory. Old ID: {args.memory_id} -> New ID: {new_id}")

if __name__ == '__main__':
    main()
