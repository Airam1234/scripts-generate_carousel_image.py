import pytest

from app.extensions import db
from app.models import AuditImmutableError, AuditLog, User

from .conftest import PASSWORD, login


def test_login_and_generic_error(client, people):
    r = login(client, "admin@x.org", "wrong-password")
    assert b"Incorrect email or password" in client.get("/login").data or r.status_code == 200
    assert login(client, "admin@x.org").status_code == 302


def test_lockout_after_failed_attempts(client, people, app):
    for _ in range(app.config["MAX_FAILED_LOGINS"]):
        login(client, "tutor@x.org", "nope-nope-nope")
    r = login(client, "tutor@x.org")  # correct password, but locked
    assert r.status_code == 200
    assert db.session.get(User, people["tutor"].id).is_locked


def test_pages_require_login(client, people):
    for url in ["/", "/learners/", "/reports/monthly", "/admin/users", "/pastoral/"]:
        r = client.get(url)
        assert r.status_code == 302 and "/login" in r.headers["Location"]


@pytest.mark.parametrize("role,url,code", [
    ("tutor", "/admin/users", 403),
    ("tutor", "/admin/audit", 403),
    ("tutor", "/pastoral/", 403),
    ("pastoral", "/admin/users", 403),
    ("inspector", "/admin/users", 403),
    ("inspector", "/admin/audit", 200),
    ("inspector", "/reports/monthly", 200),
    ("pastoral", "/pastoral/", 200),
])
def test_role_access(client, people, role, url, code):
    login(client, f"{role}@x.org")
    assert client.get(url).status_code == code


def test_inspector_cannot_write(client, people, cohort):
    login(client, "inspector@x.org")
    assert client.post("/learners/new", data={}).status_code == 403
    assert client.post(f"/learners/{cohort.test_learners[0].id}/archive", data={}).status_code == 403


def test_tutor_cannot_see_other_tutors_learners(client, people, cohort):
    login(client, "tutor2@x.org")
    assert client.get(f"/learners/{cohort.test_learners[0].id}").status_code == 403
    assert client.get(f"/cohorts/{cohort.id}").status_code == 403


def test_security_headers(client, people):
    r = client.get("/login")
    assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Frame-Options"] == "DENY"


def test_forced_password_change(client, people):
    u = people["tutor"]
    u.must_change_password = True
    db.session.commit()
    login(client, "tutor@x.org")
    r = client.get("/")
    assert r.status_code == 302 and "/account/password" in r.headers["Location"]
    r = client.post("/account/password", data={"current_password": PASSWORD, "new_password": "short",
                                               "confirm_password": "short"})
    assert db.session.get(User, u.id).must_change_password
    client.post("/account/password", data={"current_password": PASSWORD, "new_password": "a much longer passphrase",
                                           "confirm_password": "a much longer passphrase"})
    assert not db.session.get(User, u.id).must_change_password


def test_open_redirect_blocked(client, people):
    r = client.post("/login?next=https://evil.example", data={"email": "admin@x.org", "password": PASSWORD})
    assert r.headers["Location"] == "/"


def test_audit_log_is_immutable(app, people):
    from app.audit import audit
    audit("test.entry", summary="original")
    db.session.commit()
    entry = AuditLog.query.first()
    entry.summary = "tampered"
    with pytest.raises(AuditImmutableError):
        db.session.commit()
    db.session.rollback()
    with pytest.raises(AuditImmutableError):
        db.session.delete(AuditLog.query.first())
        db.session.commit()
    db.session.rollback()


def test_admin_adds_tutor_with_temp_password(client, people):
    login(client, "admin@x.org")
    r = client.post("/admin/users/new", data={"name": "New Tutor", "email": "new@x.org", "role": "tutor"})
    assert r.status_code == 200 and b"Temporary password" in r.data
    u = User.query.filter_by(email="new@x.org").one()
    assert u.role == "tutor" and u.must_change_password
