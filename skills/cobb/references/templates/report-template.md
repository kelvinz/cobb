# Review Report Template

Use this result contract for standalone and called reviews. Keep the inspection report separate from repairs performed by the caller.

```text
Review Report

Caller: standalone | commit | finalise | hotfix
Review mode: branch | staged-hotfix

Decision:
- Good to commit: Yes | No

Review fingerprint:
- Branch: <current branch>
- Branch kind: base | feature
- HEAD: <full commit hash>
- Comparison base (branch mode): <branch> @ <full commit hash> (resolved from: argument | finalise-target | upstream | session-start | repo-convention | remote-head | local-fallback)
- Effective merge base (branch mode): <full commit hash>
- Staged tree (staged-hotfix mode): <full tree hash>
- Upstream (staged-hotfix mode): <ref> @ <full commit hash> | none
- Remote freshness: refreshed | unverified, with reason | no remotes
- Worktree: clean | matches staged tree | dirty
- Valid until: any branch, HEAD, base/upstream, index, or worktree change

Blockers (must fix):
- B1: <finding with file/line, evidence, impact, required change, and decision needed or none>
- None

Suggestions (non-blocking):
- S1: <finding with file/line, evidence, value, scope classification, concrete improvement, and decision needed or none>
- None

Missing evidence:
- E1: <required or optional evidence, exact command/artifact, and B#/S# cross-reference>
- None

Dismissed (considered, not findings):
- <candidate, which lens raised it, and the one-line reason: no reachable path | preference only | consistent with repository convention | out of scope>
- None

Security notes:
- ...

Regression risks / watch-outs:
- ...

Proposed context updates:
- B# | S# | Finalise: <entry for the repair/finalise workflow>
- None: <reason>

Next action:
- Called review: return to the automatic repair loop.
- Standalone: state the recommended next action and remain read-only.

Decisions needed:
- <actual unresolved choice, affected finding IDs, and why it cannot be settled from evidence>
- None
```

Include only fingerprint fields for the selected mode. Number only actual findings; use `None` for an empty section.
