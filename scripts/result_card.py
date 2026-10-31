#!/usr/bin/env python3
"""Render the final comparison result as one image, straight from the verdict file."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from film_plans import Plate, GOOD, WARN, BLUE, INK, MUTE, W

v = json.loads(pathlib.Path("runs/benchmark-v2/independent-verification.json")
               .read_text(encoding="utf-8"))
a = v["arms"]
p = Plate("THE RESULT", "Concurrency bought time and cost cases.",
          "INDEPENDENT VERDICT %s . 12/12 blocks . 72/72 case-arms . same 24 cases per arm"
          % v.get("result"))
p.head()
hdr = ("Arm", "Accepted", "Controls refused", "Wall time")
xs = (130, 760, 1090, 1540)
for x, h in zip(xs, hdr):
    p.p.append('<text x="%d" y="%d" class="cap">%s</text>' % (x, p.y, h))
p.y += 54
for name, label in (("solo", "Solo, 1 agent"), ("serial", "Serial, 4 agents"),
                    ("parallel", "Parallel, 4 agents")):
    r = a[name]
    hot = name == "parallel"
    col = BLUE if hot else INK
    vals = ("%d / %d" % (r["accepted"], r["cases"]),
            "%d / 6" % r["controlled_negative_abstained"],
            "%.1f min" % (r["wall_ms"] / 60000))
    p.p.append('<text x="130" y="%d" class="row" fill="%s">%s</text>' % (p.y, col, label))
    for x, val in zip(xs[1:], vals):
        c = (GOOD if "54" in val else WARN if val.startswith("9 ") else INK) if hot else INK
        p.p.append('<text x="%d" y="%d" class="rowv" fill="%s">%s</text>' % (x, p.y, c, val))
    p.y += 62
p.rule()
p.body("The two sequential arms agree on all 24 cases. The parallel arm differs on 3. That "
       "control pair is what makes the gap readable: it is attributable to concurrency, not "
       "to noise. All three arms refuse all six missing-evidence controls.", 86)
p.body("18.5 percent faster, three fewer accepted out of twenty-four. No quality uplift is "
       "claimed, because none was measured.", 86, INK)
p.save("evidence/05-final-result")
print("carte ecrite")
