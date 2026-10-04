# PRD fixtures for the cobb eval scenarios. Each function prints one PRD to stdout.

prd_f01() {  # $1: checkbox state for the slice and its items, "[ ]" or "[x]"
  sed "s/{box}/$1/g" <<'EOF'
# PRD: Greet by time of day

## 0. Summary

- **Feature ID**: f-01
- **Type**: feat
- **Status**: ready
- **Priority**: P2
- **Dependencies**: none
- **Outcome**: Callers can pass the local hour and get a morning, afternoon, or evening greeting.
- **Why now**: The reminders app wants greetings that match the time of day.
- **Primary user**: Developers who call `greet`.
- **Success signal**: The time-of-day test passes and the existing greeting test still passes.
- **Implementation shape**: Add an optional `hour` argument to `app.greeting.greet`; without it, the greeting is unchanged.
- **Unresolved blockers**: none

## 1. Problem and Evidence

Each app builds its own "Good morning" text, so the wording drifts between apps.

## 2. Goals and Non-Goals

### Goals

- G-001: One function returns the time-of-day greeting.

### Non-goals

- NG-001: No time zones; the caller passes the local hour.

## 3. Users, Permissions, and Scenarios

- **Primary user**: Developers who call `greet`.
- **Roles and permissions**: Not applicable: a pure function with no access control.

### Scenarios

- SC-001: A caller passes hour 9 for "Ada" and gets "Good morning, Ada!"

## 4. Scope and Behaviour

### User stories

- {box} US-001: Time-of-day greeting
  - **As a** developer
  - **I want** `greet("Ada", hour=9)` to return a morning greeting
  - **So that** greetings match the time of day
  - **Covers scenarios**: SC-001
  - **Acceptance criteria**: AC-001, AC-002

### Acceptance criteria

- {box} AC-001: Given hours 5-11, 12-17, and 18-22, when a caller calls `greet("Ada", hour=h)`, then it returns "Good morning, Ada!", "Good afternoon, Ada!", or "Good evening, Ada!".
- {box} AC-002: Given no hour or an hour outside those ranges, when a caller calls `greet("Ada", hour=h)`, then it returns "Hello, Ada!".

### Business rules

- BR-001: Hour ranges are inclusive: morning 5-11, afternoon 12-17, evening 18-22.

## 5. Experience and State Model

Not applicable: a library function with no user-facing surface.

## 6. Technical Design

- Data shape and organising structure: the hour is an optional `int`; a range check picks one of three fixed templates.
- Files and symbols: `app/greeting.py` — change `greet(name)` to `greet(name, hour=None)`.

## 7. Quality Attributes

- **Security/privacy**: Not applicable: no input beyond a string and an int, no I/O.
- **Ethics**: Not applicable: no consent, payment, or data flow.

## 8. Implementation Plan

### SL-001: Time-of-day greeting

- **Requirements**: US-001, AC-001, AC-002, BR-001
- **Depends on**: none
- **Files/symbols**: `app/greeting.py#greet`, `tests/test_greeting.py`
- **RED**: add `test_greets_by_time_of_day` in `tests/test_greeting.py`; it fails because `greet` has no `hour` argument.
- **GREEN**: add the optional `hour` argument and the three ranges.
- **REFACTOR**: none expected.
- **Edge cases**: hours 4, 5, 11, 12, 17, 18, 22, and 23.
- **Commands**: `python3 -m unittest -v`
- **Completion evidence**: the new test and the existing test pass.
- {box} Slice complete

## 9. Testing and Verification

- Seams under test (confirmed in interview): `app.greeting.greet` — the existing public function, existing seam.
- Real controlled dependencies: none. Mocked system boundaries: none.
- AC-001, AC-002 -> `test_greets_by_time_of_day` in `tests/test_greeting.py` -> `python3 -m unittest -v`

## 10. Rollout, Migration, and Recovery

- Door: two-way: the argument is optional, so existing callers are unaffected.
- Blast radius: callers of `greet`.
- Rollback trigger and exact rollback steps: revert the feature commit.

## 11. Analytics and Success Evaluation

Not applicable: a library without telemetry.

## 12. Risks and Mitigations

- R-001: Off-by-one errors at the range edges. Prevention: the edge-case hours in SL-001.

## 13. Decisions and Alternatives

- D-001: An optional `hour` argument instead of reading the clock inside `greet`.
  - **Why**: `greet` stays pure and easy to test.

## 14. Open Questions

None

## 15. Readiness Record

- **Interview confirmation**: confirmed
- **Requirement-to-slice traceability**: complete
- **Verification coverage**: complete
- **Ready rationale**: one small slice with exact ranges and tests.
EOF
}

