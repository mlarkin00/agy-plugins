# Agent Memory for Jetski

A Jetski plugin for managing agent memory across sessions. It provides skills and agents to save, retrieve, and verify memory stored in a global `GEMINI.md` file.

## Installation

Since Jetski does not support direct installation from a Git URL, follow these steps:

1.  **Clone the repository** to your local machine:
    ```bash
    git clone https://github.com/mlarkin00/agent-memory-jetski.git
    ```

2.  **Install the plugin** using the Jetski CLI, pointing to the cloned directory:
    ```bash
    jetski plugin install /path/to/cloned/agent-memory-jetski
    ```

## Post-Installation

After installation, you should verify the setup by running the verification script or using the verification skill.

### Verification

Run the provided health check script:
```bash
bash scripts/verify-memory-jetski.sh
```
This script will check if the memory repo is set up correctly and fix minor issues silently.

## Available Skills

-   `add-memory-jetski`: Save information to long-term memory.
-   `verify-memory-jetski`: Check the health of the memory system.
-   `uninstall-memory-jetski`: Uninstall the memory extension.

## Available Agents

-   `bootstrap-memory-jetski`: Sets up or restores the memory system.
-   `memory-puller-jetski`: Pulls the latest memory state from remote.
-   `memory-pusher-jetski`: Pushes local memory changes to remote.
