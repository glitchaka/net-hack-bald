#!/usr/bin/env python3
"""Genera el template de traducción para opthelp."""

import polib

po = polib.pofile("po/es.po")
entries = []

for entry in po:
    is_op = any(ref[0] == "dat/opthelp" for ref in entry.occurrences)
    if is_op and not entry.msgstr:
        entries.append(entry.msgid)

print(f"# Template opthelp - {len(entries)} entradas")
print("TRANSLATIONS = {")
for msgid in entries:
    escaped = msgid.replace("\\", "\\\\").replace('"', '\\"')
    print(f'    "{escaped}": "",')
print("}")