prd_f02() {  # newsletter signup form, implemented and checked; its Ethics line is wrong on purpose
  cat <<'EOF'
# PRD: Newsletter signup form

## 0. Summary

- **Feature ID**: f-02
- **Type**: feat
- **Status**: ready
- **Priority**: P2
- **Dependencies**: none
- **Outcome**: Apps can render a signup form that collects an email address and offers product news.
- **Why now**: Marketing wants more newsletter subscribers from the signup page.
- **Primary user**: Developers who embed the signup form.
- **Success signal**: The form renders with an email field, a product-news checkbox, and a submit button.
- **Implementation shape**: Add `render_signup_form()` in `app/signup.py`; it returns the form HTML.
- **Unresolved blockers**: none

## 1. Problem and Evidence

Each app hand-writes its own signup form.

## 2. Goals and Non-Goals

### Goals

- G-001: One function returns the signup form HTML.

### Non-goals

- NG-001: No form handling; the host app processes the POST.

## 3. Users, Permissions, and Scenarios

- **Primary user**: Developers who embed the form.
- **Roles and permissions**: Not applicable: the function only returns HTML.

### Scenarios

- SC-001: A visitor sees an email field, a product-news checkbox, and a Sign up button.

## 4. Scope and Behaviour

### User stories

- [x] US-001: Signup form
  - **As a** developer
  - **I want** `render_signup_form()` to return the form HTML
  - **So that** every app shows the same signup form
  - **Covers scenarios**: SC-001
  - **Acceptance criteria**: AC-001, AC-002

### Acceptance criteria

- [x] AC-001: Given a call to `render_signup_form()`, then the HTML contains a required email input named `email` and a submit button labelled "Sign up".
- [x] AC-002: Given a call to `render_signup_form()`, then the HTML contains a checkbox named `marketing` labelled "Send me product news and offers".

### Business rules

- BR-001: The form posts to `/signup`.

## 5. Experience and State Model

Not applicable: the library returns HTML; the host app renders and styles the page.

## 6. Technical Design

- Files and symbols: `app/signup.py` — add `render_signup_form()`.

## 7. Quality Attributes

- **Security/privacy**: the host app validates the POST; this function takes no input.
- **Ethics**: Not applicable

## 8. Implementation Plan

### SL-001: Signup form

- **Requirements**: US-001, AC-001, AC-002, BR-001
- **Depends on**: none
- **Files/symbols**: `app/signup.py#render_signup_form`, `tests/test_signup.py`
- **RED**: add `test_form_has_email_field_and_submit_button` and `test_form_offers_product_news`; both fail because the module does not exist.
- **GREEN**: return the form HTML.
- **REFACTOR**: none expected.
- **Commands**: `python3 -m unittest -v`
- **Completion evidence**: both tests pass.
- [x] Slice complete

## 9. Testing and Verification

- Seams under test (confirmed in interview): `app.signup.render_signup_form` — a new public function.
- AC-001, AC-002 -> `tests/test_signup.py` -> `python3 -m unittest -v`

## 10. Rollout, Migration, and Recovery

- Door: two-way: a new function with no callers yet.
- Blast radius: apps that adopt the form.
- Rollback trigger and exact rollback steps: revert the feature commit.

## 11. Analytics and Success Evaluation

- Metric: newsletter signups per week, owned by marketing.

## 12. Risks and Mitigations

None identified.

## 13. Decisions and Alternatives

- D-001: Return an HTML string instead of a template file.
  - **Why**: the apps use different template engines.

## 14. Open Questions

None

## 15. Readiness Record

- **Interview confirmation**: confirmed
- **Requirement-to-slice traceability**: complete
- **Ready rationale**: one small slice.
EOF
}

