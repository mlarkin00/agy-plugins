import sys
import os
import json
import time
import urllib.request
from resolve_scope import resolve_user_id, resolve_project_id
from config import get_plugin_config

def get_state_file_path():
    home = os.path.expanduser('~')
    state_dir = os.path.join(home, '.gemini', 'antigravity-cli')
    os.makedirs(state_dir, exist_ok=True)
    return os.path.join(state_dir, '.gcp_memory_bank_sidecar_state.json')

def get_brain_dir_path():
    home = os.path.expanduser('~')
    return os.path.join(home, '.gemini', 'antigravity-cli', 'brain')

def should_run_sidecar(interval_seconds=86400):
    state_path = get_state_file_path()
    if not os.path.exists(state_path):
        return True
    try:
        with open(state_path, 'r') as f:
            data = json.loads(f.read())
            last_run = data.get('last_run', 0)
            if time.time() - last_run >= interval_seconds:
                return True
    except Exception:
        return True
    return False

def save_state_timestamp():
    state_path = get_state_file_path()
    try:
        data = {"last_run": time.time()}
        with open(state_path, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass

def aggregate_transcripts(brain_dir):
    events = []
    if not brain_dir or not os.path.exists(brain_dir):
        return events

    for root, _, files in os.walk(brain_dir):
        for file in files:
            if file == 'transcript.jsonl':
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                step = json.loads(line.strip())
                            except (json.JSONDecodeError, TypeError):
                                continue  # Skip corrupted lines gracefully
                            source = step.get('source')
                            content = step.get('content')
                            if source == 'USER_EXPLICIT' and content:
                                events.append({
                                    "content": {
                                        "role": "user",
                                        "parts": [{"text": content}]
                                    }
                                })
                            elif source == 'MODEL' and content:
                                events.append({
                                    "content": {
                                        "role": "model",
                                        "parts": [{"text": content}]
                                    }
                                })
                except Exception:
                    pass
    return events

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
    except Exception:
        pass

    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            return data.get('memories', [])
    except Exception as e:
        sys.stderr.write(f"Warning: sidecar failed to list memories for deduplication: {e}\n")
        return []

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
    except Exception:
        pass

    try:
        req = urllib.request.Request(url, headers=headers, method='DELETE')
        with urllib.request.urlopen(req, timeout=10) as res:
            res.read()
            return True
    except Exception as e:
        sys.stderr.write(f"Warning: sidecar failed to delete duplicate memory '{memory_id}': {e}\n")
        return False

def deduplicate_memories(project, location, engine_id):
    """
    Retrieves all memories, identifies duplicates under the same scope and normalized fact,
    and deletes the redundant ones (keeping the oldest by createTime).
    """
    sys.stderr.write("Sidecar: Reviewing and deduplicating existing memories...\n")
    memories = list_memories(project, location, engine_id)
    if not memories:
        sys.stderr.write("Sidecar: No memories found to deduplicate.\n")
        return

    def normalize_fact(text):
        if not text:
            return ""
        return " ".join(text.strip().lower().split())

    # Group memories by (user_hash, project_hash, normalized_fact)
    grouped = {}
    for m in memories:
        scope = m.get('scope', {})
        user_hash = scope.get('user', '')
        project_hash = scope.get('project', '')
        fact = m.get('fact', '')
        norm_fact = normalize_fact(fact)
        
        key = (user_hash, project_hash, norm_fact)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(m)

    deleted_count = 0
    for key, items in grouped.items():
        if len(items) <= 1:
            continue
        
        # Sort items by createTime (oldest first). Parse ISO 8601 strings
        items_sorted = sorted(items, key=lambda x: x.get('createTime', ''))
        
        keep_item = items_sorted[0]
        duplicate_items = items_sorted[1:]
        
        keep_name = keep_item.get('name', '')
        keep_id = keep_name.split('/')[-1] if '/' in keep_name else keep_name
        
        for dup in duplicate_items:
            dup_name = dup.get('name', '')
            dup_id = dup_name.split('/')[-1] if '/' in dup_name else dup_name
            if dup_id and dup_id != keep_id:
                sys.stderr.write(f"Sidecar: Deleting duplicate memory ID '{dup_id}' (keeping oldest ID '{keep_id}')\n")
                if delete_memory(project, location, engine_id, dup_id):
                    deleted_count += 1

    if deleted_count > 0:
        sys.stderr.write(f"Sidecar: Successfully cleaned up {deleted_count} duplicate memories.\n")
    else:
        sys.stderr.write("Sidecar: No duplicate memories detected.\n")

def run():
    force = "--force" in sys.argv
    if not force and not should_run_sidecar():
        return

    input_data = {}
    if not sys.stdin.isatty():
        try:
            input_data = json.loads(sys.stdin.read())
        except Exception:
            pass

    workspace_paths = input_data.get('workspacePaths', [])
    workspace_path = workspace_paths[0] if workspace_paths else None

    brain_dir = get_brain_dir_path()
    events = aggregate_transcripts(brain_dir)
    # Limit to the most recent 500 events to stay within API payload size limits and prevent timeouts
    if len(events) > 500:
        events = events[-500:]

    user_hash = resolve_user_id()
    # Default to global scope for automatic memory consolidation
    project_hash = "global"

    cfg = get_plugin_config()
    gcp_project = cfg["project"]
    location = cfg["location"]
    engine_id = cfg["reasoning_engine_id"]

    # Deduplicate memories
    deduplicate_memories(gcp_project, location, engine_id)

    # Consolidate new memories if events exist
    if events:
        success = send_generation_request(gcp_project, location, engine_id, user_hash, project_hash, events)
        if success:
            save_state_timestamp()

if __name__ == '__main__':
    run()
