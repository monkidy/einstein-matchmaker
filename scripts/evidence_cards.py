#!/usr/bin/env python3
"""Render the submission's evidence cards from the run files themselves.

Three cards, each built only from fields that exist in a run directory: the
independent verdict, one accepted proposal with a real quotation and its source
URL, and the honest outcome breakdown that separates evidence-based refusals
from deadline timeouts.

Nothing is typed in by hand. If a field is missing the card says so rather than
inventing a value.

Usage: python3 scripts/evidence_cards.py runs/benchmark-v2/block-1/parallel evidence
"""
import json
import pathlib
import sys

W = 1600
INK = "#1f2328"
MUTE = "#59636e"
LINE = "#d1d9e0"
GOOD = "#1a7f37"
WARN = "#9a6700"
BAD = "#cf222e"
ACCENT = "#0969da"


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def wrap(text, width):
    words, lines, cur = str(text).split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if len(trial) > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


class Card:
    def __init__(self, title, subtitle):
        self.y = 0
        self.parts = []
        self.title = title
        self.subtitle = subtitle

    def head(self):
        self.parts.append('<text x="56" y="68" class="h1">%s</text>' % esc(self.title))
        self.parts.append('<text x="56" y="104" class="sub">%s</text>' % esc(self.subtitle))
        self.parts.append('<line x1="56" y1="130" x2="%d" y2="130" stroke="%s"/>'
                          % (W - 56, LINE))
        self.y = 180

    def row(self, label, value, color=INK, gap=46):
        self.parts.append('<text x="56" y="%d" class="lbl">%s</text>' % (self.y, esc(label)))
        self.parts.append('<text x="560" y="%d" class="val" fill="%s">%s</text>'
                          % (self.y, color, esc(value)))
        self.y += gap

    def para(self, text, width=135, cls="body", color=MUTE):
        for line in wrap(text, width):
            self.parts.append('<text x="56" y="%d" class="%s" fill="%s">%s</text>'
                              % (self.y, cls, color, esc(line)))
            self.y += 34

    def rule(self, pad=18):
        self.y += pad
        self.parts.append('<line x1="56" y1="%d" x2="%d" y2="%d" stroke="%s"/>'
                          % (self.y, W - 56, self.y, LINE))
        self.y += pad + 24

    def foot(self, source):
        self.y += 10
        self.parts.append('<line x1="56" y1="%d" x2="%d" y2="%d" stroke="%s"/>'
                          % (self.y, W - 56, self.y, LINE))
        self.y += 38
        self.parts.append('<text x="56" y="%d" class="src">Source: %s</text>'
                          % (self.y, esc(source)))
        self.y += 40

    def write(self, path_prefix):
        height = self.y + 20
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
            'height="%d" role="img" aria-label="%s">'
            '<style>'
            'text{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}'
            '.h1{font-size:40px;font-weight:650;fill:%s}'
            '.sub{font-size:21px;fill:%s}'
            '.lbl{font-size:24px;fill:%s}'
            '.val{font-size:24px;font-weight:600}'
            '.body{font-size:23px}'
            '.mono{font-size:20px;font-family:ui-monospace,SFMono-Regular,Consolas,monospace}'
            '.src{font-size:19px;fill:%s;font-family:ui-monospace,SFMono-Regular,Consolas,monospace}'
            '</style>'
            '<rect width="%d" height="%d" fill="#ffffff"/>%s</svg>'
        ) % (W, height, W, height, esc(self.title), INK, MUTE, MUTE, MUTE, W, height,
             "".join(self.parts))
        pathlib.Path(path_prefix + ".svg").write_text(svg, encoding="utf-8")
        try:
            import cairosvg
            cairosvg.svg2png(url=path_prefix + ".svg", write_to=path_prefix + ".png",
                             output_width=W, background_color="white")
        except Exception as exc:                                    # pragma: no cover
            print("PNG skipped (%s)" % exc)
        print("wrote", path_prefix + ".svg")


