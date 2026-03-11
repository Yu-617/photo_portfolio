#!/usr/bin/env python3
"""
Simple runner to invoke the tools in `tools/` in a defined order.

Usage:
  python run_tool.py [--dry-run] [--no-backup]

This script will run the following scripts (in this order):
 - tools/csv_to_data.py
 - tools/exif_overwrite.py
 - tools/optimize_images.py
 - tools/delete_gps.py

It forwards `--dry-run` and `--no-backup` where those options are supported.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None):
	print(f"\n--- RUN: {' '.join(cmd)}")
	res = subprocess.run(cmd, cwd=cwd)
	print(f"--- EXIT {res.returncode}: {' '.join(cmd)}\n")
	return res.returncode


def main():
	p = argparse.ArgumentParser(description='Run project tools in sequence')
	p.add_argument('--dry-run', action='store_true', help='Pass --dry-run to supported tools')
	p.add_argument('--no-backup', action='store_true', help='Pass --no-backup to supported tools')
	p.add_argument('--tools-dir', type=Path, default=Path('tools'), help='Path to tools directory')
	args = p.parse_args()

	tools_dir = args.tools_dir
	if not tools_dir.exists():
		print('tools directory not found:', tools_dir)
		sys.exit(2)

	failures = []

	# 1) csv_to_data.py (if exists)
	csv_script = tools_dir / 'csv_to_data.py'
	if csv_script.exists():
		cmd = [sys.executable, str(csv_script)]
		if args.dry_run:
			cmd.append('--dry-run')
		rc = run(cmd)
		if rc != 0:
			failures.append(('csv_to_data.py', rc))
	else:
		print('Skipping csv_to_data.py (not found)')

	# 2) exif_overwrite.py
	exif_script = tools_dir / 'exif_overwrite.py'
	if exif_script.exists():
		cmd = [sys.executable, str(exif_script), '--config', str(tools_dir / 'exif_overwrite_config.json')]
		if args.dry_run:
			cmd.append('--dry-run')
		if args.no_backup:
			cmd.append('--no-backup')
		rc = run(cmd)
		if rc != 0:
			failures.append(('exif_overwrite.py', rc))
	else:
		print('Skipping exif_overwrite.py (not found)')

	# 3) optimize_images.py
	opt_script = tools_dir / 'optimize_images.py'
	if opt_script.exists():
		cmd = [sys.executable, str(opt_script), 'content/gallery']
		# sensible defaults: keep backup unless user passed --no-backup
		if args.dry_run:
			cmd.append('--dry-run')
		if not args.no_backup:
			cmd.append('--backup')
		rc = run(cmd)
		if rc != 0:
			failures.append(('optimize_images.py', rc))
	else:
		print('Skipping optimize_images.py (not found)')

	# 4) delete_gps.py
	del_script = tools_dir / 'delete_gps.py'
	if del_script.exists():
		cmd = [sys.executable, str(del_script), 'content/gallery']
		if args.dry_run:
			cmd.append('--dry-run')
		rc = run(cmd)
		if rc != 0:
			failures.append(('delete_gps.py', rc))
	else:
		print('Skipping delete_gps.py (not found)')

	if failures:
		print('Finished with failures:')
		for name, code in failures:
			print(f' - {name}: exit {code}')
		sys.exit(1)

	print('All tools finished successfully')


if __name__ == '__main__':
	main()

