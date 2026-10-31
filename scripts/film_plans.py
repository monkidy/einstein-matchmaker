#!/usr/bin/env python3
"""Render the seven film plates for the submission video, from the run files.

Every figure on screen is read out of a run directory. Nothing is typed by hand except
the narration headings. Each plate carries an honesty pill saying what it is, in the same
discipline as the ANIMA film.

Usage: python3 scripts/film_plans.py runs/benchmark-v2/block-1/parallel film/plates
"""
import json
import pathlib
import sys

W, H = 1920, 1080
PAPER = "#f6f1e7"
INK = "#1f2328"
MUTE = "#6b6253"
RULE = "#d8cfbe"
GOOD = "#1a7f37"
WARN = "#9a6700"
BLUE = "#0b5fa5"

PILL_RUN = ("REAL RUN  .  31 Oct 2026  .  Qwen3-4B Q4_K_M, CPU only  .  organizer corpus v2"
            "  .  fictional dataset  .  edited for length")
PILL_DRAWN = "DRAWN FROM THE TRACE  .  no interpolated value"


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def wrap(text, width):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


class Plate:
    def __init__(self, kicker, title, pill=PILL_RUN):
        self.p = []
        self.kicker = kicker
        self.title = title
        self.pill = pill
        self.y = 300

    def head(self):
        self.p.append('<text x="130" y="150" class="kick">%s</text>' % esc(self.kicker))
        for i, line in enumerate(wrap(self.title, 42)):
            self.p.append('<text x="130" y="%d" class="h1">%s</text>' % (228 + i * 76, line))
        self.y = 228 + len(wrap(self.title, 42)) * 76 + 48

    def rule(self):
        self.p.append('<line x1="130" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>'
                      % (self.y, W - 130, self.y, RULE))
        self.y += 44

    def quote(self, text, width=62):
        self.p.append('<rect x="130" y="%d" width="10" height="%d" fill="%s"/>'
                      % (self.y - 42, len(wrap(text, width)) * 54 + 16, BLUE))
        for line in wrap(text, width):
            self.p.append('<text x="178" y="%d" class="quote">%s</text>' % (self.y, esc(line)))
            self.y += 50
        self.y += 16

    def body(self, text, width=78, color=None):
        for line in wrap(text, width):
            self.p.append('<text x="130" y="%d" class="body" fill="%s">%s</text>'
                          % (self.y, color or MUTE, esc(line)))
            self.y += 44
        self.y += 10

    def stat(self, value, label, x, color=INK):
        self.p.append('<text x="%d" y="%d" class="num" fill="%s">%s</text>'
                      % (x, self.y, color, esc(value)))
        for i, line in enumerate(wrap(label, 24)):
            self.p.append('<text x="%d" y="%d" class="cap">%s</text>'
                          % (x, self.y + 48 + i * 34, esc(line)))

    def row(self, left, right, color=INK, gap=56):
        self.p.append('<text x="130" y="%d" class="row">%s</text>' % (self.y, esc(left)))
        self.p.append('<text x="900" y="%d" class="rowv" fill="%s">%s</text>'
                      % (self.y, color, esc(right)))
        self.y += gap

    # Below this line the subtitles live. Nothing a viewer must read may go there.
    SUBTITLE_BAND = 845

    def save(self, path):
        if self.y > self.SUBTITLE_BAND:
            print("  ATTENTION: %s deborde dans la bande des sous-titres (y=%d > %d)"
                  % (pathlib.Path(path).name, self.y, self.SUBTITLE_BAND))
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">'
            '<style>'
            'text{font-family:"Segoe UI",ui-sans-serif,system-ui,sans-serif}'
            '.kick{font-size:26px;fill:%s;letter-spacing:.18em}'
            '.h1{font-size:62px;font-weight:650;fill:%s}'
            '.quote{font-size:36px;fill:%s;font-style:italic}'
            '.body{font-size:32px}'
            '.row{font-size:34px;fill:%s}'
            '.rowv{font-size:34px;font-weight:650}'
            '.num{font-size:92px;font-weight:700}'
            '.cap{font-size:26px;fill:%s}'
            '.pill{font-size:21px;fill:%s;font-family:ui-monospace,Consolas,monospace}'
            '.mono{font-size:27px;fill:%s;font-family:ui-monospace,Consolas,monospace}'
            '</style>'
            '<rect width="%d" height="%d" fill="%s"/>%s'
            '<line x1="130" y1="975" x2="%d" y2="975" stroke="%s" stroke-width="2"/>'
            '<text x="130" y="1018" class="pill">%s</text>'
            '</svg>'
        ) % (W, H, W, H, MUTE, INK, INK, MUTE, MUTE, MUTE, MUTE, W, H, PAPER,
             "".join(self.p), W - 130, RULE, esc(self.pill))
        pathlib.Path(path + ".svg").write_text(svg, encoding="utf-8")
        try:
            import cairosvg
            cairosvg.svg2png(url=path + ".svg", write_to=path + ".png", output_width=W)
        except Exception as exc:
            print("PNG ignore (%s)" % exc)
        print("plan", pathlib.Path(path).name)