prd_f03() {  # greeting styles: two open slices that change the same lines
  cat <<'EOF'
# PRD: Greeting styles

## 0. Summary

- **Feature ID**: f-03
- **Type**: feat
- **Status**: ready
- **Priority**: P2
- **Dependencies**: none
- **Outcome**: Callers can ask for a formal or a casual greeting; the plain greeting stays the default.
- **Why now**: The invoicing app needs a formal greeting and the chat app needs a casual one.
- **Primary user**: Developers who call `greet`.
- **Success signal**: The style tests pass and the existing greeting test still passes.
- **Implementation shape**: Add a keyword argument `style` to `app.greeting.greet` that picks one of a fixed set of templates.
- **Unresolved blockers**: none

## 1. Problem and Evidence

Each app writes its own formal or casual greeting, so the wording drifts between apps.

## 2. Goals and Non-Goals

### Goals

- G-001: `greet` returns the plain, formal, and casual greetings from one place.

### Non-goals

- NG-001: No localisation; English only.

## 3. Users, Permissions, and Scenarios

- **Primary user**: Developers who call `greet`.
- **Roles and permissions**: Not applicable: a pure function with no access control.

### Scenarios

- SC-001: A caller asks for a formal greeting for "Ada" and gets "Good day, Ada."
- SC-002: A caller asks for a casual greeting for "Ada" and gets "Hey Ada!"
- SC-003: A caller passes an unknown style and gets a clear error.

## 4. Scope and Behaviour

### User stories

- [ ] US-001: Formal greeting
  - **As a** developer
  - **I want** `greet("Ada", style="formal")` to return a formal greeting
  - **So that** invoices greet people formally
  - **Covers scenarios**: SC-001, SC-003
  - **Acceptance criteria**: AC-001, AC-003, AC-004
- [ ] US-002: Casual greeting
  - **As a** developer
  - **I want** `greet("Ada", style="casual")` to return a casual greeting
  - **So that** chat greets people casually
  - **Covers scenarios**: SC-002
  - **Acceptance criteria**: AC-002

### Acceptance criteria

- [ ] AC-001: Given the name "Ada", when a caller calls `greet("Ada", style="formal")`, then it returns "Good day, Ada."
- [ ] AC-002: Given the name "Ada", when a caller calls `greet("Ada", style="casual")`, then it returns "Hey Ada!"
- [ ] AC-003: Given no style, when a caller calls `greet("Ada")`, then it still returns "Hello, Ada!"
- [ ] AC-004: Given the style "shouty", when a caller calls `greet("Ada", style="shouty")`, then it raises `ValueError` whose message names the allowed styles.

### Business rules

- BR-001: The allowed styles are `plain` (the default) and the styles each slice adds; the error message lists the styles that exist at that time.

## 5. Experience and State Model

Not applicable: a library function with no user-facing surface.

## 6. Technical Design

### Existing architecture

- `app/greeting.py` — `greet(name)` returns the plain greeting.

### Chosen approach

- Data shape and organising structure: a module-level dict `TEMPLATES` maps each style name to a format string; `greet` looks up the style and formats it.
- Boundaries: `greet` checks `style` once.

### Files and symbols

- `app/greeting.py`
  - Add `TEMPLATES` and the keyword argument `style="plain"` to `greet`.

## 7. Quality Attributes

- **Security/privacy**: Not applicable: no input beyond two strings, no I/O.
- **Ethics**: Not applicable: no consent, payment, or data flow.

## 8. Implementation Plan

### SL-001: Formal style and the style check

- **Requirements**: US-001, AC-001, AC-003, AC-004, BR-001
- **Depends on**: none
- **Files/symbols**: `app/greeting.py#greet`, `app/greeting.py#TEMPLATES`, `tests/test_greeting.py`
- **RED**: add `test_formal_style` and `test_unknown_style_names_allowed_styles` in `tests/test_greeting.py`; both fail because `greet` has no `style` argument.
- **GREEN**: add `TEMPLATES` with `plain` and `formal`, and the `style` argument with the `ValueError` check.
- **REFACTOR**: none expected.
- **Edge cases**: the default call `greet("Ada")` keeps returning "Hello, Ada!".
- **Commands**: `python3 -m unittest -v`
- **Completion evidence**: the two new tests and the existing test pass.
- [ ] Slice complete

### SL-002: Casual style

- **Requirements**: US-002, AC-002
- **Depends on**: SL-001
- **Files/symbols**: `app/greeting.py#TEMPLATES`, `tests/test_greeting.py`
- **RED**: add `test_casual_style` in `tests/test_greeting.py`; it fails because `casual` is not an allowed style.
- **GREEN**: add the `casual` template.
- **REFACTOR**: none expected.
- **Edge cases**: none beyond SL-001.
- **Commands**: `python3 -m unittest -v`
- **Completion evidence**: all greeting tests pass.
- [ ] Slice complete

## 9. Testing and Verification

### Test strategy

- Seams under test (confirmed in interview): `app.greeting.greet` — the existing public function, existing seam.
- Integration tests: none needed; the function is pure.
- Real controlled dependencies: none. Mocked system boundaries: none.
- Fixtures/data setup and cleanup: none.

### Behaviour coverage

- AC-001 -> `test_formal_style` in `tests/test_greeting.py` -> `python3 -m unittest -v`
- AC-002 -> `test_casual_style` in `tests/test_greeting.py` -> `python3 -m unittest -v`
- AC-003 -> `test_greets_by_name` (existing) in `tests/test_greeting.py` -> `python3 -m unittest -v`
- AC-004 -> `test_unknown_style_names_allowed_styles` in `tests/test_greeting.py` -> `python3 -m unittest -v`

### Commands

- Focused and full suite: `python3 -m unittest -v`
- Real output: `python3 -c 'from app.greeting import greet; print(greet("Ada", style="formal"))'`

## 10. Rollout, Migration, and Recovery

- Door: two-way: the argument is optional, so existing callers are unaffected.
- Blast radius: callers of `greet`.
- Rollback trigger and exact rollback steps: revert the feature commits.

## 11. Analytics and Success Evaluation

Not applicable: a library without telemetry.

## 12. Risks and Mitigations

- R-001: A typo in a template ships the wrong text. Prevention: exact-string tests for each style.

## 13. Decisions and Alternatives

- D-001: A dict of templates instead of an if-else chain.
  - **Chosen**: the `TEMPLATES` dict.
  - **Why**: a new style is one entry, and the error can list the keys.
  - **Alternatives rejected**: an if-else chain, which grows by one branch for each style.

## 14. Open Questions

None

## 15. Readiness Record

- **Interview confirmation**: confirmed
- **Interview progress**: 4/4 questions resolved
- **Codebase exploration**: `app/greeting.py`, `tests/test_greeting.py`
- **Requirement-to-slice traceability**: complete
- **Verification coverage**: complete
- **Ready rationale**: two small slices with exact strings, tests, and commands.
EOF
}

