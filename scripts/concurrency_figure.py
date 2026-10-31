#!/usr/bin/env python3
"""Measure real inference concurrency from a run trace and draw it.

Reads runs/<name>/trace.jsonl, counts server slots actually PROCESSING at each
sample, and writes a self-contained SVG plus a JSON receipt. Every drawn pixel
is backed by a measured field: no decorative movement, no inferred value.

Usage: python3 scripts/concurrency_figure.py runs/<name> [out_prefix]
"""
import json
import sys
import pathlib

def samples(trace_path):
    out = []
    with open(trace_path, encoding="utf-8") as fh:
        for line in fh:
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if ev.get("event") != "server.slots":
                continue
            slots = ev.get("slots") or []
            out.append((ev.get("at"), sum(1 for s in slots if s.get("processing"))))
    return out

def measure(run_dir):
    trace = pathlib.Path(run_dir) / "trace.jsonl"
    pts = samples(trace)
    if not pts:
        raise SystemExit("no server.slots samples in %s" % trace)
    total = len(pts)
    dist = {}
    for _, n in pts:
        dist[n] = dist.get(n, 0) + 1
    overlap = sum(c for n, c in dist.items() if n >= 2)
    t0 = pts[0][0]
    spans, start = [], None
    for at, n in pts:
        if n >= 2 and start is None:
            start = at
        elif n < 2 and start is not None:
            spans.append((start, at))
            start = None
    if start is not None:
        spans.append((start, pts[-1][0]))
    return {
        "run": str(pathlib.Path(run_dir).name),
        "samples_total": total,
        "samples_by_slots_processing": {str(k): v for k, v in sorted(dist.items())},
        "samples_with_two_or_more": overlap,
        "overlap_share_formula": "samples_with_two_or_more / samples_total",
        "overlap_share": round(overlap / total, 6),
        "max_slots_processing": max(dist),
        "overlap_windows": len(spans),
        "overlap_seconds_total": round(sum(b - a for a, b in spans) / 1000.0, 3),
        "wall_seconds_observed": round((pts[-1][0] - t0) / 1000.0, 3),
        "source": "runs/%s/trace.jsonl, event=server.slots, field slots[].processing"
                  % pathlib.Path(run_dir).name,
        "caveat": "Counts llama.cpp server slots in the PROCESSING state. Two HTTP "
                  "requests in flight are not counted as concurrency.",
    }, pts, spans

def svg(m, pts, spans, path):
    W, H, PAD = 900, 260, 48
    t0, t1 = pts[0][0], pts[-1][0]
    span = max(t1 - t0, 1)
    def x(at):
        return PAD + (at - t0) / span * (W - 2 * PAD)
    rows = {1: H - 150, 2: H - 196}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="Measured inference concurrency">' % (W, H, W, H),
        '<style>'
        'text{font:13px ui-sans-serif,system-ui,sans-serif;fill:#1f2328}'
        '.s{font-size:11px;fill:#59636e}.k{font-weight:600}'
        '</style>',
        '<rect width="%d" height="%d" fill="#ffffff"/>' % (W, H),
        '<text x="%d" y="26" class="k">Measured inference concurrency — run %s</text>'
        % (PAD, m["run"]),
        '<text x="%d" y="44" class="s">%d samples of llama.cpp server slots; '
        '%d show two slots PROCESSING at the same instant (%.1f%%); '
        '%d overlap window(s) totalling %.1f s over %.1f s observed</text>'
        % (PAD, m["samples_total"], m["samples_with_two_or_more"],
           100 * m["overlap_share"], m["overlap_windows"],
           m["overlap_seconds_total"], m["wall_seconds_observed"]),
    ]
    for lvl, y in rows.items():
        parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#d1d9e0"/>'
                     % (PAD, y, W - PAD, y))
        parts.append('<text x="8" y="%d" class="s">%d slot%s</text>'
                     % (y + 4, lvl, "" if lvl == 1 else "s"))
    for a, b in spans:
        parts.append('<rect x="%.2f" y="%d" width="%.2f" height="10" fill="#1a7f37" '
                     'opacity="0.85"/>' % (x(a), rows[2] - 5, max(x(b) - x(a), 1.2)))
    prev = None
    for at, n in pts:
        if n >= 1 and n < 2:
            xx = x(at)
            if prev is None or xx - prev > 0.6:
                parts.append('<rect x="%.2f" y="%d" width="1.2" height="10" '
                             'fill="#8250df" opacity="0.5"/>' % (xx, rows[1] - 5))
                prev = xx
    parts.append('<text x="%d" y="%d" class="s">0 s</text>' % (PAD, H - 16))
    parts.append('<text x="%d" y="%d" class="s" text-anchor="end">%.1f s</text>'
                 % (W - PAD, H - 16, m["wall_seconds_observed"]))
    parts.append('<text x="%d" y="%d" class="s">Green = two slots processing '
                 "(real concurrency). Purple = one slot. Drawn from the trace "
                 'only.</text>' % (PAD, H - 34))
    parts.append("</svg>")
    pathlib.Path(path).write_text("\n".join(parts), encoding="utf-8")

if __name__ == "__main__":
    run = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else "concurrency"
    m, pts, spans = measure(run)
    pathlib.Path(prefix + ".json").write_text(
        json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    svg(m, pts, spans, prefix + ".svg")
    print(json.dumps(m, indent=2, ensure_ascii=False))
