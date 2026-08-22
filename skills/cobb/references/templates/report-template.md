# Review Report Template

Use this exact result contract for standalone and commit-triggered reviews.

```text
Review Report

Decision:
- Good to commit: Yes | No

Review fingerprint:
- Branch: <current branch>
- Branch kind: base | feature
- HEAD: <full commit hash>
- Comparison base: <branch> @ <full commit hash> (resolved from: argument | finalise-target | upstream | session-start | repo-convention | remote-head | local-fallback)
- Effective merge base: <full commit hash>
- Worktree: clean | dirty
- Valid until: any commit, base movement, or worktree change

Blockers (must fix):
- B1: <finding with file/line, impact, and required change>
- None

Suggestions (optional):
- S1: <finding with file/line, value, scope classification, and concrete improvement>
- None

Missing evidence:
- E1: <required or optional evidence, exact command/artifact, and B#/S# cross-reference>
- None

Security notes:
- ...

Regression risks / watch-outs:
- ...

Proposed context updates:
- B# | S# | Finalise: <entry for selected implement/finalise workflow>
- None: <reason>

Recommended next step:
- Good to commit=No: use the numbered blocker workflow; finalise is unavailable.
- Good to commit=Yes with suggestions: use the numbered suggestion workflow; the recommended reply renders as option `0`.
- Good to commit=Yes with no suggestions: offer finalise as option `0` **Recommended** on a feature branch; conclude a direct base-branch review without finalise.

Numbered next actions:
- <render the applicable blocker/suggestion/clean-pass numeric menu with the evidence-based recommended reply as `0` and the alternatives as `1..N`>
```

Number only actual findings. Do not emit placeholder IDs when a section is empty.