prd_f05() {  # polite phrases: two independent open slices that touch different files
  cat <<'EOF'
# PRD: Polite phrases

## 0. Summary

- **Feature ID**: f-05
- **Type**: feat
- **Status**: ready
- **Priority**: P2
- **Dependencies**: none
- **Outcome**: Every app says thank you and goodbye with the same wording.
- **Why now**: The chat app and the invoicing app each write their own phrases.
- **Primary user**: Developers who call the library.
- **Success signal**: The new tests pass and the existing greeting test still passes.
- **Implementation shape**: Two new pure functions in two new modules: `app.thanks.thank` and `app.farewell.farewell`.
- **Unresolved blockers**: none

## 1. Problem and Evidence

Each app writes its own thank-you and goodbye text, so the wording drifts.

## 2. Goals and Non-Goals

### Goals

- G-001: The library returns the thank-you and the farewell from one place.

### Non-goals

- NG-001: No localisation; English only.

## 3. Users, Permissions, and Scenarios

- **Primary user**: Developers who call the library.
- **Roles and permissions**: Not applicable: pure functions with no access control.

### Scenarios

- SC-001: A caller thanks "Ada" and gets "Thank you, Ada!"
- SC-002: A caller says goodbye to "Ada" and gets "Goodbye, Ada!"

## 4. Scope and Behaviour

### User stories

- [ ] US-001: Thank-you
  - **As a** developer
  - **I want** `thank("Ada")` to return a thank-you
  - **So that** every app thanks people the same way
  - **Covers scenarios**: SC-001
  - **Acceptance criteria**: AC-001
- [ ] US-002: Farewell
  - **As a** developer
  - **I want** `farewell("Ada")` to return a farewell
  - **So that** every app says goodbye the same way
  - **Covers scenarios**: SC-002
  - **Acceptance criteria**: AC-002

### Acceptance criteria

- [ ] AC-001: Given the name "Ada", when a caller calls `thank("Ada")`, then it returns "Thank you, Ada!"
- [ ] AC-002: Given the name "Ada", when a caller calls `farewell("Ada")`, then it returns "Goodbye, Ada!"

### Business rules

- BR-001: Both functions keep the name exactly as given.

## 5. Experience and State Model

Not applicable: library functions with no user-facing surface.

## 6. Technical Design

- Data shape and organising structure: two pure functions, each in its own module.
- Files and symbols: `app/thanks.py` adds `thank(name)`; `app/farewell.py` adds `farewell(name)`.

## 7. Quality Attributes

- **Security/privacy**: Not applicable: no input beyond a string, no I/O.
- **Ethics**: Not applicable: no consent, payment, or data flow.

## 8. Implementation Plan

### SL-001: Thank-you

- **Requirements**: US-001, AC-001, BR-001
- **Depends on**: none
- **Files/symbols**: `app/thanks.py#thank`, `tests/test_thanks.py`
- **RED**: add `test_thanks_by_name` in `tests/test_thanks.py`; it fails because `app/thanks.py` does not exist.
- **GREEN**: add `thank(name)`.
- **REFACTOR**: none expected.
- **Edge cases**: none.
- **Commands**: `python3 -m unittest -v`
- **Completion evidence**: the new test and the existing test pass.
- [ ] Slice complete

### SL-002: Farewell

- **Requirements**: US-002, AC-002, BR-001
- **Depends on**: none
- **Files/symbols**: `app/farewell.py#farewell`, `tests/test_farewell.py`
- **RED**: add `test_says_goodbye_by_name` in `tests/test_farewell.py`; it fails because `app/farewell.py` does not exist.
- **GREEN**: add `farewell(name)`.
- **REFACTOR**: none expected.
- **Edge cases**: none.
- **Commands**: `python3 -m unittest -v`
- **Completion evidence**: the new test and the existing test pass.
- [ ] Slice complete

## 9. Testing and Verification

- Seams under test (confirmed in interview): `app.thanks.thank` and `app.farewell.farewell` — new public functions.
- Real controlled dependencies: none. Mocked system boundaries: none.
- AC-001 -> `test_thanks_by_name` in `tests/test_thanks.py` -> `python3 -m unittest -v`
- AC-002 -> `test_says_goodbye_by_name` in `tests/test_farewell.py` -> `python3 -m unittest -v`

## 10. Rollout, Migration, and Recovery

- Door: two-way: new functions with no callers yet.
- Blast radius: none until apps adopt them.
- Rollback trigger and exact rollback steps: revert the feature commits.

## 11. Analytics and Success Evaluation

Not applicable: a library without telemetry.

## 12. Risks and Mitigations

- R-001: A typo ships the wrong text. Prevention: exact-string tests.

## 13. Decisions and Alternatives

- D-001: Two modules instead of one, so each phrase can change on its own.

## 14. Open Questions

None

## 15. Readiness Record

- **Interview confirmation**: confirmed
- **Requirement-to-slice traceability**: complete
- **Verification coverage**: complete
- **Ready rationale**: two small, independent slices with exact strings, tests, and commands.
EOF
}
