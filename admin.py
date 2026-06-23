from flask import (
    Flask, Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify
)
import hashlib
from datetime import datetime
from functools import wraps
from config import Config

# ───────────────────────────────────────────────────────────────────
# 2. BLUEPRINT REGISTRATION & SECURITY MIDDLEWARE
# ───────────────────────────────────────────────────────────────────
admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder='frontend/templates'
)

def admin_required(f):
    """View-level decorator ensuring current session profile carries admin clearance."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.before_request
def require_admin():
    """Global blueprint interception gate blocking unauthorized requests explicitly."""
    # Exclude basic static assets if necessary, otherwise gate everything matching prefix
    if session.get('role') != 'admin':
        flash('Access denied. Administrator privileges required.', 'danger')
        return redirect(url_for('auth.login'))

def get_conn():
    """Direct proxy utility to retrieve live execution contexts."""
    return Config.get_db_connection()

# At the bottom of admin.py, after admin_bp is defined
from backend.routes import dashboard  # noqa: F401 — registers routes onto admin_bp
from backend.routes import farmers   # noqa: F401 — registers routes onto admin_bp
from backend.routes import farm     # noqa: F401 — registers routes onto admin_bp
from backend.routes import crop     # noqa: F401 — registers routes onto admin_bp
from backend.routes import advisory  # noqa: F401 — registers routes onto admin_bp
from backend.routes import location
from backend.routes import weather
from backend.routes import soil
from backend.routes import report

