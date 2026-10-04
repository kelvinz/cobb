"""Check literal bundled paths in cobb, including an isolated install. No agent calls."""
import os
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


BUNDLED_PATH = re.compile(
    r"(?<![\w/.#-])((?:\.\./|\./)*(?:references|scripts)/[^\s`\"'|,;()\[\]]+)"
)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
URL = re.compile(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s`<>]+")


def literal_paths(text):
    """Recognise skill-root pointers outside fences; not general Markdown syntax."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = FENCE.match(line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        for match in BUNDLED_PATH.finditer(URL.sub("", line)):
            path = match[1].removesuffix(">").split("#", 1)[0].rstrip(".:!?")
            if any(char in path for char in "<>${}*\\") or "..." in path:
                continue
            if Path(path).suffix:
                yield number, path


def validate_skill(skill_dir: Path) -> list[str]:
    """Read only the package; return deterministic source-location diagnostics."""
    try:
        root = skill_dir.resolve(strict=True)
        if not root.is_dir():
            return ["SKILL.md:1: package is not a directory"]
    except (OSError, RuntimeError):
        return ["SKILL.md:1: cannot open package"]
    errors = set()
    if not (root / "SKILL.md").is_file():
        errors.add("SKILL.md:1: missing router")

    def target_error(target):
        try:
            if not target.resolve().is_relative_to(root):
                return "escapes package"
            if not target.exists():
                return "missing file"
            if not target.is_file():
                return "not a file"
        except (OSError, RuntimeError):
            return "cannot resolve target"
        return None

    def walk_error(error):
        # Report the source directory, not its contents or an exception payload.
        directory = Path(error.filename).relative_to(root)
        errors.add(f"{directory}:1: cannot scan directory")

    for directory, folders, files in os.walk(root, onerror=walk_error, followlinks=False):
        for name in folders[:]:
            path = Path(directory) / name
            if path.is_symlink():
                reason = target_error(path)
                if reason == "not a file":
                    reason = "directory symlink is not scanned"
                errors.add(f"{path.relative_to(root)}:1: {reason}")
                folders.remove(name)
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            source = Path(directory) / name
            location = str(source.relative_to(root))
            reason = target_error(source)
            if reason:
                errors.add(f"{location}:1: {reason}")
                continue
            try:
                text = source.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.add(f"{location}:1: cannot read file")
                continue
            for number, path in literal_paths(text):
                reason = "parent traversal" if ".." in Path(path).parts else target_error(root / path)
                if reason:
                    errors.add(f"{location}:{number}: {path} — {reason}")
    return sorted(errors)


class SkillPathsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cobb-skill-test-")
        self.addCleanup(self.temp.cleanup)
        self.skill = Path(self.temp.name) / "skill"
        self.skill.mkdir()
        self.file("SKILL.md", "# Test skill\n")

    def file(self, name, content=""):
        target = self.skill / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return target

    def test_nested_references_resolve_from_skill_root(self):
        self.file("SKILL.md", "| phase | `references/menu.md` |\n")
        self.file("references/menu.md", "Read `references/design/ui.md` and `scripts/check.py`.\n")
        self.file("references/design/ui.md", "[Template](references/templates/prd.md#rules)\n")
        self.file("references/templates/prd.md")
        self.file("scripts/check.py")
        self.assertEqual(validate_skill(self.skill), [])

    def test_missing_dispatch_and_script_have_source_lines(self):
        self.file("SKILL.md", "# Skill\n| phase | `references/missing.md` |\n")
        self.file("references/menu.md", "Use `scripts/missing.sh`.\n")
        self.assertEqual(validate_skill(self.skill), [
            "SKILL.md:2: references/missing.md — missing file",
            "references/menu.md:1: scripts/missing.sh — missing file",
        ])

    def test_markdown_link_destination_and_prose_pointer(self):
        self.file("SKILL.md", "[Read](references/missing.md#rules)\nRead references/other.md.\n")
        errors = validate_skill(self.skill)
        self.assertEqual(len(errors), 2)
        self.assertIn("SKILL.md:1: references/missing.md — missing file", errors)
        self.assertIn("SKILL.md:2: references/other.md — missing file", errors)

    def test_angle_link_destination_is_checked(self):
        self.file("SKILL.md", "[Read](<references/missing.md>)\n[More](<scripts/missing.py#usage>)\n")
        self.assertEqual(validate_skill(self.skill), [
            "SKILL.md:1: references/missing.md — missing file",
            "SKILL.md:2: scripts/missing.py — missing file",
        ])

    def test_fences_keep_line_numbers(self):
        self.file("SKILL.md", "```md\n`references/example.md`\n```\n~~~text\n"
                  "scripts/example.sh\n~~~\n`references/missing.md`\n")
        self.assertEqual(validate_skill(self.skill), [
            "SKILL.md:7: references/missing.md — missing file",
        ])

    def test_long_fence_contains_shorter_fence(self):
        self.file("SKILL.md", "````markdown\n```\nreferences/example.md\n```\n````\n")
        self.assertEqual(validate_skill(self.skill), [])

    def test_project_paths_urls_directories_and_placeholders_are_ignored(self):
        self.file("SKILL.md", "`tasks/f-01-work.md` `DESIGN.md` `AGENTS.md`\n"
                  "[Docs](https://example.invalid/references/remote.md)\n"
                  "[#](#references/anchor.md) `references/design/`\n"
                  "`scripts/<name>.sh` `references/{mode}.md` `references/*.md`\n"
                  "`references/...` `scripts/$CHECK.sh`\n")
        self.assertEqual(validate_skill(self.skill), [])

    def test_directory_with_file_name_is_not_a_target_file(self):
        self.file("SKILL.md", "`references/menu.md`\n")
        (self.skill / "references/menu.md").mkdir(parents=True)
        self.assertEqual(validate_skill(self.skill), [
            "SKILL.md:1: references/menu.md — not a file",
        ])

    def test_parent_traversal_is_rejected_even_if_target_exists(self):
        self.file("SKILL.md", "`references/../SKILL.md` `../references/other.md`\n")
        errors = validate_skill(self.skill)
        self.assertEqual(len(errors), 2)
        self.assertTrue(all("parent traversal" in error for error in errors))

    def symlink(self, target, link):
        link.parent.mkdir(parents=True, exist_ok=True)
        try:
            link.symlink_to(target, target_is_directory=target.is_dir())
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlinks unavailable: {error}")

    def test_escape_target_is_not_read(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("private content")
        self.symlink(outside, self.skill / "references/outside.md")
        self.file("SKILL.md", "`references/outside.md`\n")
        original = Path.read_text

        def read_inside(path, *args, **kwargs):
            self.assertTrue(path.resolve().is_relative_to(self.skill.resolve()))
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", read_inside):
            errors = validate_skill(self.skill)
        self.assertTrue(any("escapes package" in error for error in errors))
        self.assertFalse(any("private content" in error for error in errors))

    def test_directory_symlink_escape_is_rejected(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "hidden.md").write_text("private content")
        self.symlink(outside, self.skill / "references")
        self.assertTrue(any("escapes package" in error for error in validate_skill(self.skill)))

    def test_external_script_target_is_rejected(self):
        outside = Path(self.temp.name) / "outside.sh"
        outside.write_text("private content")
        self.symlink(outside, self.skill / "scripts/check.sh")
        self.file("SKILL.md", "Run `scripts/check.sh`.\n")
        self.assertEqual(validate_skill(self.skill), [
            "SKILL.md:1: scripts/check.sh — escapes package",
        ])

    def test_internal_directory_symlink_is_not_silently_skipped(self):
        (self.skill / "real").mkdir()
        self.symlink(self.skill / "real", self.skill / "references")
        self.assertTrue(any("directory symlink" in error for error in validate_skill(self.skill)))

    def test_unreadable_markdown_is_a_failure(self):
        with patch.object(Path, "read_text", side_effect=OSError("unreadable")):
            self.assertEqual(validate_skill(self.skill), ["SKILL.md:1: cannot read file"])

    def test_missing_router_or_package_is_a_failure(self):
        (self.skill / "SKILL.md").unlink()
        self.assertEqual(validate_skill(self.skill), ["SKILL.md:1: missing router"])
        self.assertTrue(validate_skill(self.skill / "missing"))

    def test_duplicate_pointers_on_one_line_produce_one_diagnostic(self):
        self.file("SKILL.md", "Read `references/menu.md` ([menu](references/menu.md)).\n")
        self.assertEqual(validate_skill(self.skill), [
            "SKILL.md:1: references/menu.md — missing file",
        ])


class InstalledSkillTest(unittest.TestCase):
    def test_isolated_install_and_missing_target_fault(self):
        with tempfile.TemporaryDirectory(prefix="cobb-install-test-") as temp:
            package = Path(temp) / "cobb"
            shutil.copytree(ROOT / "skills/cobb", package, symlinks=True)
            self.assertEqual(validate_skill(package), [])
            (package / "references/menu.md").unlink()
            errors = validate_skill(package)
            self.assertTrue(any(error.startswith("SKILL.md:") and
                                "references/menu.md — missing file" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
