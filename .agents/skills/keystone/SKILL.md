---
name: keystone
description: Keystone adapter for Agent Skills hosts such as OpenCode, GitHub Copilot, and VS Code. Use when the user invokes /keystone or explicitly asks Keystone to route work.
---

# Keystone Agent Skills Adapter

This is a thin adapter for hosts that discover skills from `.agents/skills/<name>/SKILL.md`.

The canonical Keystone skill lives at:

```text
../../../skills/keystone/SKILL.md
```

When this adapter is loaded:

1. Read `../../../skills/keystone/SKILL.md`, resolved relative to this adapter file's directory.
2. Follow the canonical Keystone entrypoint exactly.
3. Resolve Keystone module, gate, and helper paths relative to `skills/keystone/`, not relative to this adapter directory.
4. Keep the public surface as one Keystone skill. Do not expose internal modules as separate public commands.
