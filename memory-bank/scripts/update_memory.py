import sys
import os
import json
import urllib.request
from config import get_plugin_config

def update_memory(project, location, engine_id, memory_id, new_fact):
    # Endpoint: PATCH /memories/{memory_id}?updateMask=fact
    url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines/{engine_id}/memories/{memory_id}?updateMask=fact"
    
    payload = {
        "fact": new_fact
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
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='PATCH')
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Error updating memory: {e}", file=sys.stderr)
        return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Update an existing memory's fact content in the GCP Memory Bank.")
    parser.add_argument("memory_id", help="The ID of the memory to update (e.g., '1097192207997206528').")
    parser.add_argument("fact", help="The new fact text to set for this memory.")
    args = parser.parse_args()

    cfg = get_plugin_config()
    gcp_project = cfg["project"]
    location = cfg["location"]
    engine_id = cfg["reasoning_engine_id"]

    print(f"Attempting to update memory '{args.memory_id}' with fact content: '{args.fact[:60]}...'")
    res = update_memory(gcp_project, location, engine_id, args.memory_id, args.fact)

    if res is not None and (res.get('done') or 'fact' in res or 'name' in res or isinstance(res, dict)):
        print(f"Successfully updated memory '{args.memory_id}'.")
    else:
        print(f"Failed to update memory '{args.memory_id}' or update operation is in progress.")

if __name__ == '__main__':
    main()
