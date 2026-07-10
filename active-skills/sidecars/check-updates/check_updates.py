import os
import sys
import json
import urllib.request
from datetime import datetime, timezone

def parse_version(v_str):
    try:
        return tuple(map(int, v_str.strip().split('.')))
    except ValueError:
        return (0, 0, 0)

def check_for_updates():
    # 1. Locate and parse local plugin.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.abspath(os.path.join(current_dir, '../../plugin.json'))
    
    try:
        with open(local_path, 'r', encoding='utf-8') as f:
            local_manifest = json.load(f)
            local_version = local_manifest.get('version', '0.0.0')
    except Exception as e:
        print(f"Error reading local manifest: {e}", file=sys.stderr)
        local_version = '0.0.0'

    # 2. Fetch remote plugin.json
    remote_url = 'https://raw.githubusercontent.com/mlarkin00/agy-plugins/main/active-skills/plugin.json'
    try:
        req = urllib.request.Request(remote_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            remote_manifest = json.loads(response.read().decode('utf-8'))
            remote_version = remote_manifest.get('version', '0.0.0')
    except Exception as e:
        print(f"Error fetching remote manifest: {e}", file=sys.stderr)
        remote_version = '0.0.0'

    # 3. Compare versions
    update_available = parse_version(remote_version) > parse_version(local_version)

    if update_available:
        print(f"[UPDATE] A newer version of active-skills is available: local={local_version}, remote={remote_version}")
    else:
        print(f"[OK] active-skills is up-to-date (v{local_version})")

    # 4. Persist state
    status_data = {
        "last_checked": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "local_version": local_version,
        "remote_version": remote_version,
        "update_available": update_available
    }

    data_dir = os.environ.get('ANTIGRAVITY_EXECUTABLE_DATA_DIR')
    if not data_dir:
        data_dir = os.path.join(current_dir, 'data')
    
    try:
        os.makedirs(data_dir, exist_ok=True)
        status_path = os.path.join(data_dir, 'status.json')
        with open(status_path, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"Error writing status.json: {e}", file=sys.stderr)

    return status_data

if __name__ == '__main__':
    check_for_updates()