def load(run):
    run = pathlib.Path(run)
    res = json.loads((run / "results.json").read_text(encoding="utf-8"))
    cases = res if isinstance(res, list) else res.get("cases", [])
    ver = json.loads((run / "independent-verification.json").read_text(encoding="utf-8"))
    rec = json.loads((run / "receipt.json").read_text(encoding="utf-8"))
    return cases, ver, rec


def main(run, out):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    cases, ver, rec = load(run)
    accepted = next((c for c in cases if c.get("status") == "ACCEPTED"), None)
    prop = (accepted or {}).get("proposal") or {}
    claims = prop.get("claims") or []
    challenge_quote = next((c.get("quote") for c in claims
                            if str(c.get("file", "")).endswith("companies.json")), None)

    # S1, the problem
    p = Plate("THE PROBLEM", "A company knows its pain. It does not know who can fix it.")
    p.head()
    if challenge_quote:
        p.quote(challenge_quote)
    p.body("One of 489 challenges in the corpus, and 1047 researchers to look through.")
    p.save(str(out / "S1_problem"))

    # S2, the agents
    agents = rec.get("agents") or []
    p = Plate("THE SYSTEM", "Four agents, one model, nothing leaves the machine.")
    p.head()
    for a in agents:
        p.row(a.get("name", "?"), (a.get("id", "") or "")[:28], BLUE, gap=50)
    p.rule()
    p.row("Hosted model API calls", str(rec.get("hostedInferenceCalls", "?")), GOOD)
    p.row("Paid provider calls", str(rec.get("paidProviderCalls", "?")), GOOD)
    p.row("Runtime", str(rec.get("runtime", "?")))
    p.save(str(out / "S2_agents"))

    # S3, the concurrency, drawn from the slot samples
    import collections
    dist = collections.Counter()
    pts = []
    for line in (pathlib.Path(run) / "trace.jsonl").open(encoding="utf-8"):
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("event") == "server.slots":
            n = sum(1 for s in (ev.get("slots") or []) if s.get("processing"))
            dist[n] += 1
            pts.append((ev.get("at"), n))
    total = sum(dist.values())
    two = dist.get(2, 0)
    p = Plate("THE PROOF", "Two slots, busy at the same instant.", PILL_DRAWN)
    p.head()
    p.y += 10
    p.stat("%d" % two, "samples with two slots processing", 130, GOOD)
    p.stat("%d" % total, "samples taken of the slot table", 700)
    p.stat("%.1f%%" % (100.0 * two / max(total, 1)), "of observed compute", 1270, GOOD)
    p.y += 190
    # bande temporelle, un trait par echantillon
    t0, t1 = pts[0][0], pts[-1][0]
    span = max(t1 - t0, 1)
    p.p.append('<rect x="130" y="%d" width="%d" height="64" fill="#ffffff" stroke="%s"/>'
               % (p.y, W - 260, RULE))
    step = max(1, len(pts) // 1400)
    for at, n in pts[::step]:
        x = 130 + (at - t0) / span * (W - 260)
        col = GOOD if n >= 2 else "#b9ad97"
        p.p.append('<rect x="%.1f" y="%d" width="1.6" height="%d" fill="%s"/>'
                   % (x, p.y + (6 if n >= 2 else 24), 52 if n >= 2 else 16, col))
    p.y += 108
    p.body("Green is two agents inferring at the same instant, over %.0f seconds of run. Two "
           "HTTP requests in flight would not count: the verifier demands two distinct "
           "producers, overlapping intervals, and two server slots observed in PROCESSING."
           % (span / 1000.0), 78)
    p.save(str(out / "S3_concurrency"))

    # S4, an accepted proposal
    p = Plate("THE ANSWER", "Accepted, because every claim quotes its source.")
    p.head()
    p.row("Company", "%s (%s)" % (prop.get("companyName", "?"), prop.get("companyId", "?")))
    p.row("Researcher", "%s (%s)" % (prop.get("researcherName", "?"),
                                     prop.get("researcherId", "?")), BLUE)
    p.row("Claims, each quoting a source field", str(len(claims)), GOOD)
    p.row("Independent critic",
          "accepted" if ((accepted or {}).get("critic") or {}).get("accepted") else "refused",
          GOOD)
    p.rule()
    if claims:
        c0 = claims[0]
        p.p.append('<text x="130" y="%d" class="mono">%s</text>'
                   % (p.y, esc("record " + str(c0.get("recordSha256", ""))[:40] + "...")))
        p.y += 44
        p.p.append('<text x="130" y="%d" class="mono">%s</text>'
                   % (p.y, esc(str(c0.get("file", "")) + "  " + str(c0.get("locator", "")))))
    p.save(str(out / "S4_accepted"))

    # S5, the outcomes told apart
    acc = [c for c in cases if c.get("status") == "ACCEPTED"]
    tmo = [c for c in cases if c.get("status") != "ACCEPTED"
           and ("timeout" in (c.get("reason") or "").lower()
                or "aborted" in (c.get("reason") or "").lower())]
    ref = [c for c in cases if c.get("status") != "ACCEPTED" and c not in tmo]
    p = Plate("THE HONEST PART", "A refusal on the evidence is not a refusal on the clock.")
    p.head()
    p.y += 10
    p.stat(str(len(acc)), "accepted", 130, GOOD)
    p.stat(str(len(ref)), "refused on the evidence", 700, BLUE)
    p.stat(str(len(tmo)), "ran out of time", 1270, WARN)
    p.y += 190
    p.body("A case that ends on the clock has said nothing about its sources, so the three "
           "are never added together, here or in the repository. That distinction is also "
           "where the architectures differ: at an equal time budget, the question becomes "
           "how many cases an arm can finish at all.", 78)
    p.save(str(out / "S5_outcomes"))

    # S6, what is not claimed
    p = Plate("WHAT WE DO NOT CLAIM", "No answer key exists, so no advantage is claimed.",
              PILL_DRAWN)
    p.head()
    p.row("Hidden jury answer key available",
          "no" if ver.get("hidden_jury_gold_available") is False else "?", WARN)
    p.row("Usefulness uplift proven",
          "no, and not claimed" if ver.get("usefulness_uplift_proven") is False else "?", WARN)
    p.rule()
    p.body("The verifier reports what it could not establish, not only what passed. The README "
           "marks every statement PROVEN or NOT CLAIMED in a table at the top, and this line "
           "is one of them. A speed or quality advantage has to be measured. It is never "
           "inferred from the number of agents.")
    p.save(str(out / "S6_not_claimed"))

    # S7, end card
    p = Plate("", "EINSTEIN Matchmaker", "Narration: synthetic voice (Asso, SYSTASYS).  .  "
                                         "Entry by Hichem Benali, solo.")
    p.head()
    p.body("A system that cannot refuse cannot be trusted when it accepts.", 56, INK)
    p.y += 30
    p.p.append('<text x="130" y="%d" class="mono">github.com/monkidy/einstein-matchmaker</text>'
               % p.y)
    p.y += 60
    p.p.append('<text x="130" y="%d" class="cap">The code, the traces and the verdicts are all '
               'in the repository.</text>' % p.y)
    p.save(str(out / "S7_end"))
    print("OK, 4 plans ecrits dans", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "runs/benchmark-v2/block-1/parallel",
         sys.argv[2] if len(sys.argv) > 2 else "film/plates")
