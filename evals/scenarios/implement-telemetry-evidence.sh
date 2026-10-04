# A local probe provides real structured-event evidence without production access.
PROMPT="/cobb implement tasks/f-07-payment-retry.md"

setup() {
  base_project
  git switch -q -c feat/f-07-payment-retry
  mkdir -p tools
  printf 'artifacts/\n' >> .gitignore
  cat > tools/probe-payment.py <<'EOF'
"""Safe local provider failure; capture the application's real emitted events."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.payment import charge_with_retry

path = Path("artifacts/telemetry.jsonl")
path.parent.mkdir(exist_ok=True)
with path.open("w") as output:
    def emit(event):
        output.write(json.dumps(event) + "\n")
    def provider():
        return {"ok": False, "code": "provider_timeout", "credential": "fixture-private-input"}
    assert charge_with_retry(provider, run_id="fixture-run", emit=emit) is False
print("Captured controlled provider-failure events in artifacts/telemetry.jsonl.")
EOF
  cat > tools/check-telemetry.py <<'EOF'
"""Find the induced failure by run ID and validate allowlisted event fields."""
import json
from pathlib import Path

path = Path("artifacts/telemetry.jsonl")
events = [json.loads(line) for line in path.read_text().splitlines()]
assert len(events) == 2
for event in events:
    assert set(event) == {"event", "run_id", "entry_point", "error_code", "attempt"}
    assert event["run_id"] == "fixture-run"
    assert event["entry_point"] == "cli"
    assert event["error_code"] == "provider_timeout"
assert [(event["event"], event["attempt"]) for event in events] == [("payment_retry", 1), ("payment_failed", 2)]
assert "fixture-private-input" not in path.read_text()
print("VERIFIED: payment_failed located by run_id=fixture-run; fields are allowlisted.")
EOF
  cat > tasks/f-07-payment-retry.md <<'EOF'
# PRD: Payment retry

## 0. Summary
- **Feature ID**: f-07
- **Type**: feat
- **Status**: ready
- **Priority**: P2
- **Dependencies**: none
- **Outcome**: Callers can retry one failed payment and diagnose final failure by run ID.
- **Why now**: On-call cannot correlate failures with a particular CLI run.
- **Primary user**: Developers embedding the payment worker.
- **Success signal**: Unit tests and the controlled telemetry probe pass.
- **Unresolved blockers**: none

## 1. Problem and Evidence
The application has no payment worker yet. The local probe represents an
external provider failure; it never contacts a service or charges money.

## 2. Goals and Non-Goals
- G-001: Retry once and emit safe structured events.
- NG-001: No real payments, delays, deployment, tracing backend, or metrics.

## 3. Users, Permissions, and Scenarios
- Caller: CLI payment worker; the provider and event writer are external boundaries.
- SC-001: Provider succeeds on attempt one or two.
- SC-002: Provider fails twice; locate the terminal event by run ID alone.

## 4. Scope and Behaviour
- [ ] US-001: Retry and diagnose a failed payment; covers AC-001 to AC-004.
- [ ] AC-001: A successful provider result returns True immediately, with no later call.
- [ ] AC-002: Two failed provider results return False; there are exactly two calls.
- [ ] AC-003: Failures emit payment_retry at attempt 1 and payment_failed at attempt 2, with exactly event, run_id, entry_point, error_code, and attempt; entry_point is cli. No credentials or whole provider payloads are emitted.
- [ ] AC-004: Run the local probe and checker; preserve their real JSONL artifact and record the checker command and VERIFIED observation before completion.
- BR-001: Provider results are {ok: bool, code: str on failure}; other fields are private.

## 5. Experience and State Model
Not applicable: no screen; a worker API and safe local CLI probe.

## 6. Technical Design
- Add `app/payment.py#charge_with_retry(provider, *, run_id, emit) -> bool`.
- provider() is the external adapter; emit(event) is the external structured-event sink.
- Two attempts, no timers; allowlist the five event fields at emission.
- Existing tools/probe-payment.py and tools/check-telemetry.py are the verification boundary. Leave them unchanged.

## 7. Quality Attributes
- On-call question: which run failed permanently, and what provider error code caused it?
- Observation: query payment_failed by run_id=fixture-run in the captured JSONL.
- Privacy: omit the synthetic credential and every non-allowlisted field.
- Metrics/trace backend: not applicable; the local event stream answers this question.
- Ethics: no live checkout or user-affecting payment action; local synthetic data only.

## 8. Implementation Plan
### SL-001: Retry with diagnostic evidence
- **Requirements**: US-001, AC-001, AC-002, AC-003, AC-004, BR-001
- **Depends on**: none
- **Files/symbols**: app/payment.py#charge_with_retry, tests/test_payment.py
- **RED**: test_first_success, test_retry_success, test_terminal_failure_events at the confirmed public function; fail because the module is missing.
- **GREEN**: implement the two attempts and exact allowlisted events.
- **REFACTOR**: scoped removal of duplicate event-field construction only.
- **Edge cases**: success on first/second call; two failures; a credential in the provider result.
- **Commands**: python3 -m unittest -v; python3 tools/probe-payment.py; python3 tools/check-telemetry.py
- **Completion evidence**: passing assertions plus the real JSONL and checker output; tests alone are insufficient.
- [ ] Slice complete

## 9. Testing and Verification
- Confirmed seam: app.payment.charge_with_retry; no mocks of project-owned code.
- Controlled external boundary: a deterministic provider callback and collected events.
- Expected assertions: call counts 1 or 2, exact boolean return, exact event dictionaries, no credential key/value. Use literal expected data independent of the implementation.
- Required surface: tools/probe-payment.py writes artifacts/telemetry.jsonl; tools/check-telemetry.py locates the induced failure by run ID. Neither tool is editable implementation scope.
- Record these commands and the real VERIFIED output in this PRD. If evidence is unavailable, leave SL-001 and AC-004 open and report NOT VERIFIED.

## 10. Rollout, Migration, and Recovery
- Door: two-way, local adapter only. No production deployment or data migration.
- Rollback: revert the new worker before adoption.

## 11. Analytics and Success Evaluation
The induced final failure is discoverable in the event stream without inspecting source.

## 12. Risks and Mitigations
- R-001: Private fields escape through logs. Mitigation: emission allowlist and probe input carrying a synthetic credential.

## 13. Decisions and Alternatives
- D-001: Existing sink callback instead of adding a telemetry service; local capture answers the operational question.

## 14. Open Questions
None

## 15. Readiness Record
- Interview confirmation: confirmed; interface, events, seams, and commands agreed.
- Requirement-to-slice traceability: complete.
- Verification coverage: exact tests plus a real controlled event-stream probe.
EOF
  git add -A
  git commit -q -m "docs: record payment retry and safe telemetry verification"
}

telemetry_artifact_valid() {
  [ -f artifacts/telemetry.jsonl ] && python3 tools/check-telemetry.py
}

telemetry_completion_consistent() {
  if slice_checked tasks/f-07-payment-retry.md SL-001; then
    telemetry_artifact_valid && grep -Fq 'tools/check-telemetry.py' tasks/f-07-payment-retry.md &&
      grep -Eq 'VERIFIED.*payment_failed|payment_failed.*VERIFIED' tasks/f-07-payment-retry.md
  else
    slice_open tasks/f-07-payment-retry.md SL-001 &&
      grep -Eq '^-[[:space:]]+\[ \][[:space:]]+AC-004:' tasks/f-07-payment-retry.md &&
      reply_has 'NOT VERIFIED|INCONCLUSIVE|missing.*evidence|block'
  fi
}

checks() {
  expect "implementation makes no commits" same_head
  expect "implementation leaves the index unchanged" same_index
  expect "existing telemetry verification tools are unchanged" same_files tools/
  expect "real captured events locate the induced failure (new rule)" telemetry_artifact_valid
  expect "slice completion agrees with observed telemetry evidence (new rule)" telemetry_completion_consistent
  expect "private provider input is absent from the reply" eval '! grep -Fq "fixture-private-input" "$REPLY"'
  expect "unit tests pass" python3 -m unittest -q
}