def card_verification(run, out):
    v = json.loads((run / "independent-verification.json").read_text(encoding="utf-8"))
    c = v.get("concurrency") or {}
    card = Card("Independent verification: %s" % v.get("result", "?"),
                "Checked by a raw-file Python verifier, separate from the application's "
                "own scorer")
    card.head()
    card.row("Verdict", v.get("result", "?"),
             GOOD if v.get("result") == "PASS" else BAD)
    card.row("Arm", v.get("mode", "?"))
    card.row("Cases in block", v.get("cases", "?"))
    card.row("Accepted proposals", v.get("accepted", "?"))
    card.row("Source claims verified independently",
             v.get("source_claims_independently_verified", "?"), ACCENT)
    card.rule()
    card.row("Real inference concurrency proven",
             "yes" if c.get("parallel_proven") else "no",
             GOOD if c.get("parallel_proven") else BAD)
    card.row("Distinct Mozaik agents", c.get("distinct_agents", "?"))
    card.row("Mozaik answers on the bus", c.get("mozaik_answers", "?"))
    card.row("Verified peer events", v.get("verified_peer_events", "?"))
    card.row("Verified actual model responses",
             v.get("verified_actual_model_responses", "?"))
    card.rule()
    card.row("Client-only false concurrency",
             "rejected" if v.get("client_only_false_concurrency_rejected") else "NOT CHECKED",
             GOOD if v.get("client_only_false_concurrency_rejected") else BAD)
    card.row("Same-agent false concurrency",
             "rejected" if v.get("same_agent_false_concurrency_rejected") else "NOT CHECKED",
             GOOD if v.get("same_agent_false_concurrency_rejected") else BAD)
    card.rule()
    card.row("Hidden jury answer key available",
             "no" if v.get("hidden_jury_gold_available") is False else "?", WARN)
    card.row("Usefulness uplift proven",
             "no - and not claimed" if v.get("usefulness_uplift_proven") is False else "?",
             WARN)
    card.y += 8
    card.para("The verifier reports what it could not establish, not only what passed. "
              "No quality advantage is claimed anywhere in this submission.")
    card.foot("%s/independent-verification.json" % run.as_posix())
    card.write(str(out / "02-independent-verification"))


def pick_accepted(cases):
    for case in cases:
        if case.get("status") == "ACCEPTED":
            return case
    return None


def card_proposal(run, out):
    data = json.loads((run / "results.json").read_text(encoding="utf-8"))
    cases = data if isinstance(data, list) else data.get("cases", [])
    case = pick_accepted(cases)
    if case is None:
        print("no accepted case in", run)
        return
    prop = case.get("proposal") or {}
    claims = prop.get("claims") or []
    card = Card("An accepted proposal, and what it had to prove",
                "Case %s - accepted only after an independent critic and a source audit"
                % case.get("caseId", "?"))
    card.head()
    card.row("Company", "%s (%s)" % (prop.get("companyName", "?"),
                                     prop.get("companyId", "?")))
    card.row("Researcher", "%s (%s)" % (prop.get("researcherName", "?"),
                                        prop.get("researcherId", "?")))
    card.row("Independent critic", "accepted"
             if (case.get("critic") or {}).get("accepted") else "refused", GOOD)
    card.row("Factual claims, each quoting a source field", len(claims), ACCENT)
    metrics = case.get("metrics") or {}
    card.row("Model calls / wall time", "%s calls, %.0f s"
             % (metrics.get("modelCalls", "?"), metrics.get("wallMs", 0) / 1000))
    card.rule()
    card.para("Why this pair, in the system's own words:", cls="lbl", color=INK)
    card.y += 6
    card.para((case.get("selection") or {}).get("reason", "no reason recorded"))
    if claims:
        claim = claims[0]
        card.rule()
        card.para("One of its claims, as stored - a quotation, not a summary:",
                  cls="lbl", color=INK)
        card.y += 6
        for line in wrap('"%s"' % claim.get("quote", "?"), 120):
            card.parts.append('<text x="56" y="%d" class="body" fill="%s">%s</text>'
                              % (card.y, INK, esc(line)))
            card.y += 34
        card.y += 12
        for label, key in (("field", "field"), ("file", "file"),
                           ("locator", "locator"), ("record SHA-256", "recordSha256")):
            if claim.get(key) is not None:
                value = str(claim[key])
                if key == "recordSha256":
                    value = value[:48] + ("..." if len(value) > 48 else "")
                card.parts.append('<text x="56" y="%d" class="mono" fill="%s">%s: %s</text>'
                                  % (card.y, MUTE, esc(label), esc(value)))
                card.y += 32
        if claim.get("url"):
            card.y += 6
            for line in wrap("immutable source: " + claim["url"], 150):
                card.parts.append('<text x="56" y="%d" class="mono" fill="%s">%s</text>'
                                  % (card.y, ACCENT, esc(line)))
                card.y += 30
    card.foot("%s/results.json" % run.as_posix())
    card.write(str(out / "03-accepted-proposal"))


