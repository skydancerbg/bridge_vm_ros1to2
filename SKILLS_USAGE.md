# Skills Usage

## Repo-Local Skills
This repo can include Codex skills under `.codex/skills/`.
These are repo-local instructions that help Codex follow the expected workflow for this bridge VM repo without changing the live system structure.

## Recommended Working Directory
Codex should usually be in `/home/swu/bridge-vm-config-repo` before using repo-local skills.
That keeps relative paths, scripts, manifests, and git operations aligned with the mirrored bridge repo instead of `/root` or another unrelated directory.

## Manual Skill Invocation
Invoke a skill explicitly in the prompt by naming it and stating the task.

Example:
`Use the bridge-precommit-commit skill. Refresh the mirror from live state, verify the bridge runtime, update mirrored docs/manifests, stage the relevant files, and if everything is verified ready, commit with the standard post-fix message.`

## Automatic Invocation
Codex may automatically use a repo-local skill when the request clearly matches that skill's purpose.
That is not guaranteed, so explicit invocation is preferred when the workflow matters.

## bridge-precommit-commit
Use this skill for the bridge repo pre-commit workflow:
- refresh the mirrored repo state from live files
- verify the bridge runtime and key services
- update mirrored docs and manifests to match the current bridge state
- stage the relevant repo changes
- commit only when explicitly requested and the repo is verified ready

## Adding Future Skills
Add future repo-local skills to `.codex/skills/` and document each one here as a new section.
Keep this file as the shared usage guide for all Codex skills in this repo.
