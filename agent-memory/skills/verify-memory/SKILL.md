---
name: verify-memory-jetski
description: Use when the user asks to check memory health for Jetski, says memory isn't loading or saving, or when you want to verify the memory system is intact. Runs automated health checks and applies minor self-repairs.
---

Run the verify-memory-jetski health check script:

```bash
bash ~/.gemini/scripts/verify-memory-jetski.sh
```

Interpret the output:

- **No output:** All checks passed. Memory system is healthy.
- **`[verify-memory-jetski] ⚠ ...` lines:** Structural problem found. Tell the user what was reported, then **offer to run bootstrap-memory-jetski yourself**.

After running, confirm whether memory is healthy or what action is needed.
