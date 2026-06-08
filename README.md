# FIFA World Cup 2026 — Self-Hosted Pacific-Time Calendar

A subscribable, auto-syncing calendar feed for all 104 World Cup 2026 matches,
with every kickoff in **Pacific time**. You host it for free on GitHub Pages and
share one link with friends — everyone's calendar stays in sync on its own.

```
schedule.json   ← the source of truth (edit this; it's just data)
build_calendar.py  ← turns schedule.json into the feed + landing page (stdlib only)
site/              ← generated output (worldcup.ics + index.html) served by Pages
.github/workflows/build.yml  ← rebuilds & redeploys automatically
```

## One-time setup (about 5 minutes)

1. **Create a new GitHub repo** (public is simplest for Pages) and push these files
   to the `main` branch.
   ```bash
   git init && git add . && git commit -m "World Cup 2026 calendar"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
   git push -u origin main
   ```
2. In the repo: **Settings → Pages → Build and deployment → Source: GitHub Actions.**
3. The workflow runs automatically. When it finishes (Actions tab → green check),
   your feed is live at:
   ```
   https://YOUR-USERNAME.github.io/YOUR-REPO/worldcup.ics
   ```
   and a shareable landing page at `https://YOUR-USERNAME.github.io/YOUR-REPO/`.

## Share it with friends

Just send them the **landing page link** (`https://YOUR-USERNAME.github.io/YOUR-REPO/`).
It has one-tap "Add to Google Calendar" / "Add to Apple Calendar" buttons plus the
raw feed URL. Each friend subscribes once; everyone then auto-syncs from the same
source — nobody ever re-downloads anything.

To add it yourself in Google Calendar on desktop:
**Other calendars → + → From URL → paste the `worldcup.ics` URL.**

## Updating the knockout teams (or anything else)

Everything lives in `schedule.json`. When the bracket fills in, edit the relevant
matches — change `"home"` and `"away"` from `"TBD"` to the real teams — and push:

```bash
# edit schedule.json, then:
git commit -am "Fill in Round of 32 matchups"
git push
```

The Action rebuilds and redeploys within a minute, and every subscriber picks up
the change on their app's next refresh. **You never touch the .ics file by hand**;
it's regenerated from the JSON each time.

To test the build locally first (optional):
```bash
python build_calendar.py   # writes site/worldcup.ics — open it to check
```

## Notes & limits

- **Times are anchored to America/Los_Angeles**, so they display as Pacific in
  every app regardless of the viewer's own timezone. Opener: Mexico vs South Africa,
  2:00 PM PT, June 11. Final: 12:00 PM PT, Sunday July 19.
- **Sync delay is the app's, not yours.** Google Calendar polls subscribed feeds on
  its own schedule (often several hours, up to ~24h). Apple Calendar lets you set the
  refresh interval. This is normal for all calendar subscriptions.
- **Knockout entries show the round name** ("Round of 32," etc.) until you fill in
  the teams. Slots, dates, times, and venues are already correct.
- **Match length** defaults to 2 hours (`match_duration_minutes` in schedule.json).

## Optional: fully automatic knockout updates

The workflow already runs on a 12-hour cron. If you want the bracket to resolve with
zero manual edits, add a step to `build_calendar.py` that fetches results from a
sports data API and rewrites the `TBD` slots before building the .ics. Good free-tier
options include football-data.org and TheSportsDB. (Left out by default so the feed
has no external dependencies and can't silently break — happy to wire it in if you
want it.)
