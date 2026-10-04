# menu

Show the subcommand menu for a bare `/cobb`, or for a request whose intent is ambiguous. Stay read-only.

Shared guardrails from the cobb router apply.

1. Read `tasks/` — list active PRDs (`f-##`, name, `Status`, `Priority`) and check git branch/commit state.
2. Print the subcommand menu (the Dispatch table in `SKILL.md`) so the user sees the options.
3. Offer the phases as a numbered choice, recommending the one repository state indicates, so the user can reply with a number instead of a command name.
4. Recommend the single next phase based on state, for example:
   - no `tasks/context.md` or no PRDs → "start with `/cobb prd`"
   - a reported bug with no fix PRD → "`/cobb prd` (it runs diagnose first when the cause is unknown)"
   - a `Status: ready` PRD with no feature branch → "`/cobb implement <prd>`"
   - feature branch ahead of base with uncommitted changes → "`/cobb commit` (review and repairs run after the final clean commit group)"
   - feature branch committed, repair loop complete, PRD has unchecked slices → "`/cobb implement <prd>` to finish the remaining slices"
   - feature branch committed, repair loop complete, PRD fully checked → "`/cobb commit finalise`"
   - feature branch committed but not yet reviewed, PRD fully checked → "`/cobb commit finalise` (it runs review and repairs first)"
   - feature branch committed but not yet reviewed, PRD incomplete or absent → "`/cobb review`"
   - `tasks/context.md` long/noisy → "`/cobb compact`"
5. Wait for the user's option number or explicit subcommand before acting.
