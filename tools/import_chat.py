#!/usr/bin/env python3
"""A small, guided entry to the existing transcript importer and profiler."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile

import mirror_profiler as profiler
import transcript_importer as importer


SUFFIXES = {'.txt', '.md', '.json', '.jsonl', '.csv', '.tsv'}
CSV_ALIASES = {
    'sender': ('sender', 'from', 'author', 'name', 'speaker', '发送者', '发言者', '发送人', '昵称'),
    'content': ('content', 'text', 'message', 'body', '内容', '消息', '消息内容', '文本'),
    'timestamp': ('timestamp', 'time', 'date', 'datetime', '时间', '发送时间', '日期'),
}


def linked(path: Path) -> bool:
    return (path.is_symlink() or bool(getattr(path, 'is_junction', lambda: False)())
            or (path.exists() and path.resolve() != path.absolute()))


def collect_files(values: list[str], recursive: bool = False) -> tuple[list[Path], int]:
    found: list[Path] = []
    skipped = 0
    for value in values:
        path = Path(value).expanduser().absolute()
        if linked(path):
            raise ValueError(f'所选路径是链接，请明确选择原文件或原目录：{path}')
        if path.is_file():
            if path.suffix.lower() not in SUFFIXES:
                raise ValueError(f'暂不能直接读取 {path.name}。请选择 TXT、Markdown、JSON、JSONL、CSV 或 TSV 导出。')
            found.append(path.resolve())
        elif path.is_dir():
            if recursive:
                import os
                candidates = []
                for directory, dirs, files in os.walk(path, followlinks=False):
                    dirs[:] = sorted(name for name in dirs if not linked(Path(directory)/name))
                    candidates.extend(Path(directory)/name for name in sorted(files))
            else:
                candidates = sorted(path.iterdir())
            for candidate in candidates:
                if not candidate.is_file() or linked(candidate):
                    continue
                if candidate.suffix.lower() in SUFFIXES:
                    found.append(candidate.resolve())
                else:
                    skipped += 1
        else:
            raise ValueError(f'找不到所选文件或目录：{path}')
    # Repeating a path is not permission to count it twice. Different files remain distinct.
    unique = list(dict.fromkeys(found))
    if not unique:
        raise ValueError('没有找到可读记录。请选择导出文件，或含 TXT/MD/JSON/JSONL/CSV/TSV 的目录。')
    return unique, skipped


def parse_csv(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:
        raise ValueError(f'{path.name} 不是 UTF-8；保留原件，另存为 UTF-8 CSV 后重试。') from None
    reader = csv.DictReader(io.StringIO(text, newline=''), delimiter='\t' if path.suffix.lower()=='.tsv' else ',', strict=True)
    headers = reader.fieldnames or []
    lowered = [name.strip().lower() for name in headers]
    if len(lowered) != len(set(lowered)):
        raise ValueError(f'{path.name} 有重复表头，请先给各列不同名称。')
    mapping = {target: next((headers[i] for i, key in enumerate(lowered) if key in aliases), None)
               for target, aliases in CSV_ALIASES.items()}
    if not mapping['sender'] or not mapping['content']:
        raise ValueError(f'{path.name} 需要“发送者/内容”或 sender/content 表头；时间列可选。请另存标准表头副本，不改原件。')
    rows = []
    try:
        for row in reader:
            if None in row:
                raise ValueError(f'{path.name} 第 {reader.line_num} 行列数超过表头，请检查引号和分隔符。')
            rows.append({key: row.get(column, '') if column else '' for key, column in mapping.items()})
    except csv.Error as error:
        raise ValueError(f'{path.name} 第 {reader.line_num} 行 CSV 无法读取：{error}') from error
    return importer.parse_json_records(rows)


def read_source(path: Path, single_author: str | None) -> list[dict]:
    messages = parse_csv(path) if path.suffix.lower() in {'.csv', '.tsv'} else importer.parse_file(path, 'auto')
    messages = importer.dedupe_messages(messages)
    if not messages:
        raise ValueError(f'{path.name} 没有可识别的文本消息，请检查导出结构；本批尚未写入。')
    if single_author and all(m['sender']=='unknown' for m in messages):
        if path.suffix.lower() not in {'.txt', '.md'}:
            raise ValueError(f'{path.name} 的说话人未知。--single-author 只用于确认单一作者的 TXT/Markdown；聊天导出请修正说话人。')
        for message in messages:
            message['sender'] = single_author
    return messages


def choose_names(counts: Counter, requested: list[str], interactive: bool) -> list[str]:
    available = [name for name in counts if name.lower() != 'unknown']
    if requested:
        names = list(dict.fromkeys(name.strip() for name in requested if name.strip()))
    elif interactive:
        answer = input('上面哪个名字是你？输入完整名称；多个名称用英文逗号隔开：').strip()
        names = [name.strip() for name in answer.split(',') if name.strip()]
    else:
        raise ValueError('还没有确认哪位是你。请加 --self-name "上面显示的本人名称"；先查看可加 --preview。无标签日记请明确加 --single-author "本人名称"。')
    if not names or any(name.lower()=='unknown' or name not in available for name in names):
        raise ValueError('本人名称未与上面的说话人准确匹配。请复制完整名称重试；未知发言不能自动归给自己。')
    for name in names:
        collision = [other for other in counts if other.lower()==name.lower() and other not in names]
        if collision:
            raise ValueError(f'说话人 {name} 与 {collision[0]} 只差大小写，现有画像器无法分开。请先在副本里用明确不同的标签。')
    return names


def write_bundle(destination: Path, sources: list[dict], names: list[str]) -> dict:
    destination = destination.expanduser().absolute()
    for part in (destination, *destination.parents):
        if linked(part):
            raise ValueError(f'输出路径经过链接，请改用明确的普通目录：{part}')
    if destination.exists():
        raise ValueError(f'输出目录已经存在，已保留原内容：{destination}。换一个 --output-dir 后重试。')
    if not destination.parent.is_dir():
        raise ValueError(f'输出的父目录不存在：{destination.parent}。请选择已有父目录下的新文件夹。')
    # Prepare every byte before touching the filesystem; preserve separate source contexts.
    staged_text: dict[str, str] = {}
    bundles = []
    source_index = []
    for index, source in enumerate(sources, 1):
        path, messages = source['path'], source['messages']
        filename = f'transcripts/{index:03d}.txt'
        staged_text[filename] = importer.render_transcript(path.name, messages)
        bundles.append(profiler.TranscriptBundle(
            source_path=destination/filename, label=f'Source {index}', source_hint=path.name,
            messages=[profiler.Message(m['timestamp'], m['sender'], m['content']) for m in messages]))
        source_index.append({'file':str(path), 'sha256':source['sha256'], 'messages':len(messages),
                             'self_messages':sum(m['sender'] in names for m in messages), 'transcript':filename})
    generated_at = datetime.now(timezone.utc).isoformat()
    # Unlike the low-level CLI, only explicitly confirmed names are self aliases here.
    aliases = {profiler.lower_text(name) for name in names}
    staged_text['profile.md'] = profiler.render_report(bundles, aliases, generated_at)
    result = {'generated_at':generated_at,'files':source_index,'self_names':names,
              'message_count':sum(len(s['messages']) for s in sources),
              'self_message_count':sum(row['self_messages'] for row in source_index),
              'scope':'Mechanical import/profile only; the model has not read or learned all messages.'}
    staged_text['summary.json'] = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
    staged_text['next-step.txt'] = (
        '请用这些导入结果创建我的水仙，让我和自己的说话方式对话。\n'
        f'结果目录：{destination}\n本人发言标签：'+ '、'.join(names)+'\n'
        '先读 summary.json 核对范围，再看 profile.md，并分批读 transcripts 里的本人原句。\n'
        '只保存抽象表达习惯，不把对方的话当作我的风格；保存镜像后直接试聊。\n'
        '请区分文件导入条数和你实际读过的样本，不宣称已经学会全部历史。\n')
    temporary = Path(tempfile.mkdtemp(prefix='.shuixian-import-', dir=destination.parent))
    try:
        for filename, content in staged_text.items():
            target = temporary/filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf-8')
        # Windows rename refuses an existing directory. A plain new destination only.
        if destination.exists() or linked(destination):
            raise ValueError(f'输出目录在处理中已出现，已保留：{destination}')
        temporary.rename(destination)
    finally:
        if temporary.exists():
            assert temporary.resolve().parent == destination.parent.resolve()
            assert temporary.name.startswith('.shuixian-import-') and not linked(temporary)
            shutil.rmtree(temporary)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description='水仙导入助手：选文件 → 确认哪位是你 → 整理成可用语料。')
    parser.add_argument('paths', nargs='*', help='选好的文件或目录；带空格请加引号，可同时给多个。')
    parser.add_argument('--self-name', action='append', default=[], help='本人在记录里的准确名称；多个别名可重复。')
    parser.add_argument('--single-author', help='明确确认无标签 TXT/Markdown 全是这位作者的文字，例如日记。')
    parser.add_argument('--preview', action='store_true', help='只看文件、说话人和条数，不写入。')
    parser.add_argument('--recursive', action='store_true', help='包括所选目录的子目录；不跟随链接。')
    parser.add_argument('--output-dir', type=Path, help='一个尚不存在的新结果目录。')
    args = parser.parse_args(argv)
    try:
        values = args.paths
        if not values and sys.stdin.isatty():
            value = input('把选好的聊天文件或文件夹路径粘贴到这里：').strip().strip('"')
            values = [value] if value else []
        if not values:
            raise ValueError('请给一个文件或目录，例如：python tools/import_chat.py "D:/我的语料"')
        paths, skipped = collect_files(values, args.recursive)
        sources, counts = [], Counter()
        for path in paths:
            data = path.read_bytes()
            messages = read_source(path, args.single_author)
            if path.read_bytes() != data:
                raise ValueError(f'读取时源文件发生变化，请等导出完成再试：{path}')
            sources.append({'path':path,'messages':messages,'sha256':hashlib.sha256(data).hexdigest()})
            counts.update(m['sender'] for m in messages)
        print(f'找到 {len(sources)} 个可读文件，共 {sum(counts.values())} 条文本消息。')
        if skipped:
            print(f'所选目录里另有 {skipped} 个不支持的文件，未读取。')
        print('说话人（请确认哪个是你）：')
        for name, count in counts.most_common():
            print(f'  {name}：{count} 条')
        if args.preview:
            print('仅预览，尚未写入任何导入结果。')
            return
        requested = args.self_name or ([args.single_author] if args.single_author else [])
        names = choose_names(counts, requested, sys.stdin.isatty())
        target = args.output_dir or Path.cwd()/('shuixian-import-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        result = write_bundle(target, sources, names)
        print(f'\n整理好了：本人 {result["self_message_count"]}/{result["message_count"]} 条。原件保留。')
        print(f'结果目录：{target.absolute()}')
        print('下一步：把 next-step.txt 发给已安装水仙的 agent，开始创建和试聊。')
        print('这里只整理了文件与统计线索，还没有生成镜像或让模型读完所有记录。')
    except (OSError, ValueError, EOFError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    main()
