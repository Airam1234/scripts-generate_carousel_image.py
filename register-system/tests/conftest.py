import re
from datetime import date, datetime, time

import pytest

from app import create_app
from app.extensions import db
from app.models import Cohort, Course, Learner, Role, User
from app.services import place_learner

PASSWORD = "CorrectHorseBattery1"


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "test",
        "WTF_CSRF_ENABLED": False,
        "ENABLE_SCHEDULER": False,
    })
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def make_user(email, role, name=None):
    u = User(email=email, name=name or email.split("@")[0].title(), role=role, must_change_password=False)
    u.set_password(PASSWORD)
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def people(app):
    return {
        "admin": make_user("admin@x.org", Role.ADMIN),
        "tutor": make_user("tutor@x.org", Role.TUTOR),
        "tutor2": make_user("tutor2@x.org", Role.TUTOR),
        "pastoral": make_user("pastoral@x.org", Role.PASTORAL),
        "inspector": make_user("inspector@x.org", Role.INSPECTOR),
    }


@pytest.fixture
def cohort(people):
    course = Course.query.filter_by(name="Business Administrator").first()
    c = Cohort(name="BA L3 Sep", course=course, tutor=people["tutor"], start_date=date(2026, 9, 17))
    db.session.add(c)
    db.session.flush()
    learners = []
    for first, last in [("Ann", "Able"), ("Ben", "Baker"), ("Cat", "Cole")]:
        l = Learner(first_name=first, last_name=last, cohort=c, tutor=people["tutor"], start_date=date(2026, 9, 17))
        db.session.add(l)
        db.session.flush()
        place_learner(l, people["tutor"], c, datetime.combine(date(2026, 9, 17), time()), "Enrolled", people["admin"])
        learners.append(l)
    db.session.commit()
    c.test_learners = learners
    return c


def login(client, email, password=PASSWORD):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=False)


def freeze(monkeypatch, when):
    """Pin 'now' everywhere it is imported."""
    import app.timeutil as tu
    for mod in ["app.timeutil", "app.notifications", "app.views.sessions", "app.views.main", "app.views.learners",
                "app.views.pastoral", "app.views.auth", "app.views.admin", "app.reports", "app.services",
                "app.models", "app"]:
        m = __import__(mod, fromlist=["x"])
        if hasattr(m, "now"):
            monkeypatch.setattr(m, "now", lambda: when)
    monkeypatch.setattr(tu, "today", lambda: when.date())
