#!/usr/bin/env bash
# Build repo-market-model's published daily panel at the pinned commit and check its digest.
# Usage: scripts/build_panel.sh [path to a repo-market-model checkout]   (default: ../repo-market-model)
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
parent="${1:-$here/../repo-market-model}"
pin="$here/metadata/parent_pin.json"
read_pin() {  # read_pin a.b -> the value at that dotted key of the pin file
  python3 -c "import json,sys; d=json.load(open(sys.argv[1]))
for k in sys.argv[2].split('.'): d=d[k]
print(d)" "$pin" "$1"
}
commit="$(read_pin commit)"
expected="$(read_pin panel_sha256)"
mkdir -p "$here/data"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
git -C "$parent" fetch --quiet origin "$commit" 2>/dev/null || true
git -C "$parent" archive "$commit" | tar -x -C "$work"
( cd "$work" && PYTHONPATH=src python3.11 -m repo_model.cli build \
    --raw-root "$(read_pin panel_build.raw_root)" \
    --output "$here/data/panel.csv" \
    --build-cutoff "$(read_pin panel_build.build_cutoff)" \
    --decision-time "$(read_pin panel_build.decision_time)" >/dev/null )
cp "$work/$(read_pin fomc_calendar)" "$here/data/fomc_calendar.json"
actual="$(sha256sum "$here/data/panel.csv" | cut -d' ' -f1)"
if [ "$actual" != "$expected" ]; then
  echo "panel digest mismatch: $actual != $expected" >&2; exit 1
fi
echo "panel ok: $actual"
