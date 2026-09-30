#!/usr/bin/env python3
"""Apply the reviewed local corrections to both variants and serializations.

Every replacement is guarded against both the pinned original and corrected
statement. Unrelated records, headers and competition answer formats stay intact.
"""

import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "LOCAL_CORRECTIONS.json").read_text())
    pending = []
    for variant in ("s", "c"):
        for extension in ("json", "jsonl"):
            path = root / f"datasets/miniF2F_v2{variant}.{extension}"
            records = (json.loads(path.read_text()) if extension == "json" else
                       [json.loads(line) for line in path.read_text().splitlines()])
            seen = set()
            for record in records:
                correction = manifest["cases"].get(record["name"])
                if correction is None:
                    continue
                patch = correction["variants"][variant]
                if record["formal_statement"] not in (
                    patch["upstream_formal_statement"], patch["formal_statement"]
                ):
                    raise ValueError(f"Unexpected statement in {path}: {record['name']}")
                record["formal_statement"] = patch["formal_statement"]
                seen.add(record["name"])
            if seen != set(manifest["cases"]):
                raise ValueError(f"Missing correction targets in {path}")
            text = (json.dumps(records, ensure_ascii=False, indent=2) + "\n" if extension == "json"
                    else "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
            pending.append((path, text))
    for path, text in pending:
        path.write_text(text)
    print(f"Applied {len(manifest['cases'])} corrections to v2s/v2c JSON and JSONL")


if __name__ == "__main__":
    main()
