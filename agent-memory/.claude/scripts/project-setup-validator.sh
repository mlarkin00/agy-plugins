#!/usr/bin/env bash
# SessionStart validator: read-only check that the current directory looks like
# a properly-configured agent project. Silent unless project signals are present
# AND something is missing — in which case it suggests /setting-up-projects.

set -u

dir="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$dir" ] || exit 0

# --- Project signal detection ---------------------------------------------
# A directory "looks like a project" if any of:
#   - .git exists in cwd or up to 3 parent levels
#   - any of AGENTS.md / GEMINI.md / CLAUDE.md is present in cwd
has_git=0
root="$dir"
probe="$dir"
for _ in 1 2 3 4; do
  if [ -d "$probe/.git" ] || [ -f "$probe/.git" ]; then
    has_git=1
    root="$probe"
    break
  fi
  parent="$(dirname "$probe")"
  [ "$parent" = "$probe" ] && break
  probe="$parent"
done

# Anchor the brief-file check to the repo root if we found one — otherwise cwd.
has_agents=0; [ -f "$root/AGENTS.md" ] && has_agents=1
has_gemini=0; [ -f "$root/GEMINI.md" ] && has_gemini=1
has_claude=0; [ -f "$root/CLAUDE.md" ] && has_claude=1
has_any_brief=$(( has_agents | has_gemini | has_claude ))

# Bail out silently if this doesn't look like a project at all.
if [ "$has_git" -eq 0 ] && [ "$has_any_brief" -eq 0 ]; then
  exit 0
fi

# Skip if cwd is inside a known throwaway location.
case "$dir" in
  /tmp/*|*/node_modules/*|*/.venv/*|*/venv/*|*/dist/*|*/build/*) exit 0 ;;
esac

# --- Gap detection --------------------------------------------------------
missing=()
[ "$has_agents" -eq 0 ] && missing+=("AGENTS.md")
[ "$has_gemini" -eq 0 ] && missing+=("GEMINI.md")
[ "$has_claude" -eq 0 ] && missing+=("CLAUDE.md")
[ -f "$root/DESIGN.md" ] || missing+=("DESIGN.md")
[ -f "$root/.agents/TODO.md" ] || missing+=(".agents/TODO.md")

if [ "${#missing[@]}" -eq 0 ]; then
  exit 0
fi

# --- Report (stdout becomes SessionStart additional context) --------------
printf 'Project setup validator — directory looks like a project but is missing:\n'
for f in "${missing[@]}"; do
  printf '  - %s\n' "$f"
done
printf '\nOffer the user: "Want me to run /setting-up-projects to fix the missing files?"\n'
printf 'Do NOT run it unprompted. Skip the offer if the user is clearly mid-task on something unrelated.\n'

exit 0
