#!/usr/bin/env python3
"""Assemble the submission film from the plates, the narration and its receipt.

Each plate is held for exactly as long as its narration segment lasts, plus a short
breath, so picture and voice never drift. Subtitles come from the word timings the
narration receipt recorded, not from a re-transcription.

Inputs expected under <work>:
  plates/S1_problem.png ... S7_end.png
  audio/S1_g1234.m4a ... (or _g1235 for a retake)
  audio/recu.json

Usage: python3 scripts/build_film.py film einstein_matchmaker_demo.mp4
"""
import json
import pathlib
import subprocess
import sys

ORDER = [("S1", "S1_problem"), ("S2", "S2_agents"), ("S3", "S3_concurrency"),
         ("S4", "S4_accepted"), ("S5", "S5_outcomes"), ("S6", "S6_not_claimed"),
         ("S7", "S7_end")]
BREATH = 0.55          # silence between segments, as in the ANIMA film
HEAD, TAIL = 0.6, 1.8  # a beat before the first word and after the last


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        print(" ".join(str(c) for c in cmd[:6]), "...")
        print(p.stderr[-1500:])
        raise SystemExit("ffmpeg a echoue")
    return p


def best(receipt, ident):
    """The retained take: fewest misheard words, then the most natural."""
    tries = receipt["candidats"][ident]["essais"]
    return sorted(tries, key=lambda e: (e.get("wer", 1), -e.get("utmos22", 0)))[0]


