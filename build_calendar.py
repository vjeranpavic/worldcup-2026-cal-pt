#!/usr/bin/env python3
"""
Build the World Cup 2026 calendar feed from schedule.json.

Outputs into ./site :
  - worldcup.ics   (the subscribable calendar feed, Pacific time)
  - index.html     (a friendly landing page with subscribe links)

No third-party dependencies (Python standard library only).
"""
import json
import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "site")
ICS_NAME = "worldcup.ics"

# America/Los_Angeles VTIMEZONE — makes events display as Pacific in every app,
# regardless of the viewer's own device timezone.
VTIMEZONE = """BEGIN:VTIMEZONE
TZID:America/Los_Angeles
BEGIN:DAYLIGHT
TZOFFSETFROM:-0800
TZOFFSETTO:-0700
TZNAME:PDT
DTSTART:20070311T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0700
TZOFFSETTO:-0800
TZNAME:PST
DTSTART:20071104T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE""".split("\n")


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def make_title(m: dict) -> str:
    home, away, stage = m["home"], m["away"], m["stage"]
    if home == "TBD" and away == "TBD":
        core = stage                      # e.g. "Round of 32" before teams are known
    else:
        core = f"{home} vs {away}"
        if not stage.startswith("Group"):
            core = f"{core} ({stage})"
    return f"\u26bd {core}"               # soccer ball prefix


def build_ics(data: dict) -> str:
    tzid = data.get("timezone", "America/Los_Angeles")
    dur = int(data.get("match_duration_minutes", 120))
    name = data.get("calendar_name", "FIFA World Cup 2026 (Pacific Time)")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//WC2026//Self-Hosted Pacific Feed//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{esc(name)}",
        f"X-WR-TIMEZONE:{tzid}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
    ]
    lines += VTIMEZONE

    # Stable timestamp so unchanged events don't churn; bumped only when file changes.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for m in data["matches"]:
        start = datetime.strptime(f"{m['date']} {m['time']}", "%Y-%m-%d %H:%M")
        end = start + timedelta(minutes=dur)
        lines += [
            "BEGIN:VEVENT",
            f"UID:wc2026-match-{m['id']}@worldcup-feed",
            f"DTSTAMP:{stamp}",
            f"DTSTART;TZID={tzid}:{start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND;TZID={tzid}:{end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{esc(make_title(m))}",
            f"LOCATION:{esc(m['venue'])}",
            f"DESCRIPTION:{esc('FIFA World Cup 2026 \u2014 ' + m['stage'] + '. All times shown in Pacific.')}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def pages_base_url() -> str:
    """Derive the GitHub Pages URL from Actions env vars, else a placeholder."""
    repo = os.environ.get("GITHUB_REPOSITORY")  # "owner/name"
    if repo and "/" in repo:
        owner, name = repo.split("/", 1)
        return f"https://{owner.lower()}.github.io/{name}"
    return "https://YOUR-USERNAME.github.io/YOUR-REPO"


def build_index(data: dict) -> str:
    base = pages_base_url()
    ics_https = f"{base}/{ICS_NAME}"
    ics_webcal = ics_https.replace("https://", "webcal://", 1)
    google_add = f"https://calendar.google.com/calendar/r?cid={ics_webcal}"
    name = data.get("calendar_name", "FIFA World Cup 2026 (Pacific Time)")
    n = len(data["matches"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name}</title>
<style>
  :root {{ --ink:#0d1b2a; --accent:#0b6e4f; --muted:#5b6b7b; --bg:#f7f5ef; --card:#fff; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
         background:var(--bg); color:var(--ink); line-height:1.5; }}
  .wrap {{ max-width:640px; margin:0 auto; padding:48px 24px 64px; }}
  h1 {{ font-size:1.9rem; margin:0 0 .25em; letter-spacing:-.02em; }}
  .sub {{ color:var(--muted); margin:0 0 32px; }}
  .card {{ background:var(--card); border:1px solid #e7e2d6; border-radius:14px; padding:24px; margin-bottom:18px; }}
  .btn {{ display:inline-block; background:var(--accent); color:#fff; text-decoration:none;
          padding:12px 18px; border-radius:10px; font-weight:600; margin:6px 6px 6px 0; }}
  .btn.alt {{ background:#0d1b2a; }}
  code {{ background:#eef0ee; padding:2px 7px; border-radius:6px; font-size:.9em; word-break:break-all; }}
  ol {{ padding-left:20px; }} li {{ margin:.35em 0; }}
  .url {{ display:block; margin-top:10px; }}
  footer {{ color:var(--muted); font-size:.85rem; margin-top:28px; }}
</style>
</head>
<body>
  <div class="wrap">
    <h1>\u26bd {name}</h1>
    <p class="sub">All {n} matches \u00b7 kickoff times in Pacific \u00b7 auto-updating subscription</p>

    <div class="card">
      <strong>Add it to your calendar</strong>
      <p style="margin:.5em 0 1em; color:var(--muted)">One tap on mobile, or use the link below in any calendar app.</p>
      <a class="btn" href="{google_add}">Add to Google Calendar</a>
      <a class="btn alt" href="{ics_webcal}">Add to Apple Calendar</a>
      <span class="url">Or paste this feed URL manually:<br><code>{ics_https}</code></span>
    </div>

    <div class="card">
      <strong>Add manually in Google Calendar (desktop)</strong>
      <ol>
        <li>Open Google Calendar \u2192 <em>Other calendars</em> \u2192 <em>+</em> \u2192 <em>From URL</em></li>
        <li>Paste the feed URL above and click <em>Add calendar</em></li>
        <li>It stays in sync automatically \u2014 no re-downloading</li>
      </ol>
    </div>

    <footer>
      Subscribed calendars refresh on the app's own schedule (Google: up to ~24h; Apple: adjustable).
      Knockout matchups fill in as the bracket is decided.
    </footer>
  </div>
</body>
</html>
"""


def main():
    with open(os.path.join(ROOT, "schedule.json"), encoding="utf-8") as f:
        data = json.load(f)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, ICS_NAME), "w", encoding="utf-8") as f:
        f.write(build_ics(data))
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_index(data))
    print(f"Built {OUT_DIR}/{ICS_NAME} and index.html ({len(data['matches'])} matches)")
    print(f"Feed URL will be: {pages_base_url()}/{ICS_NAME}")


if __name__ == "__main__":
    main()
