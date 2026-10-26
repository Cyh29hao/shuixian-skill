"""Real filesystem lifecycle checks; all mirror data stays in temporary dirs."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import demo_builder
import skill_writer
import version_manager


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="shuixian-lifecycle-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name) / "镜像 skills"

    def create(self, slug="test", appearance=""):
        return skill_writer.create_skill(
            base_dir=self.base, slug=slug, meta={"display_name": "测试镜像"},
            style_content="原来的说话节奏\n", mind_content="values\n",
            relationship_content="friends\n", appearance_content=appearance,
        )

    def update(self, **kwargs):
        arguments = dict(base_dir=self.base, slug="test", meta_patch={},
                         style_patch="", mind_patch="", relationship_patch="", appearance_patch="")
        arguments.update(kwargs)
        return skill_writer.update_skill(**arguments)

    @staticmethod
    def snapshot(directory):
        return {name: (directory / name).read_bytes() if (directory / name).exists() else None
                for name in skill_writer.TRACKED_FILES}

    def cli(self, tool, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / tool), *args],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

    def test_duplicate_create_preserves_current_files(self):
        directory = self.create()
        before = self.snapshot(directory)
        with self.assertRaises(FileExistsError):
            self.create()
        self.assertEqual(self.snapshot(directory), before)

    def test_intake_scope_label_is_rejected_before_creation(self):
        with self.assertRaisesRegex(ValueError, "privacy_scope -> privacy_mode"):
            skill_writer.create_skill(base_dir=self.base, slug="draft", meta={"privacy_scope":"prompt-only"},
                style_content="short", mind_content="unknown", relationship_content="family-like", appearance_content="")
        self.assertFalse(self.base.exists())

    def test_misnamed_scope_update_preserves_files_and_versions(self):
        directory = self.create()
        before = {p.relative_to(directory):p.read_bytes() for p in directory.rglob('*') if p.is_file()}
        with self.assertRaisesRegex(ValueError, "privacy_scope -> privacy_mode"):
            self.update(meta_patch={"privacy_scope":"prompt-only"})
        self.assertEqual(before, {p.relative_to(directory):p.read_bytes() for p in directory.rglob('*') if p.is_file()})

    def test_create_failure_leaves_no_partial_mirror(self):
        with mock.patch.object(skill_writer, "write_skill_files", side_effect=OSError("disk failure")):
            with self.assertRaises(OSError):
                self.create()
        self.assertEqual(list(self.base.iterdir()), [])

    def test_denied_directory_commit_has_guidance_and_preserves_existing_mirror(self):
        existing = self.create(slug="existing")
        before = self.snapshot(existing)
        with mock.patch.object(Path, "rename", side_effect=PermissionError("blocked by host")):
            with self.assertRaises(PermissionError) as caught:
                self.create(slug="new")
        message = str(caught.exception)
        self.assertIn(str(self.base / "shuixian-new"), message)
        self.assertIn("--base-dir", message)
        self.assertIn("not installed", message)
        self.assertEqual(self.snapshot(existing), before)
        self.assertEqual([p.name for p in self.base.iterdir()], ["shuixian-existing"])

    def test_update_archives_original_and_preserves_imports(self):
        directory = self.create()
        source = directory / "knowledge" / "imports" / "source.txt"
        source.write_text("private original", encoding="utf-8")
        before = self.snapshot(directory)
        _, version = self.update(style_patch="new phrase")
        self.assertEqual(version, "v2")
        self.assertEqual(self.snapshot(directory / "versions" / "v1"), before)
        self.assertEqual(source.read_text(encoding="utf-8"), "private original")
        self.assertIn("原来的说话节奏\n\nnew phrase", (directory / "style.md").read_text(encoding="utf-8"))

    def test_correction_replaces_instead_of_accumulating_contradictions(self):
        directory = self.create(appearance="outdated appearance")
        self.update(patch_mode="replace", style_patch="corrected voice", replace_sections={"appearance": ""})
        self.assertEqual((directory / "style.md").read_text(encoding="utf-8"), "corrected voice\n")
        self.assertFalse((directory / "appearance.md").exists())
        self.assertIn("outdated appearance", (directory / "versions" / "v1" / "appearance.md").read_text(encoding="utf-8"))

    def test_failed_replace_restores_original_bytes(self):
        directory = self.create()
        before = self.snapshot(directory)
        original_replace = Path.replace
        call_count = 0

        def fail_second_replace(path, target):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise PermissionError("simulated locked file")
            return original_replace(path, target)

        with mock.patch.object(Path, "replace", fail_second_replace):
            with self.assertRaises(PermissionError):
                self.update(style_patch="changed", mind_patch="changed")
        self.assertEqual(self.snapshot(directory), before)
        self.assertEqual(self.snapshot(directory / "versions" / "v1"), before)

    def test_rollback_removes_appearance_absent_from_target(self):
        directory = self.create()
        self.update(appearance_patch="new appearance")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(version_manager.rollback(directory, "test", "v1"))
        self.assertFalse((directory / "appearance.md").exists())
        self.assertNotIn("new appearance", (directory / "SKILL.md").read_text(encoding="utf-8"))

    def test_failed_rollback_restores_current_and_retains_backup(self):
        directory = self.create()
        self.update(style_patch="version two", appearance_patch="current look")
        before = self.snapshot(directory)
        original_replace = Path.replace
        call_count = 0

        def fail_second_replace(path, target):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise PermissionError("simulated rollback lock")
            return original_replace(path, target)

        with mock.patch.object(Path, "replace", fail_second_replace):
            with self.assertRaises(PermissionError):
                version_manager.rollback(directory, "test", "v1")
        self.assertEqual(self.snapshot(directory), before)
        self.assertEqual(self.snapshot(directory / "versions" / "v2-before-rollback"), before)

    def test_invalid_replacement_does_not_create_archive(self):
        directory = self.create()
        before = self.snapshot(directory)
        with self.assertRaisesRegex(ValueError, "Unknown replacement"):
            self.update(replace_sections={"typo": "wrong"})
        self.assertEqual(self.snapshot(directory), before)
        self.assertEqual(list((directory / "versions").iterdir()), [])

    def test_incomplete_archive_cannot_delete_live_files(self):
        directory = self.create()
        before = self.snapshot(directory)
        bad = directory / "versions" / "broken"
        bad.mkdir()
        (bad / "style.md").write_text("partial", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            version_manager.rollback(directory, "test", "broken")
        self.assertEqual(self.snapshot(directory), before)

    def test_malformed_archived_metadata_does_not_mutate_live_files(self):
        directory = self.create()
        self.update(style_patch="v2")
        (directory / "versions" / "v1" / "meta.json").write_text("[]", encoding="utf-8")
        before = self.snapshot(directory)
        with self.assertRaisesRegex(ValueError, "JSON object"):
            version_manager.rollback(directory, "test", "v1")
        self.assertEqual(self.snapshot(directory), before)

    def test_repeated_rollback_preserves_each_backup(self):
        directory = self.create()
        original = self.snapshot(directory)
        self.update(style_patch="version two A")
        first_v2 = self.snapshot(directory)
        with contextlib.redirect_stdout(io.StringIO()):
            version_manager.rollback(directory, "test", "v1")
        self.update(style_patch="version two B")
        second_v2 = self.snapshot(directory)
        with contextlib.redirect_stdout(io.StringIO()):
            version_manager.rollback(directory, "test", "v1")
        self.assertEqual(self.snapshot(directory / "versions" / "v1"), original)
        self.assertEqual(self.snapshot(directory / "versions" / "v2-before-rollback"), first_v2)
        self.assertEqual(self.snapshot(directory / "versions" / "v2-before-rollback-2"), second_v2)

    def test_cli_rollback_metadata_error_identifies_current_or_archive_without_writes(self):
        directory = self.create()
        self.update(style_patch="v2")
        for path in (directory / "meta.json", directory / "versions" / "v1" / "meta.json"):
            original = path.read_bytes()
            for content in ('{\n  "version": "v1",\n}\n', '[]'):
                with self.subTest(path=path, content=content):
                    try:
                        path.write_text(content, encoding="utf-8")
                        before = {str(p.relative_to(directory)): p.read_bytes()
                                  for p in directory.rglob("*") if p.is_file()}
                        result = self.cli("version_manager.py", "--action", "rollback",
                                          "--slug", "test", "--version", "v1",
                                          "--base-dir", str(self.base))
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(str(path), result.stderr)
                        self.assertIn("retry", result.stderr)
                        self.assertNotIn("Traceback", result.stderr)
                        if content.startswith("{"):
                            self.assertIn("line 3, column 1", result.stderr)
                        after = {str(p.relative_to(directory)): p.read_bytes()
                                 for p in directory.rglob("*") if p.is_file()}
                        self.assertEqual(before, after)
                    finally:
                        path.write_bytes(original)

    def test_archive_collision_keeps_both_snapshots(self):
        directory = self.create()
        first = skill_writer.archive_current_version(directory, "v1")
        (directory / "style.md").write_text("later", encoding="utf-8")
        second = skill_writer.archive_current_version(directory, "v1")
        self.assertNotEqual(first, second)
        self.assertEqual((first / "style.md").read_text(encoding="utf-8"), "原来的说话节奏\n")
        self.assertEqual((second / "style.md").read_text(encoding="utf-8"), "later")

    def test_archive_is_byte_exact(self):
        directory = self.create()
        (directory / "style.md").write_bytes(b"\xef\xbb\xbfsource\r\n")
        before = self.snapshot(directory)
        archived = skill_writer.archive_current_version(directory, "v1")
        self.assertEqual(self.snapshot(archived), before)

    def test_traversal_slugs_and_versions_are_rejected(self):
        for slug in ("../escape", "abc/../../escape", "", "hello_world", "a\\b"):
            with self.subTest(slug=slug), self.assertRaises(ValueError):
                self.create(slug=slug)
        directory = self.create()
        before = self.snapshot(directory)
        for version in ("../", "..", ".", "v1/../../outside", "v1\\..\\outside"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                version_manager.rollback(directory, "test", version)
        self.assertEqual(self.snapshot(directory), before)

    def test_non_object_metadata_has_clear_error(self):
        self.base.mkdir()
        path = self.base / "bad.json"
        path.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "JSON object"):
            skill_writer.parse_meta_json(str(path))

    def test_list_ignores_unrelated_or_malformed_metadata(self):
        self.create()
        for name, value in (("shuixian-bad", "[]"), ("shuixian-invalid", "{bad"), ("other-skill", "{}")):
            folder = self.base / name
            folder.mkdir()
            (folder / "meta.json").write_text(value, encoding="utf-8")
        self.assertEqual([item["slug"] for item in skill_writer.list_mirrors(self.base)], ["test"])

    def test_demo_force_is_versioned_and_preserves_import(self):
        directory = demo_builder.build_demo(preset_name="sweet-gender-flipped", base_dir=self.base, slug="test", name=None, force=False)
        original = self.snapshot(directory)
        source = directory / "knowledge" / "imports" / "keep.txt"
        source.write_text("keep", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            demo_builder.build_demo(preset_name="midnight-same-form", base_dir=self.base, slug="test", name=None, force=False)
        demo_builder.build_demo(preset_name="midnight-same-form", base_dir=self.base, slug="test", name=None, force=True)
        self.assertEqual(self.snapshot(directory / "versions" / "v1"), original)
        self.assertEqual(source.read_text(encoding="utf-8"), "keep")
        self.assertEqual(json.loads((directory / "meta.json").read_text(encoding="utf-8"))["version"], "v2")

    def test_cli_unchanged_demo_refresh_has_applicable_guidance_and_no_writes(self):
        directory = demo_builder.build_demo(preset_name="close-friend-same-form", base_dir=self.base,
                                            slug="test", name=None, force=False)
        source = directory / "knowledge" / "imports" / "keep.txt"
        source.write_text("公开合成素材\n", encoding="utf-8")
        before = {p.relative_to(directory).as_posix(): p.read_bytes()
                  for p in directory.rglob("*") if p.is_file()}
        result = self.cli("demo_builder.py", "--preset", "close-friend-same-form", "--force",
                          "--slug", "test", "--base-dir", str(self.base))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already matches", result.stderr)
        self.assertIn("--preset", result.stderr)
        self.assertNotIn("--*-patch", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(before, {p.relative_to(directory).as_posix(): p.read_bytes()
                                  for p in directory.rglob("*") if p.is_file()})
        self.assertEqual(list((directory / "versions").iterdir()), [])

    def test_all_presets_build(self):
        for preset_name in demo_builder.PRESETS:
            directory = demo_builder.build_demo(preset_name=preset_name, base_dir=self.base, slug=None, name=None, force=False)
            content = (directory / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("## Voice DNA", content)
            self.assertIn("Demo", content)
            self.assertIn("Source Type: authored-preset", content)
            self.assertIn("not evidence about this user", content)

    def test_generated_runtime_carries_privacy_and_correction_contracts(self):
        directory = self.create()
        content = (directory / "SKILL.md").read_text(encoding="utf-8")
        for rule in ("Access to a source is not permission", "In `style-only`", "other speakers",
                     "Never invent shared memories", "correction supersedes older inference",
                     "unless the actual update succeeded", "Do not automatically translate self-criticism"):
            with self.subTest(rule=rule):
                self.assertIn(rule, content)

    def test_cleanup_rejects_zero_retention(self):
        directory = self.create()
        self.update(style_patch="v2")
        with self.assertRaises(ValueError):
            version_manager.cleanup_old_versions(directory, max_versions=0)
        self.assertTrue((directory / "versions" / "v1").exists())

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_windows_junction_cannot_redirect_archives_or_cleanup(self):
        directory = self.create()
        before = self.snapshot(directory)
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        sentinel = outside / "keep.txt"
        sentinel.write_text("outside source", encoding="utf-8")
        versions = directory / "versions"
        versions.rmdir()
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(versions), str(outside)], capture_output=True)
        if result.returncode:
            versions.mkdir()
            self.skipTest("Windows directory junction creation unavailable")
        try:
            self.assertTrue(skill_writer.is_linked_path(versions))
            with self.assertRaisesRegex(ValueError, "linked"):
                self.update(style_patch="change")
            with self.assertRaisesRegex(ValueError, "linked"):
                version_manager.cleanup_old_versions(directory, max_versions=1)
            self.assertEqual(self.snapshot(directory), before)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "outside source")
        finally:
            # Remove the directory entry itself; never recurse into the target.
            versions.rmdir()

    def test_cli_replace_empty_file_clears_section(self):
        directory = self.create(appearance="old")
        empty = Path(self.temp.name) / "empty.md"
        empty.write_text("", encoding="utf-8")
        result = self.cli("skill_writer.py", "--action", "update", "--slug", "test", "--base-dir", str(self.base), "--appearance-patch", str(empty), "--patch-mode", "replace")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((directory / "appearance.md").exists())

    def test_cli_create_rejects_update_patch_flags_without_writes(self):
        source = Path(self.temp.name) / "initial.md"
        source.write_text("初版语气：不使用宠物称呼。\n", encoding="utf-8")
        for section in ("style", "mind", "relationship", "appearance"):
            with self.subTest(section=section):
                result = self.cli("skill_writer.py", "--action", "create",
                                  "--slug", "test", "--base-dir", str(self.base),
                                  f"--{section}-patch", str(source))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f"use --{section} instead of --{section}-patch", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(self.base.exists())
        self.assertEqual(source.read_text(encoding="utf-8"), "初版语气：不使用宠物称呼。\n")

    def test_cli_update_rejects_create_section_flags_without_writes(self):
        directory = self.create()
        source = Path(self.temp.name) / "correction.md"
        source.write_text("更正后的语气\n", encoding="utf-8")
        before = self.snapshot(directory)
        for section in ("style", "mind", "relationship", "appearance"):
            with self.subTest(section=section):
                result = self.cli("skill_writer.py", "--action", "update",
                                  "--slug", "test", "--base-dir", str(self.base),
                                  f"--{section}", str(source))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f"--{section}-patch", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(self.snapshot(directory), before)
                self.assertEqual(list((directory / "versions").iterdir()), [])

    def test_cli_no_change_update_preserves_all_files_and_archives(self):
        directory = self.create()
        self.update(mind_patch="a saved correction")
        empty = Path(self.temp.name) / "empty.md"
        empty.write_text("", encoding="utf-8")
        before = {p.relative_to(directory).as_posix(): p.read_bytes()
                  for p in directory.rglob("*") if p.is_file()}
        for flags in ([], ["--style-patch", str(empty)],
                      ["--style-patch", str(directory / "style.md"), "--patch-mode", "replace"],
                      ["--name", "测试镜像"]):
            with self.subTest(flags=flags):
                result = self.cli("skill_writer.py", "--action", "update", "--slug", "test",
                                  "--base-dir", str(self.base), *flags)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("No changes", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(before, {p.relative_to(directory).as_posix(): p.read_bytes()
                                          for p in directory.rglob("*") if p.is_file()})

    def test_cli_errors_are_actionable_and_do_not_create_base(self):
        result = self.cli("skill_writer.py", "--action", "update", "--name", "new name", "--base-dir", str(self.base))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --slug", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.base.exists())

    def test_cli_invalid_metadata_identifies_file_and_preserves_mirror(self):
        directory = self.create()
        before = self.snapshot(directory)
        source = Path(self.temp.name) / "metadata input.json"
        original_versions = sorted((directory / "versions").iterdir())
        for content in ('{\n  "display_name": "test",\n}\n', '[]'):
            source.write_text(content, encoding="utf-8")
            for action, slug in (("create", "new"), ("update", "test")):
                with self.subTest(content=content, action=action):
                    result = self.cli("skill_writer.py", "--action", action,
                                      "--slug", slug, "--base-dir", str(self.base),
                                      "--meta", str(source))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(str(source), result.stderr)
                    self.assertIn("retry", result.stderr)
                    if content.startswith("{"):
                        self.assertIn("line 3, column 1", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertEqual(self.snapshot(directory), before)
                    self.assertEqual(sorted((directory / "versions").iterdir()), original_versions)
                    self.assertFalse((self.base / "shuixian-new").exists())

    def test_cli_duplicate_demo_has_short_error(self):
        self.create()
        result = self.cli("demo_builder.py", "--preset", "sweet-gender-flipped", "--slug", "test", "--base-dir", str(self.base))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--force", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_demo_create_update_rollback_and_list(self):
        demo = self.cli("demo_builder.py", "--preset", "close-friend-same-form", "--base-dir", str(self.base), "--slug", "test")
        self.assertEqual(demo.returncode, 0, demo.stderr)
        directory = self.base / "shuixian-test"
        self.update(style_patch="new")
        restored = self.cli("version_manager.py", "--action", "rollback", "--slug", "test", "--version", "v1", "--base-dir", str(self.base))
        self.assertEqual(restored.returncode, 0, restored.stderr)
        listing = self.cli("skill_writer.py", "--action", "list", "--base-dir", str(self.base))
        self.assertEqual(listing.returncode, 0, listing.stderr)
        self.assertIn("同频朋友水仙 Demo", listing.stdout)
        self.assertIn("v1-restored", listing.stdout)
        self.assertEqual(json.loads((directory / "meta.json").read_text(encoding="utf-8"))["rollback_from"], "v2")


if __name__ == "__main__":
    unittest.main()
