"""
app.py — Core Flask Initialization Entry Point
"""
from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from config import Config
from admin import admin_bp, get_conn
from user_bp import user_bp
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pyodbc

app = Flask(__name__)
app.config.from_object(Config)

# Register functional blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')

# ───────────────────────────────────────────────────────────────────
# AUTH BLUEPRINT DEFINITION & ROUTES
# ───────────────────────────────────────────────────────────────────
auth_bp = Blueprint('auth', __name__)
#User blueprint definations and routes
app.register_blueprint(user_bp, url_prefix='/user')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registers a new farmer account."""
    if request.method == 'GET':
        return render_template('register.html')

    full_name     = request.form.get('full_name', '').strip()
    cnic          = request.form.get('cnic', '').strip()
    phone_number  = request.form.get('phone_number', '').strip()
    email         = request.form.get('email', '').strip()
    password      = request.form.get('password', '').strip()

    if not all([full_name, cnic, phone_number, email, password]):
        flash("All fields are required.", "danger")
        return render_template('register.html')

    password_hash     = generate_password_hash(password)
    registration_date = datetime.now().date()

    try:
        conn   = get_conn()
        cursor = conn.cursor()

        # Check if CNIC already exists
        cursor.execute("SELECT farmer_id FROM Farmer WHERE cnic = ?", cnic)
        if cursor.fetchone():
            conn.close()
            flash("An account with this CNIC already exists. Please log in.", "warning")
            return redirect(url_for('auth.login'))

        # Insert new farmer
        cursor.execute("""
            INSERT INTO Farmer (full_name, phone_number, email, cnic, registration_date, password_hash, role)
            OUTPUT INSERTED.farmer_id
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, full_name, phone_number, email, cnic, registration_date, password_hash, 'farmer')

        row = cursor.fetchone()
        conn.commit()

        if row:
            session['temp_farmer_id'] = row[0]

        conn.close()
        flash(f'Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    except Exception as e:
        print(f"[REGISTER ERROR] {e}")
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticates a farmer using CNIC and password."""
    if request.method == 'GET':
        return render_template('login.html')

    cnic     = request.form.get('cnic', '').strip()
    password = request.form.get('password', '').strip()

    if not cnic or not password:
        flash("CNIC and password are required.", "danger")
        return render_template('login.html')

    try:
        conn   = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT farmer_id, full_name, password_hash, role
            FROM Farmer
            WHERE cnic = ?
        """, cnic)

        row = cursor.fetchone()
        conn.close()

        if not row:
            flash("No account found with that CNIC.", "danger")
            return render_template('login.html')

        farmer_id, full_name, password_hash, role = row

        if not check_password_hash(password_hash, password):
            flash("Incorrect password. Please try again.", "danger")
            return render_template('login.html')

        # Populate session
        session['farmer_id'] = farmer_id
        session['full_name'] = full_name
        session['role'] = role

        if role == 'admin':
            return redirect('/admin/dashboard')
        else:
            return redirect(url_for('user.dashboard'))   

    except Exception as e:
        print(f"[LOGIN ERROR] {e}")
        flash(f"Database error: {str(e)}", "danger")
        return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Logs out the current user and clears the session."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

# Register the authentication blueprint to the app
app.register_blueprint(auth_bp)


# ───────────────────────────────────────────────────────────────────
# ROOT & APPLICATION ROUTES
# ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# @app.route("/dashboard")
# def dashboard():
#     farmer_id = session.get("farmer_id")

#     if not farmer_id:
#         flash("Please log in to access the dashboard.", "warning")
#         return redirect(url_for('auth.login'))

#     try:
#         conn = get_conn()
#         cursor = conn.cursor()

#         # 1. Fetch Farmer Data using SQL
#         cursor.execute("SELECT farmer_id, full_name, email, phone_number FROM Farmer WHERE farmer_id = ?", farmer_id)
#         farmer_row = cursor.fetchone()
        
#         # Convert row to a dictionary for easy template usage
#         farmer = None
#         if farmer_row:
#             farmer = {
#                 "id": farmer_row[0],
#                 "full_name": farmer_row[1],
#                 "email": farmer_row[2],
#                 "phone_number": farmer_row[3]
#             }

#         # 2. Fetch Associated Farms using SQL
#         cursor.execute("SELECT farm_id, farm_name, location FROM Farm WHERE farmer_id = ?", farmer_id)
#         farm_rows = cursor.fetchall()
        
#         # Convert rows to a list of dictionaries
#         farms = []
#         for row in farm_rows:
#             farms.append({
#                 "id": row[0],
#                 "name": row[1],
#                 "location": row[2]
#             })

#         #If farm_id is null, take the users to the farm and soil registration page
#         if not farms: 
#             return redirect('user_Farm.html')

#         conn.close()
#         return render_template("user_dashboard.html", farmer=farmer, farms=farms)

#     except Exception as e:
#         print(f"[DASHBOARD ERROR] {e}")
#         flash("Could not load dashboard data.", "danger")
#         return render_template("user_dashboard.html", farmer=None, farms=[])


# ───────────────────────────────────────────────────────────────────
# RUNTIME ENGINE ENTRY POINT
# ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)