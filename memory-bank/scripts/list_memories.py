import sys
import os
import json
import urllib.request
from resolve_scope import resolve_user_id, resolve_project_id
from config import get_plugin_config

def list_memories(project, location, engine_id):
    url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines/{engine_id}/memories"
    
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
        req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            return data.get('memories', [])
    except Exception as e:
        print(f"Error listing memories: {e}", file=sys.stderr)
        return []

def main():
    import argparse
    parser = argparse.ArgumentParser(description="List memories from GCP Reasoning Engine Memory Bank.")
    parser.add_argument("--scope", choices=["all", "current"], default="current",
                        help="Whether to list all memories in the engine regardless of scope ('all'), or only those matching the current project and global scopes ('current').")
    args = parser.parse_args()

    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_hash = resolve_user_id()
    project_hash = resolve_project_id(workspace_path)

    cfg = get_plugin_config()
    gcp_project = cfg["project"]
    location = cfg["location"]
    engine_id = cfg["reasoning_engine_id"]

    memories = list_memories(gcp_project, location, engine_id)

    if not memories:
        print("No memories found in the Memory Bank.")
        return

    # Filter by scope if requested
    if args.scope == "current":
        filtered = []
        for m in memories:
            m_scope = m.get('scope', {})
            if m_scope.get('user') == user_hash and m_scope.get('project') in ("global", project_hash):
                filtered.append(m)
        memories = filtered
        print(f"Listing memories for current scope (User Hash: {user_hash[:10]}..., Project Hash: {project_hash[:10]}... or global):")
    else:
        print("Listing all memories in the GCP Memory Bank:")

    if not memories:
        print("No memories match the current scope.")
        return

    for i, m in enumerate(memories, 1):
        name = m.get('name', 'N/A')
        memory_id = name.split('/')[-1] if '/' in name else name
        fact = m.get('fact', 'N/A')
        scope = m.get('scope', {})
        create_time = m.get('createTime', 'N/A')
        print(f"\n[{i}] Memory ID: {memory_id}")
        print(f"    Create Time: {create_time}")
        print(f"    Scope:       User={scope.get('user')[:10]}... Project={scope.get('project')[:10]}...")
        print(f"    Fact:        {fact}")

if __name__ == '__main__':
    main()
