# config.py
# ─────────────────────────────────────────────────
# This file centralizes ALL configuration for the app.
# Why? So you never hardcode settings inside app.py or models.py.
# In real companies, config files are loaded based on environment:
# development, testing, production. We build that habit here.
# ─────────────────────────────────────────────────

import os

# os.path.abspath(__file__)
#   → gives the full path of THIS file (config.py)
# os.path.dirname(...)
#   → gives the FOLDER containing config.py
# This means BASE_DIR = the root of your project folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ── SECURITY ──────────────────────────────────
    # SECRET_KEY is used by Flask to:
    #   1. Sign session cookies (so users can't tamper with them)
    #   2. Protect against CSRF attacks
    # In production, this must be a long random string stored
    # in an environment variable — NEVER hardcoded.
    # os.environ.get(...) checks for an env variable first.
    # If not found, it falls back to the string after the comma.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sla-dev-secret-key-2024')

    # ── DATABASE ──────────────────────────────────
    # SQLALCHEMY_DATABASE_URI tells Flask-SQLAlchemy WHERE the DB is.
    # 'sqlite:///' is the prefix for SQLite file-based databases.
    # os.path.join(BASE_DIR, 'instance', 'learning.db')
    #   → builds the path: /your/project/instance/learning.db
    # Using os.path.join is safer than string concatenation
    # because it handles / vs \ differences across OS.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        BASE_DIR, 'instance', 'learning.db'
    )

    # ── SQLALCHEMY SETTINGS ───────────────────────
    # SQLALCHEMY_TRACK_MODIFICATIONS:
    # If True, SQLAlchemy fires extra signals every time
    # a DB object changes. We don't need that — it wastes memory.
    # Setting it to False also removes an annoying warning.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── DEBUG MODE ────────────────────────────────
    # DEBUG = True means Flask will:
    #   1. Show detailed error pages in the browser
    #   2. Auto-restart when you save a file
    # NEVER set this to True in production.
    # We default to True for development convenience.
    DEBUG = True


class ProductionConfig(Config):
    # Inherits everything from Config but overrides unsafe settings.
    # You won't use this now, but having it shows professional awareness.
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in env


class TestingConfig(Config):
    # Used for running automated tests later.
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # DB lives in RAM only


# ── CONFIG SELECTOR ───────────────────────────────
# This dictionary lets app.py select a config by name.
# Example in app.py: app.config.from_object(config['development'])
config = {
    'development': Config,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': Config
}