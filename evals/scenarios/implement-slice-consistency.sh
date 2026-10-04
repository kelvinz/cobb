# Reuse the conflicting PRD fixture, but attempt implementation instead of planning.
source "$EVALS_DIR/scenarios/prd-slice-consistency.sh"
PROMPT="/cobb implement tasks/f-06-reply-envelope.md"

checks() {
  local prd=tasks/f-06-reply-envelope.md
  expect "conflicting contracts stop before product edits (new rule)" same_files app/ tests/
  expect "implementation makes no commits" same_head
  expect "implementation leaves the index unchanged" same_index
  expect "SL-001 remains open" slice_open "$prd" SL-001
  expect "SL-002 remains open" slice_open "$prd" SL-002
  expect "producer and consumer disagreement is reported (new rule)" contract_conflict_reported
  expect "conflict returns to PRD rather than picking a public contract" reply_has 'cobb prd|prd.*refin|refin.*prd|prd.*decision'
}