def srt_time(t):
    ms = int(round(max(t, 0) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def main(work, out_name):
    work = pathlib.Path(work)
    plates, audio = work / "plates", work / "audio"
    receipt = json.loads((audio / "recu.json").read_text(encoding="utf-8"))
    tmp = work / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    # 1. the audio track, and where every segment starts on it
    parts, starts, t = [], {}, HEAD
    for ident, _ in ORDER:
        take = best(receipt, ident)
        src = audio / (take["prefixe"] + ".m4a")
        if not src.exists():
            src = audio / (take["prefixe"] + "_presence.wav")
        starts[ident] = t
        parts.append((ident, src, take))
        t += take["duree_s"] + BREATH
    total = t - BREATH + TAIL

    # inputs in play order: head silence, segment, gap, segment, gap, ...
    ins, idx = ["-f", "lavfi", "-t", str(HEAD), "-i", "anullsrc=r=48000:cl=stereo"], 1
    labels = ["[0:a]"]
    for n, (ident, src, take) in enumerate(parts):
        ins += ["-i", str(src)]
        labels.append("[%d:a]" % idx); idx += 1
        gap = BREATH if n < len(parts) - 1 else TAIL
        ins += ["-f", "lavfi", "-t", str(gap), "-i", "anullsrc=r=48000:cl=stereo"]
        labels.append("[%d:a]" % idx); idx += 1
    voice = tmp / "voice.m4a"
    run(["ffmpeg", "-y", *ins, "-filter_complex",
         "".join(labels) + "concat=n=%d:v=0:a=1[a]" % len(labels),
         "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(voice)])

    # 2. subtitles.
    # The spoken text is the authored one, never the transcription: the engine is fed
    # "Sistah-ziss" so it pronounces SYSTASYS, and a viewer must read SYSTASYS. Word
    # timings come from the receipt and are mapped onto the authored words by position,
    # which is safe here because the measured word error rate stays under 5 percent.
    MAX_LINE, MAX_LINES, CPS, MIN_DUR = 42, 2, 17.0, 1.3
    SPOKEN_TO_WRITTEN = {"Sistah-ziss": "SYSTASYS", "Sistah-ziss.": "SYSTASYS."}

    def lay_out(text):
        """Split one sentence into at most two balanced lines."""
        if len(text) <= MAX_LINE:
            return [text]
        words, lines, cur = text.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if len(t) > MAX_LINE and cur:
                lines.append(cur); cur = w
            else:
                cur = t
        if cur:
            lines.append(cur)
        return lines

    cues = []
    for ident, _, take in parts:
        spoken = take["texte"]
        written = " ".join(SPOKEN_TO_WRITTEN.get(w, w) for w in spoken.split())
        words = take.get("mots") or []
        base, dur = starts[ident], take["duree_s"]
        src = written.split()
        n_src, n_ref = len(src), len(words)

        def t_of(i, end=False):
            """Time of authored word i, read off the nearest measured word."""
            if not n_ref:
                return base + dur * (i + (1 if end else 0)) / max(n_src, 1)
            j = min(n_ref - 1, max(0, round(i * (n_ref - 1) / max(n_src - 1, 1))))
            return base + (words[j]["f"] if end else words[j]["d"])

        # cut on sentence ends, then on length
        groups, cur, start_i = [], [], 0
        for i, w in enumerate(src):
            cur.append(w)
            text = " ".join(cur)
            if w.endswith((".", "?", "!", ":")) or len(text) > MAX_LINE * MAX_LINES:
                groups.append((start_i, i, text)); cur, start_i = [], i + 1
        if cur:
            groups.append((start_i, len(src) - 1, " ".join(cur)))

        for a_i, b_i, text in groups:
            t0, t1 = t_of(a_i), t_of(b_i, end=True)
            need = max(MIN_DUR, len(text) / CPS)          # comfortable reading time
            if t1 - t0 < need:
                t1 = t0 + need
            cues.append([t0, t1, "\n".join(lay_out(text))])

    # Merge a cue that would flash past with the next one, when the two still fit in
    # two lines. Stretching it instead would only push it onto the following cue.
    merged, i = [], 0
    while i < len(cues):
        t0, t1, text = cues[i]
        while i + 1 < len(cues):
            nxt = cues[i + 1]
            joined = text.replace("\n", " ") + " " + nxt[2].replace("\n", " ")
            too_brief = (t1 - t0) < MIN_DUR or len(text.replace("\n", " ")) / max(t1 - t0, .1) > 19
            if too_brief and len(joined) <= MAX_LINE * MAX_LINES and nxt[0] - t1 < 1.0:
                t1, text, i = nxt[1], "\n".join(lay_out(joined)), i + 1
            else:
                break
        merged.append([t0, t1, text])
        i += 1
    cues = merged
    # never let a cue run into the next one, and keep them inside the film
    for i in range(len(cues) - 1):
        cues[i][1] = min(cues[i][1], cues[i + 1][0] - 0.08)
    cues = [c for c in cues if c[1] - c[0] > 0.4]
    srt = ["%d\n%s --> %s\n%s\n" % (i, srt_time(a), srt_time(b), t)
           for i, (a, b, t) in enumerate(cues, start=1)]
    srt_path = tmp / "subs.srt"
    srt_path.write_text("\n".join(srt), encoding="utf-8")

    # An ASS file carrying its own PlayRes, because the subtitles filter lays a plain SRT
    # out in a 384x288 frame: every margin and font size would be read in the wrong unit
    # and the text would land mid-screen at the wrong size.
    def ass_time(t):
        cs = int(round(max(t, 0) * 100))
        h, cs = divmod(cs, 360000)
        m, cs = divmod(cs, 6000)
        s, cs = divmod(cs, 100)
        return "%d:%02d:%02d.%02d" % (h, m, s, cs)

    ass = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080",
        "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Sub,Segoe UI,44,&H0028231F,&H0028231F,&H00D2E3EC,&H00D2E3EC,"
        "0,0,0,0,100,100,0,0,3,12,0,2,200,200,96,1", "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for a, b, text in cues:
        ass.append("Dialogue: 0,%s,%s,Sub,,0,0,0,,%s"
                   % (ass_time(a), ass_time(b), text.replace("\n", "\\N")))
    ass_path = tmp / "subs.ass"
    ass_path.write_text("\n".join(ass) + "\n", encoding="utf-8")

    # 3. the picture: each plate held for its segment, with a slow push in
    seg_files = []
    for n, (ident, _, take) in enumerate(parts):
        plate = plates / (dict(ORDER)[ident] + ".png")
        gap = BREATH if n < len(parts) - 1 else TAIL
        dur = take["duree_s"] + gap
        seg = tmp / ("v_%s.mp4" % ident)
        frames = max(int(dur * 25), 25)
        run(["ffmpeg", "-y", "-loop", "1", "-i", str(plate), "-t", "%.3f" % dur,
             "-filter_complex",
             "scale=2400:-1,zoompan=z='min(1.04,1.001+0.00035*on)':d=%d:"
             "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=25,"
             "fade=t=in:st=0:d=0.35,fade=t=out:st=%.3f:d=0.35,format=yuv420p"
             % (frames, max(dur - 0.35, 0.1)),
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "25", str(seg)])
        seg_files.append(seg)
    # head silence as a first beat on plate 1
    head_seg = tmp / "v_head.mp4"
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(plates / "S1_problem.png"),
         "-t", "%.3f" % HEAD, "-vf",
         "scale=1920:1080,fade=t=in:st=0:d=0.4,format=yuv420p",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "25", str(head_seg)])

    # ffmpeg resolves relative paths in a concat list against the list's own folder,
    # so the entries are absolute.
    lst = tmp / "concat.txt"
    lst.write_text("".join("file '%s'\n" % p.resolve().as_posix()
                           for p in [head_seg] + seg_files), encoding="utf-8")
    picture = tmp / "picture.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
         str(picture)])

    # 4. picture + voice + burned-in subtitles
    out = work / out_name
    run(["ffmpeg", "-y", "-i", str(picture), "-i", str(voice),
         "-vf", "ass=%s" % ass_path.as_posix().replace(":", "\\:"),
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
         "-shortest", str(out)])
    print("FILM:", out, "duree visee %.2f s" % total)
    for ident, _, take in parts:
        print("  %s  %5.2f s  wer=%s  utmos=%s" % (ident, take["duree_s"],
                                                   take.get("wer"), take.get("utmos22")))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "film",
         sys.argv[2] if len(sys.argv) > 2 else "einstein_matchmaker_demo.mp4")
