# Scheduling and headless runs

## What a skill can and cannot do

A skill is a set of instructions and tools that Claude reads when it is already running. It does not have a scheduler and cannot wake itself up on the 1st of the month. The timer has to come from the operating system or a CI service, and it invokes Claude Code headlessly.

Equally, nothing here sends email on its own. Deciding to send is a human act, and it should stay one — see "Why not fully unattended" below.

## Cadence

**Draft on the 1st. Review. Send on the 5th.**

The **5th of the month is the standing send date** — every issue goes out on the 5th. The scheduled job produces the two files by the 1st and tells a human they are ready. Airam or Jeannette reads the draft, fills any figure placeholder, and it sends on the 5th. That leaves four working days of slack for a bank holiday, a missing statistic, or an awareness date that turns out to have moved.

If the 5th falls on a weekend or bank holiday, send on the 5th anyway unless told otherwise — the recipients read it when they read it.

## macOS and Linux — cron

Draft at 08:00 on the 1st of each month:

```cron
0 8 1 * * cd /path/to/newsletter && /usr/local/bin/claude -p "Produce this month's In The Loop learner issue using the in-the-loop-newsletter skill. Use the content in inbox/this-month.md. Leave a visible placeholder for any figure I have not supplied and list them at the end." >> logs/newsletter.log 2>&1
```

Notes:
- Use the absolute path to `claude`. Cron does not inherit your shell's PATH.
- `cd` into the working directory first so relative paths resolve.
- Keep the log. When a run fails at 08:00 on a Sunday you will want it.

## macOS — launchd

Cron works on macOS but launchd survives sleep better. Save as `~/Library/LaunchAgents/uk.co.coreed.newsletter.plist` and load with `launchctl load`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
  <key>Label</key><string>uk.co.coreed.newsletter</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string><string>-lc</string>
    <string>cd /path/to/newsletter && claude -p "Produce this month's In The Loop learner issue using the in-the-loop-newsletter skill."</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Day</key><integer>1</integer><key>Hour</key><integer>8</integer></dict>
  <key>StandardOutPath</key><string>/path/to/newsletter/logs/newsletter.log</string>
  <key>StandardErrorPath</key><string>/path/to/newsletter/logs/newsletter.err</string>
</dict></plist>
```

## Windows — Task Scheduler

```powershell
$action  = New-ScheduledTaskAction -Execute "claude" `
           -Argument '-p "Produce this month''s In The Loop learner issue using the in-the-loop-newsletter skill."' `
           -WorkingDirectory "C:\newsletter"
$trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 8am
Register-ScheduledTask -TaskName "InTheLoop draft" -Action $action -Trigger $trigger
```

## GitHub Actions

Useful if no one machine is reliably on. Requires `ANTHROPIC_API_KEY` as a repository secret.

```yaml
name: In The Loop monthly draft
on:
  schedule:
    - cron: "0 8 1 * *"   # 08:00 UTC on the 1st
  workflow_dispatch:

jobs:
  draft:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "22" }
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: npm install -g @anthropic-ai/claude-code
      - run: bash .claude/skills/in-the-loop-newsletter/scripts/setup.sh
      - name: Draft the issue
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude -p "Produce this month's In The Loop learner issue using the in-the-loop-newsletter skill. Content is in inbox/this-month.md. Flag any missing figures."
      - uses: actions/upload-artifact@v4
        with:
          name: in-the-loop-draft
          path: output/
```

GitHub's scheduled runs can lag by a few minutes to an hour at busy times, and are disabled automatically on repositories with no activity for 60 days. Both are fine for a monthly draft with four days of slack; neither would be fine for a same-day send.

## Feeding content in

The job needs somewhere to look for this month's material. The simplest arrangement that works: a file at `inbox/this-month.md` that the team adds to during the month — awareness dates, results, diary entries, anything the safeguarding team wants raised. The scheduled prompt points at it.

If it is empty or missing, the run should still produce a draft from the standing sections and say clearly that no content was supplied.

The **results figures are the exception** — they do not come from the inbox. They live in the SLT monthly data pack on SharePoint, reached through the Microsoft 365 connector. `references/data-sources.md` gives the library, folder, filename pattern and which cells to read. A headless run needs that connector authenticated, or it should leave the figures as placeholders and flag them.

## Notifying a human

Add a step after the draft. Any of these work:

```bash
# macOS desktop notification
osascript -e 'display notification "In The Loop draft ready in output/" with title "CoreEd"'

# Email via a configured local mailer
printf 'Subject: In The Loop draft ready\n\nFiles are in output/.\n' | sendmail airam@CoreEd.co.uk

# Slack, if a webhook is configured
curl -s -X POST -H 'Content-type: application/json' \
  --data '{"text":"In The Loop draft ready for review"}' "$SLACK_WEBHOOK_URL"
```

## Why not fully unattended

It is technically possible to have the job attach the files and mail them to the whole learner list. Resist it.

These newsletters carry safeguarding contacts, crisis helplines and governance figures. The realistic failure modes are a helpline that has changed number, an awareness date that moved, a `[XX%]` placeholder that nobody filled, or a cohort statistic that turns out to be wrong. Each of those is trivial to catch in a ten-minute read and genuinely damaging to send to several hundred learners.

The 1st-to-5th window exists so that a human check is comfortable rather than rushed. Keep the send manual.
