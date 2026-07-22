# agy-plugins — retired

**This repository is archived. Its plugins now live in [`mlarkin00/plugins`](https://github.com/mlarkin00/plugins).**

That repo serves both runtimes from one place: a Claude Code marketplace (`mlarkin00-plugins`) and an Antigravity plugin bundle. Keeping a separate Antigravity-only repo meant vendoring the same plugins twice and holding two sync workflows in step, so the two were consolidated.

## Antigravity

Clone the repo once, then bulk-install everything in it:

```bash
git clone https://github.com/mlarkin00/plugins
agy plugin install ./plugins
```

Pointing `agy plugin install` at a directory that contains several plugins reports `Found bulk plugins directory` and installs them all — `active-skills`, `agent-memory`, `llm-wiki`, `memory-bank`, and `skill-usage`. Antigravity reads Claude-format plugins natively, converting skills, agents, commands, and hooks as it installs.

## Claude Code

```
/plugin marketplace add mlarkin00/plugins
/plugin install active-skills@mlarkin00-plugins
```

## Editing skills

The skills themselves are authored in [`mlarkin00/active-skills`](https://github.com/mlarkin00/active-skills) and mirrored into the marketplace by CI. Clone that repo to add or change a skill — not this one, and not the marketplace.
