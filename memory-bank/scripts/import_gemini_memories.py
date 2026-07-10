import sys
import os
import json
import urllib.request
from resolve_scope import resolve_user_id, resolve_project_id
from config import get_plugin_config

def parse_gemini_memories(filepath):
    memories = []
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return memories
    
    with open(filepath, 'r', encoding='utf-8') as f:
        in_memories_section = False
        for line in f:
            line = line.strip()
            if "## Gemini Added Memories" in line:
                in_memories_section = True
                continue
            if in_memories_section:
                if line.startswith("- "):
                    memory = line[2:].strip()
                    # Remove markdown formatting like bolding **MANDATORY** if present
                    memory = memory.replace("**MANDATORY**", "MANDATORY")
                    if memory:
                        memories.append(memory)
                elif line.startswith("#"):
                    # Another header, stop parsing
                    break
    return memories

def save_memory_fact(project, location, engine_id, user_hash, project_hash, fact):
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
        print(f"Warning: failed to print access token via gcloud: {e}")

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as res:
            if res.status == 200 or res.status == 201:
                return True
    except Exception as e:
        print(f"Error saving fact '{fact[:40]}...': {e}")
        return False

def verify_memories(project, location, engine_id, user_hash, project_hash):
    url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines/{engine_id}/memories:retrieve"
    payload = {
        "scope": {
            "user": user_hash,
            "project": project_hash
        },
        "similaritySearchParams": {
            "searchQuery": "verify and validate configuration, search documentation libraries, Well-Lit Path workflows"
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
            data = json.loads(res.read().decode('utf-8'))
            retrieved = data.get('retrievedMemories', [])
            return [item.get('memory', {}).get('fact') for item in retrieved if item.get('memory', {}).get('fact')]
    except Exception as e:
        print(f"Error retrieving memories for verification: {e}")
        return []

def main():
    gemini_path = "/home/matthewlarkin/.gemini/GEMINI.md"
    memories = parse_gemini_memories(gemini_path)
    if not memories:
        print("No memories parsed from GEMINI.md.")
        return

    print(f"Parsed {len(memories)} memories from GEMINI.md:")
    for i, m in enumerate(memories, 1):
        print(f" {i}. {m[:100]}...")

    user_hash = resolve_user_id()
    project_hash = resolve_project_id("/home/matthewlarkin/agent-skills/plugins/memory-bank-plugin")

    cfg = get_plugin_config()
    gcp_project = cfg["project"]
    location = cfg["location"]
    engine_id = cfg["reasoning_engine_id"]

    print(f"\nTargeting GCP Reasoning Engine: projects/{gcp_project}/locations/{location}/reasoningEngines/{engine_id}")
    print(f"Resolved User Hash: {user_hash}")
    print(f"Resolved Project Hash: {project_hash}")

    print("\nSaving memories to Memory Bank...")
    saved_count = 0
    for m in memories:
        success = save_memory_fact(gcp_project, location, engine_id, user_hash, project_hash, m)
        if success:
            print(f" [SUCCESS] Persisted memory: '{m[:60]}...'")
            saved_count += 1
        else:
            print(f" [FAILED] Failed to persist memory: '{m[:60]}...'")

    print(f"\nSaved {saved_count}/{len(memories)} memories.")

    print("\nRetrieving and verifying memories from Memory Bank...")
    retrieved = verify_memories(gcp_project, location, engine_id, user_hash, project_hash)
    if retrieved:
        print(f"Successfully retrieved {len(retrieved)} memories from Memory Bank:")
        for i, fact in enumerate(retrieved, 1):
            print(f" {i}. {fact}")
    else:
        print("No memories retrieved. Note: If using mock GCP endpoints in tests, retrieval may return empty list.")

if __name__ == "__main__":
    main()
