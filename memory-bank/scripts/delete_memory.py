import sys
import os
import json
import urllib.request
from config import get_plugin_config

def delete_memory(project, location, engine_id, memory_id):
    # Endpoint: DELETE /memories/{memory_id}
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
        print(f"Warning: failed to print access token via gcloud: {e}", file=sys.stderr)

    try:
        req = urllib.request.Request(url, headers=headers, method='DELETE')
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Error deleting memory: {e}", file=sys.stderr)
        return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Delete a memory from GCP Reasoning Engine Memory Bank.")
    parser.add_argument("memory_id", help="The ID of the memory to delete (e.g., '1097192207997206528').")
    args = parser.parse_args()

    cfg = get_plugin_config()
    gcp_project = cfg["project"]
    location = cfg["location"]
    engine_id = cfg["reasoning_engine_id"]

    print(f"Attempting to delete memory '{args.memory_id}'...")
    res = delete_memory(gcp_project, location, engine_id, args.memory_id)

    if res is not None and (res.get('done') or isinstance(res, dict)):
        print(f"Successfully deleted memory '{args.memory_id}'.")
    else:
        print(f"Failed to delete memory '{args.memory_id}' or delete operation is in progress.")

if __name__ == '__main__':
    main()
