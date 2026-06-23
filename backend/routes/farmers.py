from flask import render_template, flash, redirect, url_for, request
from admin import admin_bp, get_conn
import pyodbc
import hashlib
from datetime import datetime

@admin_bp.route('/farmers', methods=['GET'])
def farmers():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT farmer_id, full_name, phone_number, email, cnic, registration_date
            FROM Farmer
            ORDER BY registration_date DESC
        """)
        farmers_list = [
            {
                'farmer_id':  r[0],
                'name':       r[1],                                              # HTML uses farmer.name
                'phone':      r[2],                                              # HTML uses farmer.phone
                'email':      r[3],
                'cnic':       r[4],
                'created_at': r[5].strftime('%Y-%m-%d') if r[5] else '—',       # HTML uses farmer.created_at
            }
            for r in cursor.fetchall()
        ]
        return render_template('farmers.html', farmers=farmers_list)
    except pyodbc.Error as e:
        print(f"DATABASE ERROR: {str(e)}")
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('farmers.html', farmers=[])
    finally:
        cursor.close()
        conn.close()


@admin_bp.route('/farmers', methods=['POST'])
def farmers_create():
    data     = request.form
    name     = data.get('name', '').strip()       # HTML form field is 'name'
    email    = data.get('email', '').strip()
    phone    = data.get('phone', '').strip()
    # address not in DB schema, ignore for now

    if not name or not email:
        flash('Name and email are required.', 'warning')
        return redirect(url_for('admin.farmers'))

    # Generate a default password hash since HTML form doesn't have password field
    default_password = 'changeme123'
    password_hash = hashlib.sha256(default_password.encode()).hexdigest()
    reg_date = datetime.utcnow().date()

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Farmer (full_name, phone_number, email, registration_date, password_hash, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, email, reg_date, password_hash, 'farmer'))
        conn.commit()
        flash(f'Farmer "{name}" created successfully.', 'success')
    except pyodbc.IntegrityError as e:
        flash(f'Duplicate entry (email already exists?): {str(e)}', 'danger')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.farmers'))


@admin_bp.route('/farmers/<int:farmer_id>', methods=['POST'])
def farmer_update(farmer_id):
    data  = request.form
    name  = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    cnic  = data.get('cnic', '').strip()
    # address not in DB schema, ignore for now

    if not name:
        flash('Name is required.', 'warning')
        return redirect(url_for('admin.farmers'))

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Farmer
            SET full_name = ?, phone_number = ?, email = ?, cnic = ?
            WHERE farmer_id = ?
        """, (name, phone, email, cnic, farmer_id))
        conn.commit()
        flash(f'Farmer updated successfully.', 'success')
    except pyodbc.IntegrityError as e:
        flash(f'Integrity error: {str(e)}', 'danger')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.farmers'))


@admin_bp.route('/farmers/delete/<int:farmer_id>', methods=['POST'])
def farmer_delete(farmer_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Farmer WHERE farmer_id = ?", (farmer_id,))
        conn.commit()
        flash('Farmer deleted successfully.', 'success')
    except pyodbc.IntegrityError:
        flash('Cannot delete: farmer has associated farm records. Remove farms first.', 'danger')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.farmers'))