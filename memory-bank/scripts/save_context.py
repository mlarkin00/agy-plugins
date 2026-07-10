import sys
import os
import json
import urllib.request
from resolve_scope import resolve_user_id, resolve_project_id
from config import get_plugin_config

def send_generation_request(project, location, engine_id, user_hash, project_hash, events):
    url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines/{engine_id}/memories:generate"
    payload = {
        "scope": {
            "user": user_hash,
            "project": project_hash
        },
        "directContentsSource": {
            "events": events
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
    except Exception:
        pass

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status == 200
    except Exception:
        return False

def run():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        return

    transcript_path = input_data.get('transcriptPath')
    workspace_paths = input_data.get('workspacePaths', [])
    workspace_path = workspace_paths[0] if workspace_paths else None

    if not transcript_path or not os.path.exists(transcript_path):
        return

    events = []
    try:
        with open(transcript_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    step = json.loads(line.strip())
                except (json.JSONDecodeError, TypeError):
                    continue  # Skip corrupt lines gracefully
                source = step.get('source')
                content = step.get('content')
                
                if source == 'USER_EXPLICIT' and content:
                    events.append({"role": "USER", "content": content})
                elif source == 'MODEL' and content:
                    events.append({"role": "AGENT", "content": content})
    except Exception:
        return

    if not events:
        return

    user_hash = resolve_user_id()
    # Default to global scope for automatic memory consolidation
    project_hash = "global"

    cfg = get_plugin_config()
    gcp_project = cfg["project"]
    location = cfg["location"]
    engine_id = cfg["reasoning_engine_id"]

    send_generation_request(gcp_project, location, engine_id, user_hash, project_hash, events)

if __name__ == '__main__':
    run()
