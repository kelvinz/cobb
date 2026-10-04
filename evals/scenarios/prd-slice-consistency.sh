# No approved answer or existing code settles the two public envelope-key proposals.
PROMPT="/cobb prd Update tasks/f-06-reply-envelope.md after checking whether its slices agree."

setup() {
  base_project
  git switch -q -c feat/f-06-reply-envelope
  cat > tasks/f-06-reply-envelope.md <<'EOF'
# PRD: Reply envelopes

## 0. Summary
- **Feature ID**: f-06
- **Type**: feat
- **Status**: ready
- **Priority**: P2
- **Dependencies**: none
- **Outcome**: Developers can reuse a greeting envelope in a farewell.
- **Why now**: Two client teams want the same public result format.
- **Primary user**: Developers calling the library.
- **Success signal**: One agreed envelope shape works across both slices.
- **Unresolved blockers**: none

## 1. Problem and Evidence
The client teams supplied incompatible public-key proposals. Neither key has
been approved. There is no envelope in existing code or prior decisions that
settles which public shape the clients should receive.

## 2. Goals and Non-Goals
- G-001: Produce and consume the same reply envelope.
- NG-001: No other greeting behaviour changes.

## 3. Users, Permissions, and Scenarios
- Primary user: library callers; no access control or I/O.
- SC-001: A farewell reuses a greeting envelope.

## 4. Scope and Behaviour
- [ ] US-001: Return a greeting envelope; covers AC-001.
- [ ] US-002: Reuse the envelope in a farewell; covers AC-002.
- [ ] AC-001: Given Ada, a greeting envelope contains the exact greeting string under the agreed public key.
- [ ] AC-002: Given Ada, the farewell reads the greeting through that same key and appends " Goodbye!".
- BR-001: Producer and consumer use one public key.

## 5. Experience and State Model
Not applicable: a library without screens.

## 6. Technical Design
- Existing `app.greeting.greet(name)` returns a string; retain it unchanged.
- Add `app.envelope.make_envelope(name)` and `app.farewell.farewell(name)`.
- The new envelope is `dict[str, str]` with exactly one public key.
- There is no authoritative selection between the client proposals below.

## 7. Quality Attributes
- Security, observability, ethics: not applicable; pure library functions.
- Reliability: the producer and consumer must agree on the key.

## 8. Implementation Plan
### SL-001: Greeting envelope
- **Requirements**: US-001, AC-001, BR-001
- **Depends on**: none
- **Files/symbols**: `app/envelope.py#make_envelope`, `tests/test_envelope.py`
- **RED**: `test_greeting_envelope` expects `make_envelope("Ada") == {"text": "Hello, Ada!"}`; module missing.
- **GREEN**: return the greeting in the public `text` field.
- **REFACTOR**: none.
- **Commands**: `python3 -m unittest -v`
- **Completion evidence**: exact dictionary assertion and real function call.
- [ ] Slice complete

### SL-002: Farewell from an envelope
- **Requirements**: US-002, AC-002, BR-001
- **Depends on**: SL-001
- **Files/symbols**: `app/farewell.py#farewell`, `tests/test_farewell.py`
- **RED**: `test_farewell` expects `farewell("Ada") == "Hello, Ada! Goodbye!"`; module missing.
- **GREEN**: consume `make_envelope(name)["message"]` and append " Goodbye!"; the second team expects `message` as the public field.
- **REFACTOR**: none.
- **Commands**: `python3 -m unittest -v`
- **Completion evidence**: farewell assertion, direct call, and producer/consumer compatibility.
- [ ] Slice complete

## 9. Testing and Verification
- Confirmed seams: the two new public functions above; no mocks.
- Run `python3 -m unittest -v` and direct calls to both functions.
- AC-001 maps to SL-001; AC-002 maps to SL-002. Their key expectations disagree.

## 10. Rollout, Migration, and Recovery
- Door: two-way until clients adopt the new envelope; then the key is a public contract.
- Rollback: revert the new functions before adoption; do not change `greet`.

## 11. Analytics and Success Evaluation
Not applicable: local library.

## 12. Risks and Mitigations
- R-001: A client receives the wrong key; settle the public shape before implementation.

## 13. Decisions and Alternatives
No envelope-key decision has been approved. `text` and `message` remain proposals.

## 14. Open Questions
None recorded; the public-key choice was missed by the earlier readiness check.

## 15. Readiness Record
- Interview confirmation: all other scope confirmed; the envelope key was not settled.
- Requirement-to-slice traceability: complete, but slice contracts disagree.
- Ready rationale: originally marked ready without checking the shared contract.
EOF
  git add tasks/f-06-reply-envelope.md
  git commit -q -m "docs: record conflicting client envelope proposals"
}

contract_conflict_reported() {
  reply_has 'text' && reply_has 'message' && reply_has 'conflict|inconsisten|contract|public.*key'
}

public_contract_choice_pending() {
  local choices
  choices=$(grep -E '^[[:space:]>*-]*[0-9]+' "$REPLY")
  printf '%s\n' "$choices" | grep -iwq text &&
    printf '%s\n' "$choices" | grep -iwq message &&
    reply_has 'unresolved|unapproved|neither.*approv|not.*settled|pending|awaiting|which.*(public|contract|key)'
}

checks() {
  expect "PRD work changes no product code or tests" same_files app/ tests/
  expect "PRD work makes no commits" same_head
  expect "PRD work leaves the index unchanged" same_index
  expect "producer and consumer disagreement is reported (new rule)" contract_conflict_reported
  expect "numbered choices leave the public contract decision with the user (new rule)" public_contract_choice_pending
  expect "reply ends with canonical contract choices" canonical_choices
}
