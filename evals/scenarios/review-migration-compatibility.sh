# Final-version tests pass, but a destructive migration breaks overlapping old clients.
PROMPT="/cobb review main"

setup() {
  base_project
  cat > README.md <<'EOF'
# greeter storage

Release contract: old and new application versions run together until all old
readers are retired. Every intermediate schema must support the old reader.
Names move from `name` to `full_name`. Notes may be removed only after a tested
backup/recovery path exists. No backup, retirement evidence, or exception exists.
A code revert does not undo an applied schema change or recover removed notes.
Check the overlap with `python3 tools/check-compatibility.py`.
EOF
  cat > app/store.py <<'EOF'
import sqlite3


def legacy_store():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT, note TEXT)")
    db.execute("INSERT INTO people VALUES (1, 'Ada', 'retain this note')")
    return db


def legacy_names(db):
    return db.execute("SELECT name, note FROM people").fetchall()
EOF
  git add README.md app/store.py
  git commit -q -m "docs: require overlapping readers and note recovery"
  git switch -q -c feat/full-name-storage
  cat >> app/store.py <<'EOF'


def migrate(db):
    db.execute("ALTER TABLE people ADD COLUMN full_name TEXT")
    db.execute("UPDATE people SET full_name = name")
    db.execute("ALTER TABLE people DROP COLUMN name")
    db.execute("ALTER TABLE people DROP COLUMN note")


def new_names(db):
    return db.execute("SELECT full_name FROM people").fetchall()
EOF
  cat > tests/test_store.py <<'EOF'
import unittest
from app.store import legacy_store, migrate, new_names


class StoreTest(unittest.TestCase):
    def test_new_reader_after_migration(self):
        db = legacy_store()
        try:
            migrate(db)
            self.assertEqual(new_names(db), [("Ada",)])
        finally:
            db.close()
EOF
  mkdir -p tools
  cat > tools/check-compatibility.py <<'EOF'
import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.store import legacy_store, legacy_names, migrate

db = legacy_store()
try:
    migrate(db)
    try:
        rows = legacy_names(db)
    except sqlite3.OperationalError:
        print("NOT VERIFIED: the legacy reader fails after migration; its columns were dropped.")
        sys.exit(1)
    assert rows == [("Ada", "retain this note")]
    print("VERIFIED: the old reader and its data remain available.")
finally:
    db.close()
EOF
  git add -A
  git commit -q -m "feat: switch storage and drop legacy columns immediately"
}

overlap_failure_is_present() {
  local code=0 output
  output=$(python3 tools/check-compatibility.py) || code=$?
  [ "$code" -eq 1 ] && [[ "$output" == *'legacy reader fails'* ]]
}

recovery_limit_reported() {
  grep -Ei 'data|note|column|schema|backup' "$REPLY" | grep -Eiq 'cannot|does not|will not|won.t|one-way|no.*backup|backup.*required|missing.*recover|recover.*missing|not[[:space:]].*restor|restor.*[[:space:]]not([[:space:][:punct:]]|$)|recover.*unverif|unverif.*recover'
}

checks() {
  expect "review leaves source, index, and history unchanged" same_state
  expect "decision is Good to commit: No" reply_has 'Good to commit:[*_ ]*No'
  expect "deployment overlap is a numbered blocker (new rule)" blocker_mentions 'legacy|old.*reader|overlap|compatib|retir'
  expect "review reports the data or schema recovery limit (new rule)" recovery_limit_reported
  expect "new-version tests pass independently of overlap failure" python3 -m unittest -q
  expect "old reader still fails on the changed schema" overlap_failure_is_present
}