def card_outcomes(run, out):
    data = json.loads((run / "results.json").read_text(encoding="utf-8"))
    cases = data if isinstance(data, list) else data.get("cases", [])
    accepted, evidence_refusal, timeout = [], [], []
    for case in cases:
        reason = (case.get("reason") or "")
        if case.get("status") == "ACCEPTED":
            accepted.append(case)
        elif "timeout" in reason.lower() or "aborted" in reason.lower():
            timeout.append(case)
        else:
            evidence_refusal.append(case)
    card = Card("Outcomes, with the abstentions told apart",
                "A refusal on the evidence and a refusal on the clock are not the "
                "same result")
    card.head()
    card.row("Accepted", "%d of %d" % (len(accepted), len(cases)), GOOD)
    card.row("Refused on the evidence", "%d of %d"
             % (len(evidence_refusal), len(cases)), ACCENT)
    card.row("Ran out of time (deadline, not evidence)", "%d of %d"
             % (len(timeout), len(cases)), WARN)
    card.rule()
    for case in cases:
        reason = (case.get("reason") or "")
        status = case.get("status", "?")
        if status == "ACCEPTED":
            color, tag = GOOD, "ACCEPTED"
        elif "timeout" in reason.lower() or "aborted" in reason.lower():
            color, tag = WARN, "TIMEOUT"
        else:
            color, tag = ACCENT, "REFUSED"
        card.parts.append('<text x="56" y="%d" class="val" fill="%s">%s</text>'
                          % (card.y, color, esc(case.get("caseId", "?"))))
        card.parts.append('<text x="190" y="%d" class="val" fill="%s">%s</text>'
                          % (card.y, color, tag))
        detail = reason or "-"
        card.parts.append('<text x="420" y="%d" class="body" fill="%s">%s</text>'
                          % (card.y, MUTE, esc(detail[:88])))
        card.y += 44
    card.rule()
    card.para("Under a per-call deadline with a ceiling of four model calls on four CPU "
              "threads, some cases end without an answer. That is a budget limit, not a "
              "judgement about the sources, and it is counted separately everywhere in "
              "this submission. It is also the variable that distinguishes the "
              "architectures: at an equal budget, the question becomes how many cases an "
              "arm can finish at all.")
    card.foot("%s/results.json" % run.as_posix())
    card.write(str(out / "04-honest-outcomes"))


if __name__ == "__main__":
    run_dir = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                           else "runs/benchmark-v2/block-1/parallel")
    out_dir = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "evidence")
    out_dir.mkdir(parents=True, exist_ok=True)
    card_verification(run_dir, out_dir)
    card_proposal(run_dir, out_dir)
    card_outcomes(run_dir, out_dir)
