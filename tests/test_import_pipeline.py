"""Synthetic, public-safe import/profiling regression and CLI experiments."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mirror_profiler as profiler
import source_importer as sources
import transcript_importer as importer


class TranscriptDiagnosticTests(unittest.TestCase):
    def test_profiler_archive_file_conflict_preserves_existing_report(self):
        with tempfile.TemporaryDirectory(prefix="profile-conflict-", dir=ROOT / "work") as temporary:
            for part in ("mirror", "knowledge", "analysis"):
                with self.subTest(part=part):
                    case = Path(temporary) / part
                    case.mkdir()
                    source, output, mirror = case / "chat.txt", case / "report.md", case / "mirror"
                    source.write_text("[unknown-time] me: 保留原件。\n", encoding="utf-8")
                    output.write_text("已有报告\n", encoding="utf-8")
                    blocked = {"mirror": mirror, "knowledge": mirror / "knowledge",
                               "analysis": mirror / "knowledge/analysis"}[part]
                    blocked.parent.mkdir(parents=True, exist_ok=True)
                    blocked.write_text("不是目录", encoding="utf-8")
                    before = {p.relative_to(case): p.read_bytes() for p in case.rglob("*") if p.is_file()}
                    directories = {p.relative_to(case) for p in case.rglob("*") if p.is_dir()}
                    result = subprocess.run(
                        [sys.executable, "-B", "-X", "utf8", str(ROOT / "tools/mirror_profiler.py"),
                         "--input", str(source), "--output", str(output), "--archive-to", str(mirror)],
                        capture_output=True, text=True, encoding="utf-8", timeout=20,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertIn(str(blocked), result.stderr)
                    self.assertIn("--archive-to", result.stderr)
                    self.assertEqual(before, {p.relative_to(case): p.read_bytes() for p in case.rglob("*") if p.is_file()})
                    self.assertEqual(directories, {p.relative_to(case) for p in case.rglob("*") if p.is_dir()})

    def test_source_destination_file_conflict_has_no_partial_directories(self):
        with tempfile.TemporaryDirectory(prefix="source-conflict-", dir=ROOT / "work") as temporary:
            for part in ("mirror", "knowledge", "imports", "images"):
                with self.subTest(part=part):
                    case = Path(temporary) / part
                    case.mkdir()
                    source, image, mirror = case / "素材.txt", case / "image.png", case / "mirror"
                    source.write_text("保留已有素材。", encoding="utf-8")
                    image.write_bytes(b"synthetic screenshot")
                    blocked = {"mirror": mirror, "knowledge": mirror / "knowledge",
                               "imports": mirror / "knowledge/imports",
                               "images": mirror / "knowledge/images"}[part]
                    blocked.parent.mkdir(parents=True, exist_ok=True)
                    blocked.write_text("不是目录", encoding="utf-8")
                    before = {p.relative_to(case): p.read_bytes() for p in case.rglob("*") if p.is_file()}
                    directories = {p.relative_to(case) for p in case.rglob("*") if p.is_dir()}
                    result = subprocess.run(
                        [sys.executable, "-B", "-X", "utf8", str(ROOT / "tools/source_importer.py"),
                         "--input", str(image), "--input", str(source), "--skill-dir", str(mirror)],
                        capture_output=True, text=True, encoding="utf-8",
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertIn(str(blocked), result.stderr)
                    self.assertIn("--skill-dir", result.stderr)
                    self.assertEqual(before, {p.relative_to(case): p.read_bytes() for p in case.rglob("*") if p.is_file()})
                    self.assertEqual(directories, {p.relative_to(case) for p in case.rglob("*") if p.is_dir()})

    def test_archive_file_conflict_preserves_existing_transcript(self):
        with tempfile.TemporaryDirectory(prefix="archive-conflict-", dir=ROOT / "work") as temporary:
            for part in ("mirror", "knowledge", "imports"):
                with self.subTest(part=part):
                    case = Path(temporary) / part
                    case.mkdir()
                    source, output, mirror = case / "chat.txt", case / "output.txt", case / "mirror"
                    source.write_text("[unknown-time] me: 保留原件。\n", encoding="utf-8")
                    output.write_text("已有转录\n", encoding="utf-8")
                    blocked = {"mirror": mirror, "knowledge": mirror / "knowledge",
                               "imports": mirror / "knowledge/imports"}[part]
                    blocked.parent.mkdir(parents=True, exist_ok=True)
                    blocked.write_text("不是目录", encoding="utf-8")
                    before = {p.relative_to(case): p.read_bytes() for p in case.rglob("*") if p.is_file()}
                    directories = {p.relative_to(case) for p in case.rglob("*") if p.is_dir()}
                    result = subprocess.run(
                        [sys.executable, "-B", "-X", "utf8", str(ROOT / "tools/transcript_importer.py"),
                         "--input", str(source), "--output", str(output), "--archive-to", str(mirror)],
                        capture_output=True, text=True, encoding="utf-8",
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertIn(str(blocked), result.stderr)
                    self.assertIn("--archive-to", result.stderr)
                    self.assertEqual(before, {p.relative_to(case): p.read_bytes() for p in case.rglob("*") if p.is_file()})
                    self.assertEqual(directories, {p.relative_to(case) for p in case.rglob("*") if p.is_dir()})

    def test_profiler_invalid_encoding_preserves_report_and_archive(self):
        with tempfile.TemporaryDirectory(prefix="profile-encoding-", dir=ROOT / "work") as temporary:
            directory = Path(temporary)
            good = directory / "first.txt"
            good.write_text("[unknown-time] me: hello\n", encoding="utf-8")
            source = directory / "中文 聊天.txt"
            output = directory / "report.md"
            output.write_text("已有报告", encoding="utf-8")
            skill = directory / "mirror"
            archive = skill / "knowledge/analysis/existing.md"
            archive.parent.mkdir(parents=True)
            archive.write_text("已有归档", encoding="utf-8")
            for encoding in ("gbk", "utf-16"):
                with self.subTest(encoding=encoding):
                    source.write_text("[unknown-time] me: 我最近忙作业。\n", encoding=encoding)
                    before = {p.relative_to(directory): p.read_bytes()
                              for p in directory.rglob("*") if p.is_file()}
                    dirs = {p.relative_to(directory) for p in directory.rglob("*") if p.is_dir()}
                    result = subprocess.run(
                        [sys.executable, "-B", "-X", "utf8", str(ROOT / "tools/mirror_profiler.py"),
                         "--input", str(good), "--input", str(source), "--output", str(output),
                         "--archive-to", str(skill)],
                        capture_output=True, text=True, encoding="utf-8",
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(str(source), result.stderr)
                    self.assertIn("UTF-8", result.stderr)
                    self.assertIn("retry", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertEqual(before, {p.relative_to(directory): p.read_bytes()
                                            for p in directory.rglob("*") if p.is_file()})
                    self.assertEqual(dirs, {p.relative_to(directory) for p in directory.rglob("*") if p.is_dir()})

    def test_source_invalid_encoding_rejects_mixed_batch_before_writing(self):
        with tempfile.TemporaryDirectory(prefix="source-encoding-", dir=ROOT / "work") as temporary:
            directory = Path(temporary)
            source = directory / "中文 素材.txt"
            image = directory / "screenshot.png"
            image.write_bytes(b"synthetic image bytes")
            for encoding in ("utf-16", "gbk"):
                source.write_text("中文素材：先整理证据。", encoding=encoding)
                for existing in (False, True):
                    with self.subTest(encoding=encoding, existing=existing):
                        skill = directory / f"{encoding}-{existing}"
                        if existing:
                            archive = skill / "knowledge/imports/existing.md"
                            archive.parent.mkdir(parents=True)
                            archive.write_text("existing archive", encoding="utf-8")
                        before = {p.relative_to(directory): p.read_bytes()
                                  for p in directory.rglob("*") if p.is_file()}
                        dirs = {p.relative_to(directory) for p in directory.rglob("*") if p.is_dir()}
                        result = subprocess.run(
                            [sys.executable, "-B", "-X", "utf8", str(ROOT / "tools/source_importer.py"),
                             "--input", str(image), "--input", str(source), "--skill-dir", str(skill)],
                            capture_output=True, text=True, encoding="utf-8",
                        )
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(str(source), result.stderr)
                        self.assertIn("UTF-8", result.stderr)
                        self.assertIn("retry", result.stderr)
                        self.assertNotIn("Traceback", result.stderr)
                        self.assertEqual(before, {p.relative_to(directory): p.read_bytes()
                                                for p in directory.rglob("*") if p.is_file()})
                        self.assertEqual(dirs, {p.relative_to(directory) for p in directory.rglob("*") if p.is_dir()})

    def test_invalid_utf8_rejected_before_any_output_is_changed(self):
        with tempfile.TemporaryDirectory(prefix="import-encoding-", dir=ROOT / "work") as temporary:
            directory = Path(temporary)
            source = directory / "中文 聊天.txt"
            output = directory / "transcript.txt"
            output.write_text("existing transcript", encoding="utf-8")
            skill = directory / "mirror"
            archive = skill / "knowledge/imports/existing.md"
            archive.parent.mkdir(parents=True)
            archive.write_text("existing archive", encoding="utf-8")
            text = "[2026-10-25 20:00:00] 小林: 我最近忙作业。\n"
            for encoding in ("utf-16", "gbk"):
                source.write_text(text, encoding=encoding)
                for fmt in ("auto", "text"):
                    with self.subTest(encoding=encoding, format=fmt):
                        before = {p.relative_to(directory): p.read_bytes()
                                  for p in directory.rglob("*") if p.is_file()}
                        result = subprocess.run(
                            [sys.executable, "-B", "-X", "utf8", str(ROOT / "tools/transcript_importer.py"),
                             "--input", str(source), "--format", fmt, "--output", str(output),
                             "--archive-to", str(skill)],
                            capture_output=True, text=True, encoding="utf-8",
                        )
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(str(source), result.stderr)
                        self.assertIn("UTF-8", result.stderr)
                        self.assertIn("retry", result.stderr)
                        self.assertNotIn("Traceback", result.stderr)
                        self.assertEqual(before, {p.relative_to(directory): p.read_bytes()
                                                for p in directory.rglob("*") if p.is_file()})

    def test_batch_parse_error_identifies_input_and_preserves_artifacts(self):
        with tempfile.TemporaryDirectory(prefix="import-diagnostic-", dir=ROOT / "work") as temporary:
            directory = Path(temporary)
            good = directory / "first" / "export.json"
            good.parent.mkdir()
            good.write_text('[{"role":"user","text":"valid synthetic message"}]', encoding="utf-8")
            output = directory / "transcript.txt"
            output.write_text("existing transcript", encoding="utf-8")
            skill = directory / "mirror"
            archive = skill / "knowledge" / "imports" / "existing.md"
            archive.parent.mkdir(parents=True)
            archive.write_text("existing archive", encoding="utf-8")
            for suffix, content, line in [("json", "{broken}", 1), ("jsonl", '{}\n{broken}', 2)]:
                bad = directory / "second" / ("export." + suffix)
                bad.parent.mkdir(exist_ok=True)
                bad.write_text(content, encoding="utf-8")
                for fmt in ("auto", suffix):
                    with self.subTest(suffix=suffix, format=fmt):
                        result = subprocess.run(
                            [sys.executable, "-X", "utf8", str(ROOT / "tools/transcript_importer.py"),
                             "--input", str(good), "--input", str(bad), "--format", fmt,
                             "--output", str(output), "--archive-to", str(skill)],
                            capture_output=True, text=True, encoding="utf-8",
                        )
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(str(bad), result.stderr)
                        self.assertIn(f"line {line}, column 2", result.stderr)
                        self.assertIn("retry", result.stderr)
                        self.assertNotIn("Traceback", result.stderr)
                        self.assertEqual(output.read_text(encoding="utf-8"), "existing transcript")
                        self.assertEqual(archive.read_text(encoding="utf-8"), "existing archive")
                        self.assertEqual(list(archive.parent.iterdir()), [archive])


class ImportPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="shuixian-import-")
        self.directory = Path(self.temp.name) / "中文 测试"
        self.directory.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, text):
        path = self.directory / name
        path.write_text(text, encoding="utf-8")
        return path

    def cli(self, tool, *arguments):
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / tool), *map(str, arguments)],
            capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

    def test_unicode_jsonl_to_archive_to_profile_cli(self):
        records = [
            {"role": "user", "timestamp": "2026-10-25T10:30:01+08:00", "content": "我最近忙作业。\n保留这行 🌼"},
            {"role": "assistant", "timestamp": "2026-10-25T02:31:00Z", "content": [{"type": "text", "text": "慢慢来，我在。"}]},
        ]
        source = self.write("合成.jsonl", "\n".join(json.dumps(row, ensure_ascii=False) for row in records))
        transcript = self.directory / "transcript.txt"
        skill = self.directory / "mirror"
        imported = self.cli("transcript_importer.py", "--input", source, "--output", transcript, "--archive-to", skill)
        self.assertEqual(imported.returncode, 0, imported.stderr)
        self.assertIn("Parsed 2 messages", imported.stdout)
        self.assertIn("[2026-10-25 02:30:01] user: 我最近忙作业。", transcript.read_text(encoding="utf-8"))
        report = self.directory / "profile.md"
        profiled = self.cli("mirror_profiler.py", "--skill-dir", skill, "--self-name", "user", "--output", report)
        self.assertEqual(profiled.returncode, 0, profiled.stderr)
        result = report.read_text(encoding="utf-8")
        self.assertIn("Identified User Messages: 1", result)
        self.assertIn("我最近忙作业。 保留这行 🌼", result)
        self.assertIn("core_alignment: unconfirmed", result)

    def test_openai_selected_branch_and_text_blocks(self):
        payload = [{"mapping": {
            "root": {"parent": None, "message": None},
            "u": {"parent": "root", "message": {"author": {"role": "user"}, "create_time": 1000, "content": {"parts": ["你好"]}}},
            "old": {"parent": "u", "message": {"author": {"role": "assistant"}, "content": {"parts": ["old branch"]}}},
            "new": {"parent": "u", "message": {"author": {"role": "assistant"}, "content": {"parts": ["new branch"]}}},
        }, "current_node": "new"}]
        parsed = importer.parse_json_records(payload)
        self.assertEqual([(item["sender"], item["content"]) for item in parsed], [("user", "你好"), ("assistant", "new branch")])

    def test_nested_telegram_and_anthropic_blocks(self):
        payload = {"chats": {"list": [{"messages": [
            {"from": "小明", "date": "2026-10-25T10:00:00", "text": ["你好", {"type": "bold", "text": "世界"}, {"type": "photo", "file": "private.png"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "hello"}]},
            {"role": "assistant", "content": {"type": "image", "path": "not-prose.png"}},
        ]}]}}
        parsed = importer.parse_json_records(payload)
        self.assertEqual([item["content"] for item in parsed], ["你好世界", "hello"])
        self.assertEqual(parsed[0]["sender"], "小明")

    def test_epoch_and_iso_timestamps_can_sort_together(self):
        parsed = importer.parse_json_records([
            {"role": "me", "timestamp": "2026-10-25T01:00:00Z", "text": "first"},
            {"role": "me", "timestamp": 1792893600000, "text": "second"},
            {"role": "me", "timestamp": "bad", "text": "unknown"},
        ])
        self.assertEqual(len(importer.dedupe_messages(parsed)), 3)
        self.assertEqual(parsed[0]["timestamp"].hour, 1)

    def test_empty_and_malformed_cli_preserve_existing_output(self):
        output = self.write("existing.txt", "keep this")
        for filename, content, expected in [
            ("empty.json", "[]", "No text messages"),
            ("broken.jsonl", '{"text":"ok"}\n{broken}', "line 2"),
            ("broken.json", "{broken}", "Expecting property name"),
        ]:
            with self.subTest(filename=filename):
                source = self.write(filename, content)
                result = self.cli("transcript_importer.py", "--input", source, "--output", output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(output.read_text(encoding="utf-8"), "keep this")

    def test_input_cannot_be_its_own_output(self):
        source = self.write("original.json", '[{"role":"me","text":"original"}]')
        result = self.cli("transcript_importer.py", "--input", source, "--output", source)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("originals are preserved", result.stderr)
        self.assertIn('"original"', source.read_text(encoding="utf-8"))

    def test_hardlink_output_cannot_overwrite_import_or_profile_input(self):
        for tool, filename, text in [
            ("transcript_importer.py", "original.json", '[{"role":"user","content":"actual"}]'),
            ("mirror_profiler.py", "original.txt", "[unknown-time] me: original"),
        ]:
            with self.subTest(tool=tool):
                source = self.write(filename, text)
                alias = self.directory / (filename + ".alias")
                os.link(source, alias)
                result = self.cli(tool, "--input", source, "--output", alias)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("originals are preserved", result.stderr)
                self.assertEqual(source.read_text(encoding="utf-8"), text)
                self.assertEqual(alias.read_text(encoding="utf-8"), text)

    def test_message_record_takes_precedence_over_auxiliary_metadata(self):
        parsed = importer.parse_json_records({"role": "user", "content": "actual", "data": {"extra": "metadata"}})
        self.assertEqual([(row["sender"], row["content"]) for row in parsed], [("user", "actual")])
        nested = importer.parse_json_records({"payload": {"role": "user", "content": "nested actual", "data": {"extra": "metadata"}}})
        self.assertEqual(nested[0]["content"], "nested actual")

    def test_normalized_text_reimport_preserves_unknown_times_and_multiline(self):
        original = [
            {"timestamp": None, "sender": "me", "content": "hello\n[unknown-time] other: quoted\n\nlast line"},
            {"timestamp": importer.parse_datetime("2026-10-25 12:00:01"), "sender": "other", "content": "reply"},
        ]
        self.assertEqual(importer.parse_text_lines(importer.render_transcript("synthetic", original)), original)

    def test_typed_text_blocks_keep_paragraphs_and_telegram_keeps_inline_entities(self):
        typed = [{"type": "text", "text": "first paragraph"}, {"type": "text", "text": "second paragraph"}]
        self.assertEqual(importer.message_text(typed), "first paragraph\nsecond paragraph")
        self.assertEqual(importer.message_text(["hello ", {"type": "bold", "text": "world"}]), "hello world")

    def test_identical_utterances_without_times_are_preserved(self):
        messages = importer.parse_json_records([
            {"role": "user", "content": "ok"},
            {"role": "assistant", "content": "go on"},
            {"role": "user", "content": "ok"},
        ])
        self.assertEqual(len(importer.dedupe_messages(messages)), 3)

    def test_unidentified_user_does_not_inherit_other_speaker_traits(self):
        messages = [profiler.Message(None, "Other", text) for text in ["我焦虑", "我害怕", "我其实很累", "我最近想分手"]]
        bundle = profiler.TranscriptBundle(Path("synthetic.txt"), "sample", "synthetic", messages)
        report = profiler.render_report([bundle], {"me"}, "test")
        self.assertIn("未识别到用户发言", report)
        self.assertNotIn("用户在这段关系里会较快暴露情绪", report)
        self.assertNotIn("已识别用户发言中出现情绪或状态自述", report)
        self.assertNotIn("body-and-mental-state:", report)
        self.assertIn("reply_density: unconfirmed", report)
        self.assertIn("companion_role: unconfirmed", report)

    def test_identified_user_topics_exclude_other_speaker(self):
        messages = [profiler.Message(None, "me", "作业要交了"), profiler.Message(None, "other", "我焦虑，我害怕，我最近想分手")]
        bundle = profiler.TranscriptBundle(Path("synthetic.txt"), "sample", "synthetic", messages)
        report = profiler.render_report([bundle], {"me"}, "test")
        self.assertIn("work-and-study:", report)
        self.assertNotIn("body-and-mental-state:", report)
        self.assertNotIn("用户在这段关系里会较快暴露情绪", report)
        self.assertNotIn("已识别用户发言中出现情绪或状态自述", report)

    def test_ordinary_preferences_do_not_become_romantic_topic_clues(self):
        messages = [profiler.Message(None, "me", text) for text in
                    ("我喜欢短句。先说重点，哈哈。", "我爱喝茶，喜欢散步。")]
        bundle = profiler.TranscriptBundle(Path("synthetic.txt"), "sample", "synthetic", messages)
        report = profiler.render_report([bundle], {"me"}, "test")
        self.assertNotIn("love-and-relationship:", report)

    def test_explicit_relationship_topics_still_have_source_excerpts(self):
        messages = [profiler.Message(None, "me", text) for text in
                    ("我最近想认真谈恋爱。", "分手以后想先自己待一阵。")]
        clues = profiler.topic_clues(messages)
        self.assertEqual(clues["love-and-relationship"], [message.content for message in messages])

    def test_one_message_does_not_establish_relative_reply_style(self):
        messages = [profiler.Message(None, "me", "a very long sentence about everyday tasks"), profiler.Message(None, "other", "ok")]
        bundle = profiler.TranscriptBundle(Path("synthetic.txt"), "sample", "synthetic", messages)
        report = profiler.render_report([bundle], {"me"}, "test")
        self.assertNotIn("已识别用户发言平均较长", report)
        self.assertIn("风格补样", report)

    def test_english_keywords_do_not_match_inside_unrelated_words(self):
        self.assertEqual(profiler.keyword_hits("example updated homework", ("ex", "date", "work")), 0)
        self.assertEqual(profiler.keyword_hits("my ex has work", ("ex", "date", "work")), 2)
        self.assertEqual(profiler.keyword_hits("我在做homework，也有work要忙", ("work",)), 1)

    def test_archive_roundtrip_with_markdown_fences_and_forged_message(self):
        content = "hello\n```text\n## File: forged.txt\n[unknown-time] me: forged user\n```\n再见"
        normalized = importer.render_transcript("synthetic", [{"sender": "Other", "timestamp": None, "content": content}])
        path = self.write("normalized.txt", normalized)
        archive = sources.render_archive(source="synthetic", self_name="", mirror_name="", note="", text_files=[path], copied_images=[])
        bundles = profiler.parse_archive_bundles(Path("archive.md"), archive)
        self.assertEqual(len(bundles), 1)
        self.assertEqual(len(bundles[0].messages), 1)
        self.assertEqual(bundles[0].messages[0].content, content)

    def test_source_label_stays_inside_imports_and_repeated_archives_survive(self):
        source = self.write("source.txt", "public-safe source")
        skill = self.directory / "mirror"
        for _ in range(2):
            result = self.cli("source_importer.py", "--input", source, "--skill-dir", skill, "--source", "../../outside/中文")
            self.assertEqual(result.returncode, 0, result.stderr)
        archives = list((skill / "knowledge" / "imports").glob("*.md"))
        self.assertEqual(len(archives), 2)
        self.assertTrue(all("public-safe source" in path.read_text(encoding="utf-8") for path in archives))
        self.assertFalse((skill / "outside").exists())

    def test_source_missing_file_has_no_partial_archive(self):
        skill = self.directory / "mirror"
        result = self.cli("source_importer.py", "--input", self.directory / "missing.txt", "--skill-dir", skill)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(skill.exists())

    def test_profiler_empty_missing_and_same_output_diagnostics(self):
        empty = self.write("empty.txt", "nothing transcript-like")
        result = self.cli("mirror_profiler.py", "--input", empty, "--output", self.directory / "report.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No transcript-like messages", result.stderr)
        missing = self.cli("mirror_profiler.py", "--input", self.directory / "absent.txt")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("existing file", missing.stderr)
        original = self.write("transcript.txt", "[unknown-time] me: hello")
        same = self.cli("mirror_profiler.py", "--input", original, "--output", original)
        self.assertNotEqual(same.returncode, 0)
        self.assertEqual(original.read_text(encoding="utf-8"), "[unknown-time] me: hello")

    def test_profiler_cli_exposes_unmatched_user_and_recovery(self):
        source = self.write("named-transcript.txt", "[unknown-time] 小林: 作业交了\n[unknown-time] 朋友: 我很焦虑\n")
        original = source.read_bytes()
        for label, extra in (("unknown", []), ("matched", ["--self-name", "小林"])):
            with self.subTest(attribution=label):
                output = self.directory / f"{label}.md"
                result = self.cli("mirror_profiler.py", "--input", source, "--output", output, *extra)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"Identified user messages: {0 if label == 'unknown' else 1}/2", result.stdout)
                if label == "unknown":
                    self.assertIn("No user sender labels matched", result.stderr)
                    self.assertIn("--self-name", result.stderr)
                    self.assertIn("reply_density: unconfirmed", output.read_text(encoding="utf-8"))
                else:
                    self.assertNotIn("Warning:", result.stderr)
                    self.assertIn("work-and-study:", output.read_text(encoding="utf-8"))
                self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
