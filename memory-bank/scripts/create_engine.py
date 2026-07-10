import sys
import os
import json
import time
import urllib.request
import urllib.error
import subprocess
from config import get_plugin_config

def build_payload(display_name, description, project, location):
    return {
        "displayName": display_name,
        "description": description,
        "contextSpec": {
            "memoryBankConfig": {
                "generationConfig": {
                    "model": f"projects/{project}/locations/{location}/publishers/google/models/gemini-3.5-flash"
                },
                "similaritySearchConfig": {
                    "embeddingModel": f"projects/{project}/locations/{location}/publishers/google/models/text-embedding-005"
                },
                "ttlConfig": {
                    "memoryRevisionDefaultTtl": "31536000s"
                },
                "customizationConfigs": [
                    {
                        "memoryTopics": [
                            { "managedMemoryTopic": { "managedTopicEnum": "USER_PERSONAL_INFO" } },
                            { "managedMemoryTopic": { "managedTopicEnum": "USER_PREFERENCES" } },
                            { "managedMemoryTopic": { "managedTopicEnum": "KEY_CONVERSATION_DETAILS" } },
                            { "managedMemoryTopic": { "managedTopicEnum": "EXPLICIT_INSTRUCTIONS" } }
                        ],
                        "generateMemoriesExamples": [],
                        "consolidationConfig": {
                            "revisionsPerCandidateCount": 1
                        },
                        "enableThirdPersonMemories": False
                    }
                ],
                "disableMemoryRevisions": False
            }
        }
    }

def parse_operation_response(data):
    done = data.get("done", False)
    if not done:
        return False, None
    response = data.get("response", {})
    name = response.get("name", "")
    engine_id = name.split("/")[-1] if "/" in name else None
    return True, engine_id

def get_access_token():
    p = subprocess.run(['gcloud', 'auth', 'application-default', 'print-access-token'],
                       capture_output=True, text=True, check=True)
    return p.stdout.strip()

def run_creation(project, location, display_name, description):
    token = get_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-Goog-User-Project": project
    }
    url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines"
    payload = build_payload(display_name, description, project, location)

    print(f"Creating reasoning engine '{display_name}' in project '{project}'...")
    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode('utf-8'), method='POST')
    
    try:
        with urllib.request.urlopen(req) as res:
            op_data = json.loads(res.read().decode('utf-8'))
            op_name = op_data.get("name")
            print(f"Asynchronous creation operation started: {op_name}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        try:
            error_body = e.read().decode('utf-8')
            print(f"Error Response Body:\n{error_body}", file=sys.stderr)
        except Exception as read_err:
            print(f"Could not read error body: {read_err}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error starting creation: {e}", file=sys.stderr)
        sys.exit(1)

    # Poll operation
    poll_url = f"https://{location}-aiplatform.googleapis.com/v1beta1/{op_name}"
    while True:
        print("Polling operation status...")
        time.sleep(10)
        poll_req = urllib.request.Request(poll_url, headers=headers, method='GET')
        try:
            with urllib.request.urlopen(poll_req) as poll_res:
                status_data = json.loads(poll_res.read().decode('utf-8'))
                done, engine_id = parse_operation_response(status_data)
                if done:
                    if engine_id:
                        print(f"\nSuccess! New Memory Bank instance created successfully.")
                        print(f"Engine ID: {engine_id}")
                        print(f"Full Resource Name: projects/{project}/locations/{location}/reasoningEngines/{engine_id}")
                        return engine_id
                    else:
                        error_info = status_data.get("error", {})
                        if error_info:
                            print(f"Operation failed: {error_info.get('message')} (Code: {error_info.get('code')})", file=sys.stderr)
                        else:
                            print("Operation completed but response details are missing.", file=sys.stderr)
                        sys.exit(1)
        except Exception as e:
            print(f"Error polling operation: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    cfg = get_plugin_config()
    project = cfg["project"]
    location = cfg["location"]
    display_name = "Shared Agentic Memory"
    description = "Shared long-term memories for AI agents"
    run_creation(project, location, display_name, description)
