#!/usr/bin/env python3
"""
exif_overwrite.py

Manually run to conditionally overwrite EXIF tags without touching other metadata.

Usage:
    python tools/exif_overwrite.py --config tools/exif_overwrite_config.json [--dry-run] [paths...]

Config file (JSON) structure example is provided in tools/exif_overwrite_config.json.

Notes:
 - The `files` field in a rule is optional. If omitted, the script will by default
     recursively scan `content/` for JPEG files (case variants of `.jpg`/`.jpeg`).
 - If `files` is present it may be a string or a list of glob patterns. CLI `paths`
     override rule `files` entirely.

Behavior:
 - For each rule in config, files matching the rule's `files` glob (or the default
     content/ patterns) are evaluated.
 - If the rule's match conditions are satisfied (AND/OR, equality/contains/regex),
     the specified target tags are overwritten with provided values.
 - Other EXIF tags and other metadata are preserved.
 - Creates backups by default unless --no-backup is passed.

Requires: piexif (recommended). If not installed, the script will exit with instructions.
"""
import argparse
import json
import sys
import shutil
from pathlib import Path
import fnmatch
import re

try:
    import piexif
except Exception:
    print("piexif is required. Install with: pip install piexif", file=sys.stderr)
    sys.exit(1)


def normalize_ifd_name(name: str) -> str:
    n = name.lower()
    if n in ("0th", "ifd0", "ifd_0"):
        return "0th"
    if n in ("exif", "exififd", "ifdexif"):
        return "Exif"
    if n in ("gps", "gpsifd"):
        return "GPS"
    if n in ("1st", "ifd1"):
        return "1st"
    if n in ("interop", "interoperability"):
        return "Interop"
    return name


def find_tag(ifds, label: str):
    """Find tag by label. Label can be 'IFD:TagName' or 'TagName'. Returns (ifd_name, tag_id) or (None,None)."""
    if ':' in label:
        ifd_part, tag_name = label.split(':', 1)
        ifd = normalize_ifd_name(ifd_part)
        for tag_id, info in piexif.TAGS.get(ifd, {}).items():
            if info.get('name') == tag_name:
                return ifd, tag_id
        return None, None
    # search across IFDs
    for ifd in ('0th', 'Exif', 'GPS', 'Interop', '1st'):
        for tag_id, info in piexif.TAGS.get(ifd, {}).items():
            if info.get('name') == label:
                return ifd, tag_id
    return None, None


def get_tag_value(ifds, ifd_name, tag_id):
    data = ifds.get(ifd_name, {})
    val = data.get(tag_id)
    if val is None:
        return None
    # bytes -> try decode
    if isinstance(val, bytes):
        try:
            return val.decode('utf-8', errors='ignore')
        except Exception:
            return val
    return val


def set_tag_value(ifds, ifd_name, tag_id, value):
    # Ensure ifd exists
    if ifd_name not in ifds:
        ifds[ifd_name] = {}
    # If value is a string that encodes a rational like "(0, 1)" or "0/1",
    # convert to a numeric tuple so piexif writes the proper rational type.
    if isinstance(value, str):
        # try to parse tuple form '(num, num)'
        m = re.match(r"^\(\s*(\d+)\s*,\s*(\d+)\s*\)$", value)
        if m:
            ifds[ifd_name][tag_id] = (int(m.group(1)), int(m.group(2)))
            return
        # try to parse 'num/num' form
        m = re.match(r"^(\d+)\s*/\s*(\d+)$", value)
        if m:
            ifds[ifd_name][tag_id] = (int(m.group(1)), int(m.group(2)))
            return
        # try numeric integer
        if value.isdigit():
            ifds[ifd_name][tag_id] = int(value)
            return
        # otherwise encode strings to bytes as piexif expects bytes for ASCII fields
        ifds[ifd_name][tag_id] = value.encode('utf-8')
    else:
        ifds[ifd_name][tag_id] = value


