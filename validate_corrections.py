#!/usr/bin/env python3
"""Check provenance, serialization consistency, and Lean elaboration.

The generated `sorry` bodies ONLY validate statement elaboration. They are not
proofs of these benchmark problems. Regression.lean contains actual checked
proofs for selected semantic properties and counterexamples.
"""

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean-project", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "LOCAL_CORRECTIONS.json").read_text())
    assert sum(c["issue"] == 2 for c in manifest["cases"].values()) == 23
    chunks = []
    for variant in ("s", "c"):
        statements = {}
        for extension in ("json", "jsonl"):
            relative = f"datasets/miniF2F_v2{variant}.{extension}"
            raw = (root / relative).read_text()
            original = subprocess.check_output(
                ["git", "show", f"{manifest['upstream_commit']}:{relative}"],
                cwd=root, text=True,
            )
            parse = json.loads if extension == "json" else lambda s: list(map(json.loads, s.splitlines()))
            records, before = parse(raw), parse(original)
            assert len(records) == len(before) == 488
            assert len({r["name"] for r in records}) == 488
            assert sum(r["split"].lower() == "test" for r in records) == 244
            for current, previous in zip(records, before):
                name = current["name"]
                assert name == previous["name"], "record ordering changed"
                correction = manifest["cases"].get(name)
                expected = dict(previous)
                if correction:
                    patch = correction["variants"][variant]
                    assert previous["formal_statement"] == patch["upstream_formal_statement"]
                    expected["formal_statement"] = patch["formal_statement"]
                assert current == expected, (relative, name, "unexpected data drift")
                if extension == "json":
                    statements[name] = current["formal_statement"]
                else:
                    assert statements[name] == current["formal_statement"]
        for name in manifest["cases"]:
            namespace = variant + "_" + name
            chunks.append(f"namespace {namespace}\n{statements[name]}\n  sorry\nend {namespace}")
    source = "import Mathlib\nimport Aesop\nopen BigOperators Real Nat Rat Finset Topology\n\n"
    with tempfile.TemporaryDirectory(prefix="minif2f-corrections-") as directory:
        path = Path(directory) / "Validate.lean"
        path.write_text(source + "\n\n".join(chunks))
        result = subprocess.run(["lake", "env", "lean", str(path)],
                                cwd=args.lean_project, capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise SystemExit(result.stdout + result.stderr)
    subprocess.run(["lake", "env", "lean", str(root / "Regression.lean")],
                   cwd=args.lean_project, check=True, timeout=120)
    print("PASS: 23 issue cases + 1 additional correction; both variants, both formats")
    print("PASS: 48 corrected declarations elaborate; selected semantic regression proofs verified")


if __name__ == "__main__":
    main()
