# Apprenticeship Register System

A cloud-hosted web app for taking and reporting attendance at apprenticeship
sessions. Tutors sign in to mark registers. Pastoral Support are sent a link
to follow up anyone who has not arrived 15 minutes after the start. Managers
run monthly attendance reports, and inspectors can be given time-limited,
read-only access.

Courses loaded on first start (edit them under **Courses**; add the IfATE
standard reference for each one):

| Course | Level |
|---|---|
| Business Administrator | 3 |
| Admin Assistant | 2 |
| Operations / Departmental Manager | 5 |
| Team Leader / Supervisor | 3 |
| Pharmacy Assistant | 2 |
| Pharmacy Technician | 3 |

## What it does

| Need | How the system handles it |
|---|---|
| Assign cohorts to tutors | Each cohort has a tutor. Changing the tutor asks for a reason and can move the cohort's learners and future sessions to the new tutor, with every move recorded. |
| Tutors mark attendance | Tutors see today's sessions on their dashboard. For each learner they mark **Present / Late (minutes) / Absent / Authorised absence**, and can add a note. The register opens 30 minutes before the start. Tutors can edit it for 7 days; after that only an administrator can change it. |
| Delivery calendar | **First day of learning** (new starts) must be in weeks 3–4 (15th–28th). **Monthly sessions** must be in week 1 (1st–7th). **Additional sessions** can be on any date. Tutors cannot schedule outside these windows. Administrators can, but must give an override reason, which is kept. *Schedule monthly sessions* creates a cohort's sessions for up to 36 months in one go. |
| 15-minute pastoral alert | 15 minutes after a session starts, anyone not marked Present or Late is recorded as absent and raised as a pastoral alert. Pastoral Support get one email per session with a link to the follow-up page (login required). They log each call, text or email and its outcome, including safeguarding referrals to the DSL. If the tutor later marks the learner Late/Present, the alert closes itself. |
| Reassign a learner, keep the audit trail | *Reassign tutor / cohort* needs a reason and an effective date. The old placement is closed, not overwritten, so the learner's full tutor and cohort history is shown on their record. Past registers keep the name of the tutor who marked them. |
| Monthly attendance reports | Overall %, a six-month trend, and breakdowns by course, tutor and cohort. Also: learners below the target (90% by default), whether each register was done within 15 minutes, cancelled sessions and pastoral outcomes. Exports to CSV, or print to PDF. Tutors only see their own delivery. |
| Archive leavers | *Archive* records the leaving date, the reason (completed, withdrawn, transferred, employment ended, other) and notes. The learner drops off future registers, but all their records stay and still appear in reports. An administrator can restore them, with a reason. |
| Tutors added on the back end | **Staff → Add staff member** creates tutor, pastoral, admin or inspector accounts. It shows a one-time temporary password, which must be changed at first sign-in. |
| Secure | See [Security](#security). |

## Supporting an Ofsted inspection

The system is built to give inspectors evidence under the Education Inspection
Framework (EIF) and the Further Education and Skills handbook, mainly on
attendance, learner engagement, and personal development and safeguarding
follow-up. It does not guarantee a judgement. Ofsted looks at how you use the
data, not just whether you have it.

* **Inspector accounts**: create a user with the *Inspector (read-only)* role
  and set an expiry date for the inspection. Inspectors can see reports,
  learner records, the pastoral log and the audit trail. They cannot change
  anything, and their access is logged.
* **Learner journey**: each learner's page shows every mark, who recorded it
  and when, their full tutor and cohort history, and every pastoral contact.
* **Integrity**: the audit trail is append-only; the app refuses to edit or
  delete entries. Changing a register after it has been submitted needs a
  reason. Automatic absences are labelled *Recorded absent by the system*.
* **Monitoring and action**: the monthly report shows whether attendance
  concerns are spotted (learners below target, late registers) and acted on
  (pastoral outcomes).
* **ULN** is stored so records can be matched against the ILR.

## Running it locally

```bash
cd register-system
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
flask --app wsgi seed-demo        # optional demo data (password DemoPassword123!)
# or: flask --app wsgi create-admin
flask --app wsgi run
```

Open http://localhost:5000. Demo logins: `admin@example.org`,
`tutor1@example.org`, `pastoral@example.org`, `inspector@example.org`.

Run the tests with `python -m pytest`.

## Deploying to the cloud

The app is a standard Python web app. It runs on any host that can run a
Docker container or a Python app, such as Azure App Service, AWS, Render,
Railway or Google Cloud Run. Use a managed **PostgreSQL** database with
automatic backups turned on, hosted in the UK or EEA for UK GDPR.

1. Create a PostgreSQL database and note its connection URL.
2. Build and deploy the container: `docker build -t registers register-system`.
3. Set the environment variables listed in `.env.example`. The essentials are:
   * `APP_ENV=production`
   * `SECRET_KEY`: a long random value, e.g. `python -c "import secrets; print(secrets.token_hex(32))"`
   * `DATABASE_URL`
   * `BASE_URL`: the public https address, used in pastoral emails
   * `TRUST_PROXY=1` when running behind the host's HTTPS load balancer
   * `SMTP_*` / `MAIL_FROM` / `PASTORAL_EMAIL`: for Microsoft 365 use
     `smtp.office365.com`, port 587, and a licensed mailbox with SMTP AUTH turned on
4. Create the first administrator from the host's console:
   `flask --app wsgi create-admin`
5. Sign in, add your tutors and pastoral staff under **Staff**, then create
   cohorts, learners and sessions.

Tables are created automatically on first start.

**Pastoral alerts timing.** Each web worker checks every 60 seconds for
sessions that have passed the 15-minute mark. Sessions are claimed
atomically, so several workers never send duplicates. If your host scales to
zero when idle, set `ENABLE_SCHEDULER=0` and run
`flask --app wsgi process-alerts` every minute from the host's scheduler
instead.

If SMTP is not configured, alerts still appear under **Pastoral** and every
email is recorded under `/admin/emails`.

## Security

* Passwords are hashed with a salted, slow algorithm (scrypt/PBKDF2 via Werkzeug). The minimum length is 12 characters, and common passwords are rejected.
* After 5 failed sign-ins the account is locked for 15 minutes. Wrong emails and wrong passwords show the same error message.
* Temporary passwords are issued by an administrator and must be changed at first sign-in. A password change or deactivation ends that user's existing sessions.
* Users are signed out after 30 minutes of inactivity. Cookies are HttpOnly, SameSite=Lax, and Secure in production.
* Every form is protected against CSRF.
* A strict Content-Security-Policy is set (no inline or third-party scripts), along with clickjacking protection and HSTS.
* Access is role-based and checked per record. Tutors only see their own cohorts, learners and registers. Inspectors are read-only and can be time-limited.
* Everything is audited: sign-ins (including failures), every change to users, cohorts, learners, sessions and registers, pastoral contacts and report exports. Audit entries cannot be edited or deleted.
* Pastoral emails contain no learner names, only a link that requires a login.
* CSV exports are protected against spreadsheet formula injection.

**Recommended before go-live:**
* Put the app behind your Microsoft 365 / Entra ID sign-in (for example
  Azure App Service "Easy Auth") to add multi-factor authentication.
* Enable daily database backups and test a restore.
* Record the system in your data-protection records (ROPA/DPIA) and set a
  retention period for learner records that fits your funding agreement.
* Commission a penetration test.

## Settings

| Variable | Default | Purpose |
|---|---|---|
| `PASTORAL_GRACE_MINUTES` | 15 | Minutes after the start before absentees go to Pastoral Support |
| `ATTENDANCE_THRESHOLD` | 90 | Target % used to flag learners in reports |
| `REGISTER_OPENS_MINUTES_BEFORE` | 30 | How early a tutor can start marking |
| `TUTOR_EDIT_WINDOW_DAYS` | 7 | How long tutors can amend a register |
| `IDLE_TIMEOUT_MINUTES` | 30 | Automatic sign-out after inactivity |
| `MAX_FAILED_LOGINS` / `LOCKOUT_MINUTES` | 5 / 15 | Account lockout |
| `TIMEZONE` | Europe/London | All times are stored and shown in UK time |

## Project layout

```
app/
  models.py         data model (users, courses, cohorts, learners, placements,
                    sessions, attendance, pastoral alerts, audit log)
  notifications.py  15-minute pastoral check and email
  reports.py        monthly attendance calculations
  services.py       reassignment and cohort tutor changes
  timeutil.py       delivery calendar rules
  security.py       roles, record-level access, password policy
  views/            pages (auth, dashboard, admin, cohorts, learners,
                    sessions/registers, pastoral, reports)
  templates/, static/
tests/              pytest suite
```