def match_conditions(ifds, conds, mode='and'):
    results = []
    for c in conds:
        label = c.get('label')
        op = c.get('op', 'eq')
        target = c.get('value')
        ifd, tid = find_tag(ifds, label)
        val = None
        if ifd and tid:
            val = get_tag_value(ifds, ifd, tid)
        if val is None:
            val = ''
        sval = str(val)
        if op == 'eq':
            res = sval == str(target)
        elif op == 'ne':
            res = sval != str(target)
        elif op == 'contains':
            res = str(target) in sval
        elif op == 'regex':
            res = re.search(str(target), sval) is not None
        else:
            res = False
        results.append(bool(res))
    if mode == 'and':
        return all(results)
    return any(results)


def process_file(path: Path, rule, dry_run=False, backup=True):
    # load exif
    try:
        exif_dict = piexif.load(str(path))
    except Exception as e:
        print(f"[SKIP] {path}: cannot read EXIF ({e})")
        return

    match_cfg = rule.get('match', {})
    mode = match_cfg.get('mode', 'and')
    conds = match_cfg.get('conditions', [])
    if conds:
        ok = match_conditions(exif_dict, conds, mode=mode)
    else:
        ok = True

    if not ok:
        print(f"[NO MATCH] {path}")
        return

    # apply sets
    sets = rule.get('set', [])
    if not sets:
        print(f"[NO ACTION] {path}: rule matched but no 'set' entries")
        return

    if dry_run:
        print(f"[DRY] {path}: would modify:")
    else:
        if backup:
            bak = str(path) + '.bak'
            shutil.copy2(path, bak)
            print(f"[BACKUP] {path} -> {bak}")

    changed = False
    for s in sets:
        label = s.get('label')
        newval = s.get('value')
        ifd, tid = find_tag(exif_dict, label)
        if not ifd:
            print(f"[WARN] {path}: tag {label} not found; skipping")
            continue
        old = get_tag_value(exif_dict, ifd, tid)
        if str(old) == str(newval):
            if dry_run:
                print(f"  - {label}: unchanged (would set same value)")
            continue
        if dry_run:
            print(f"  - {label}: '{old}' -> '{newval}'")
            changed = True
        else:
            set_tag_value(exif_dict, ifd, tid, newval)
            print(f"[MOD] {path}: {label}: '{old}' -> '{newval}'")
            changed = True

    if not dry_run and changed:
        try:
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, str(path))
            print(f"[SAVED] {path}")
        except Exception as e:
            print(f"[ERROR] {path}: failed to write EXIF ({e})")


def expand_files(patterns, cwd=Path('.')):
    files = []
    for p in patterns:
        p = str(p)
        if '*' in p or '?' in p or '[' in p:
            for f in cwd.rglob(p):
                if f.is_file():
                    files.append(f)
        else:
            f = cwd / p
            if f.exists():
                if f.is_file():
                    files.append(f)
                else:
                    for g in f.rglob('*'):
                        if g.is_file():
                            files.append(g)
    return files


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', '-c', default='tools/exif_overwrite_config.json')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--no-backup', action='store_true')
    p.add_argument('paths', nargs='*', help='Optional extra file globs to process')
    args = p.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"Config not found: {cfg_path}", file=sys.stderr)
        sys.exit(2)
    cfg = json.loads(cfg_path.read_text(encoding='utf-8'))

    rules = cfg.get('rules', [])
    cwd = Path('.')
    # default patterns: recursively search content/ for common JPEG extensions
    default_patterns = [
        'content/**/*.jpg',
        'content/**/*.jpeg',
        'content/**/*.JPG',
        'content/**/*.JPEG',
    ]

    for rule in rules:
        # CLI paths override everything
        if args.paths:
            files = args.paths
        else:
            files = rule.get('files') or default_patterns

        # allow single-string entry in config
        if isinstance(files, str):
            files = [files]

        targets = expand_files(files, cwd=cwd)
        if not targets:
            print(f"[INFO] No targets found for rule '{rule.get('name', '<unnamed>')}'")
        for t in targets:
            process_file(t, rule, dry_run=args.dry_run, backup=not args.no_backup)


if __name__ == '__main__':
    main()
