#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge i18n_missing.json and translation JSON into i18n.py.

Usage:
  python tools/i18n_merge.py --translations path/to/translations.json
Optional:
  --missing path/to/i18n_missing.json
  --i18n path/to/i18n.py
"""

import argparse
import json
import os
import re
import sys


def has_cjk(text):
	for ch in text:
		if "\u4e00" <= ch <= "\u9fff":
			return True
	return False


def load_json(path):
	with open(path, "r", encoding="utf-8") as handle:
		return json.load(handle)


def find_zh_cn_block(lines):
	start = None
	brace_depth = 0
	for i, line in enumerate(lines):
		if start is None:
			if '"zh_CN"' in line and "{" in line:
				start = i
				brace_depth = line.count("{") - line.count("}")
				continue
		else:
			brace_depth += line.count("{") - line.count("}")
			if brace_depth == 0:
				return start, i
	return None, None


def detect_indent(lines, start, end):
	for i in range(start + 1, end):
		match = re.match(r'^(\s*)"[^"]+"\s*:', lines[i])
		if match:
			return match.group(1)
	return "\t\t\t\t"


def ensure_trailing_comma(lines, start, end, indent):
	for i in range(end - 1, start, -1):
		line = lines[i].rstrip("\n")
		if not line.strip():
			continue
		if line.lstrip().startswith("#"):
			continue
		if line.strip().startswith("}"):
			continue
		if line.startswith(indent) and ":" in line:
			if not line.rstrip().endswith(","):
				lines[i] = line + ",\n"
			return


def build_entry_line(indent, key, value):
	key_json = json.dumps(key, ensure_ascii=False)
	val_json = json.dumps(value, ensure_ascii=False)
	return f"{indent}{key_json}: {val_json},\n"


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--translations", required=True)
	parser.add_argument("--missing", default="i18n_missing.json")
	parser.add_argument("--i18n", default="i18n.py")
	args = parser.parse_args()

	translations = load_json(args.translations)
	if not isinstance(translations, dict):
		raise SystemExit("translations JSON must be an object {key: value}")

	missing_keys = None
	if os.path.exists(args.missing):
		missing_data = load_json(args.missing)
		if isinstance(missing_data, dict) and "counts" in missing_data:
			missing_keys = set(missing_data["counts"].keys())
		elif isinstance(missing_data, dict):
			missing_keys = set(missing_data.keys())

	merged = {}
	skipped_cjk = []
	skipped_not_missing = []
	for key, value in translations.items():
		if has_cjk(key):
			skipped_cjk.append(key)
			continue
		if missing_keys is not None and key not in missing_keys:
			skipped_not_missing.append(key)
			continue
		merged[key] = value

	if not merged:
		print("No entries to merge.")
		return

	with open(args.i18n, "r", encoding="utf-8") as handle:
		lines = handle.readlines()

	start, end = find_zh_cn_block(lines)
	if start is None or end is None:
		raise SystemExit("Could not locate translations['zh_CN'] block")

	indent = detect_indent(lines, start, end)
	ensure_trailing_comma(lines, start, end, indent)

	insert_at = end
	new_lines = [build_entry_line(indent, k, v) for k, v in merged.items()]
	lines[insert_at:insert_at] = new_lines

	with open(args.i18n, "w", encoding="utf-8") as handle:
		handle.writelines(lines)

	print("Merged %d entries into %s" % (len(merged), args.i18n))
	if skipped_cjk:
		print("Skipped CJK keys: %d" % len(skipped_cjk))
	if skipped_not_missing:
		print("Skipped not-in-missing keys: %d" % len(skipped_not_missing))


if __name__ == "__main__":
	main()
