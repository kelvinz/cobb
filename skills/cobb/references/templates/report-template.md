# Review Report Template

Use this exact result contract for standalone and commit-triggered reviews.

```text
Review Report

Decision:
- Good to commit: Yes | No

Review fingerprint:
- Branch: <current branch>
- HEAD: <full commit hash>
- Comparison base: <branch> @ <full commit hash>
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
- Good to commit=Yes with suggestions: use the numbered suggestion workflow; `0` finalises a feature branch or concludes a direct default-branch review.
- Good to commit=Yes with no suggestions: offer `0` to finalise a feature branch; conclude a direct default-branch review without finalise.

Numbered next actions:
- <render the applicable blocker/suggestion/clean-pass numeric menu and mark one evidence-based reply Recommended>
```

Number only actual findings. Do not emit placeholder IDs when a section is empty.
