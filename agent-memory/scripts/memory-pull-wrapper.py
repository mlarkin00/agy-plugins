import sys
import json
import os
import subprocess

def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    conv_id = input_data.get("conversationId")
    artifact_dir = input_data.get("artifactDirectoryPath")

    if not conv_id or not artifact_dir:
        print("Missing conversationId or artifactDirectoryPath", file=sys.stderr)
        sys.exit(1)

    flag_file = os.path.join(artifact_dir, f".memory_pulled_{conv_id}")

    if not os.path.exists(flag_file):
        # Run the actual pull script
        res = subprocess.run(["./scripts/memory-pull.sh"], capture_output=True, text=True)
        if res.returncode != 0:
             print(f"Pull failed: {res.stderr}", file=sys.stderr)
        else:
             # Create flag file
             with open(flag_file, 'w') as f:
                 f.write("done")
             print("Pulled memory successfully", file=sys.stderr)

    # Output required JSON on stdout
    print(json.dumps({}))

if __name__ == "__main__":
    main()
