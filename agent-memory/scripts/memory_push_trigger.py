import json
import os
import subprocess
import sys

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from stdin: {e}", file=sys.stderr)
        # Exit with 0 to avoid failing the agent session if background sync checks fail.
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error reading stdin: {e}", file=sys.stderr)
        # Exit with 0 to avoid failing the agent session if background sync checks fail.
        sys.exit(0)

    transcript_path = input_data.get("transcriptPath")
    step_idx = input_data.get("stepIdx")

    if not transcript_path or step_idx is None:
        print("Debug: transcriptPath or stepIdx missing", file=sys.stderr)
        # Exit with 0 to avoid failing the agent session if background sync checks fail.
        sys.exit(0)

    if not os.path.exists(transcript_path):
        print(f"Debug: transcript file does not exist: {transcript_path}", file=sys.stderr)
        # Exit with 0 to avoid failing the agent session if background sync checks fail.
        sys.exit(0)

    trigger_push = False
    memory_path = os.path.abspath(os.path.expanduser("~/.gemini/GEMINI.md"))
    repo_path = os.path.abspath(os.path.expanduser("~/.agents/agent-memory/GEMINI.md"))

    with open(transcript_path, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("step_index") == step_idx:
                    tool_calls = entry.get("tool_calls", [])
                    for call in tool_calls:
                        name = call.get("name")
                        args = call.get("args", {})
                        file_path = args.get("TargetFile", args.get("file_path", args.get("path", "")))
                        
                        if name in ["write_to_file", "replace_file_content", "multi_replace_file_content"]:
                            if file_path:
                                target_path = os.path.abspath(os.path.expanduser(file_path.strip('"')))
                                if target_path == memory_path or target_path == repo_path:
                                    trigger_push = True
                                    break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Debug: Error parsing line in transcript: {e}", file=sys.stderr)
                continue

    if trigger_push:
        print("TRIGGER PUSH")
        subprocess.run(["/google/bin/releases/jetski-devs/tools/cli", "agents", "run", "memory-pusher-jetski"])

if __name__ == "__main__":
    main()
