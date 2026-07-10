import sys
import os
import json
import urllib.request
from resolve_scope import resolve_user_id, resolve_project_id
from config import get_plugin_config

def query_memory_bank(project, location, engine_id, user_hash, project_hash, query):
    url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines/{engine_id}/memories:retrieve"
    payload = {
        "scope": {
            "user": user_hash,
            "project": project_hash
        },
        "similaritySearchParams": {
            "searchQuery": query
        }
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
        print(f"Warning: failed to print access token via gcloud: {e}")

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            retrieved = data.get('retrievedMemories', [])
            return retrieved
    except Exception as e:
        print(f"Error retrieving memories: {e}")
        return []

def main():
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "retrieve key developer settings, configurations, workflows"
    
    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_hash = resolve_user_id()
    project_hash = resolve_project_id(workspace_path)

    cfg = get_plugin_config()
    gcp_project = cfg["project"]
    location = cfg["location"]
    engine_id = cfg["reasoning_engine_id"]

    print(f"Querying GCP Memory Bank for scope:")
    print(f"  User Hash: {user_hash}")
    print(f"  Project Hash: {project_hash}")
    print(f"  Search Query: '{query}'\n")

    results_global = query_memory_bank(gcp_project, location, engine_id, user_hash, "global", query)
    results_project = query_memory_bank(gcp_project, location, engine_id, user_hash, project_hash, query)
    
    # Combine and sort by distance
    results = results_global + results_project
    results.sort(key=lambda x: x.get('distance', 0.0))
    
    if not results:
        print("No memories matched or retrieved.")
        return

    print(f"Retrieved {len(results)} matches:")
    for i, item in enumerate(results, 1):
        memory = item.get('memory', {})
        fact = memory.get('fact', 'N/A')
        scope = memory.get('scope', {})
        distance = item.get('distance', 0.0)
        print(f"\nMatch #{i} (distance/score: {distance:.4f}):")
        print(f"  Scope: User={scope.get('user')[:10]}... Project={scope.get('project')[:10]}...")
        print(f"  Fact:  {fact}")

if __name__ == '__main__':
    main()
