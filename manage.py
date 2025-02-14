# manage.py


import os
import subprocess
import sys
import unittest

import coverage
from flask.cli import FlaskGroup

from project.server import create_app, db
from project.server.models import User

app = create_app()
cli = FlaskGroup(create_app=create_app)

# code coverage
COV = coverage.coverage(
    branch=True,
    include="project/*",
    omit=[
        "project/tests/*",
        "project/server/config.py",
        "project/server/*/__init__.py",
    ],
)
COV.start()


@cli.command()
def create_db():
    """Creates the database."""
    from sqlalchemy.exc import OperationalError

    try:
        # Ensure the directory exists
        os.makedirs('/usr/src/app/data', exist_ok=True)
        print(f"Creating database at: {os.getenv('SQLALCHEMY_DATABASE_URI')}")
        db.drop_all()
        db.create_all()
        db.session.commit()
    except OperationalError as e:
        print(f"Error creating the database: {e}")


@cli.command()
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@cli.command()
def create_admin():
    """Creates the admin user."""
    db.session.add(User(user_name="Rian", password="admin", admin=True))
    db.session.commit()


@cli.command()
def create_data():
    """Creates sample data."""
    pass


@cli.command()
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover("project/tests", pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover("project/tests")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        COV.html_report()
        COV.erase()
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
def flake():
    """Runs flake8 on the project."""
    subprocess.run(["flake8", "project"])


if __name__ == "__main__":
    cli()
