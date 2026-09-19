# Dark-Pattern Check

Load under the conditions in `references/design.md`: consent, pricing or checkout, subscriptions or trials, cancellation or account deletion, notifications, data collection or sharing, AI decisions that affect users, or products for children. Treat every match as a defect, not a growth tactic.

## Severity and Handling

- **Critical:** direct harm, likely regulated. A review blocker; a PRD cannot be `ready` with one planned.
- **High:** significant harm or broken trust. A review blocker when the fix is copy or UI inside scope; otherwise a numbered decision for the user.
- **Medium and Low:** a suggestion.

When the user asks for a Critical pattern, explain the harm, recommend the honest alternative, and leave the pattern out of the options. If they insist, the PRD stays `draft` with the pattern listed as a blocker.

Flag regulatory risk, for example GDPR consent rules, FTC and EU Digital Services Act rules on deceptive design, US auto-renewal laws, and COPPA, without giving legal advice.

For each match, report the pattern, where it occurs, its severity, the harm to the user, and the honest alternative, such as opt-in and opt-out of equal effort, cancellation as easy as signup, and real deadlines only.

## Patterns

**Deceptive**

- Critical: bait and switch; trick questions such as double negatives in opt-outs; hidden costs revealed at the last step; items added to a basket without the user's action.
- High: visual misdirection that makes the business's choice look like the only choice; ads disguised as content or navigation; confirmshaming, such as "No thanks, I don't want to save money".

**Defaults and consent**

- Critical: prechecked consent; opting out much harder than opting in; a trial that rolls into paid without clear warning and easy cancellation; easy signup with hard cancellation.
- High: privacy defaults set to maximum exposure; all-or-nothing bundled consent.
- Medium: the most expensive option preselected.

**Urgency and scarcity**

- Critical: fake countdowns; invented scarcity; fake activity or social proof.
- High: time-limited offers designed to stop comparison.
- Medium: loss framing that exploits loss aversion.

**Attention and addiction**

- High: streaks that punish absence; variable rewards; re-engagement notifications that inform nothing; repeated prompts after a decline.
- Medium: infinite feeds with no stopping point; autoplay that removes the choice.

**Accessibility used against users**

- High: low contrast or small text that hides unfavourable terms; buried unsubscribe or privacy controls; deliberately inaccessible cancellation.

**Vulnerable users**

- Critical: patterns aimed at children, people in financial distress, or older users, such as obscured loan costs or deceptive purchases in children's games.

**AI-specific**

- Critical: exploiting individual psychological vulnerabilities at scale.
- High: undisclosed AI decisions about price, eligibility, or ranking; AI that invites guilt or attachment; unexplained personalisation that steers choices; features designed to make users dependent.
- Medium: simulated understanding that invites false trust.

**Common failures**

- High: no feedback after an action; destructive actions that are too easy to trigger; errors without a recovery path; mobile treated as an afterthought.
- Medium: dead ends; jargon; the same action working differently in different places; flows that rely on memory from earlier screens.
