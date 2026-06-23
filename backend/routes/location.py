from flask import render_template, flash, redirect, url_for, request
from admin import admin_bp, get_conn
import pyodbc

@admin_bp.route('/location', methods=['GET'])
def location():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT location_id, village_name, district, province,
                   latitude, longitude, altitude
            FROM Location
            ORDER BY province, village_name
        """)
        locations = [
            {
                'location_id': r[0],
                'name':        r[1],
                'district':    r[2] or '—',
                'province':    r[3] or '—',
                'latitude':    float(r[4]) if r[4] is not None else 0.0,
                'longitude':   float(r[5]) if r[5] is not None else 0.0,
                'altitude':    float(r[6]) if r[6] is not None else None,
            }
            for r in cursor.fetchall()
        ]
        return render_template('location.html', locations=locations)
    except pyodbc.Error as e:
        print(f"DATABASE ERROR: {str(e)}")
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('location.html', locations=[])
    finally:
        cursor.close()
        conn.close()


@admin_bp.route('/location', methods=['POST'])
def location_create():
    data      = request.form
    name      = data.get('name', '').strip()
    district  = data.get('district', '').strip()
    province  = data.get('province', '').strip()

    try:
        latitude  = float(data.get('latitude', 0))
        longitude = float(data.get('longitude', 0))
        altitude  = float(data.get('altitude')) if data.get('altitude') else None
    except ValueError:
        flash('Latitude and longitude must be valid decimals.', 'warning')
        return redirect(url_for('admin.location'))

    if not name:
        flash('Village name is required.', 'warning')
        return redirect(url_for('admin.location'))

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Location (village_name, district, province, latitude, longitude, altitude)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, district, province, latitude, longitude, altitude))
        conn.commit()
        flash(f'Location "{name}" added successfully.', 'success')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.location'))


@admin_bp.route('/location/update/<int:location_id>', methods=['POST'])
def location_update(location_id):
    data      = request.form
    name      = data.get('name', '').strip()
    district  = data.get('district', '').strip()
    province  = data.get('province', '').strip()

    try:
        latitude  = float(data.get('latitude', 0))
        longitude = float(data.get('longitude', 0))
        altitude  = float(data.get('altitude')) if data.get('altitude') else None
    except ValueError:
        flash('Coordinate values must be valid decimals.', 'warning')
        return redirect(url_for('admin.location'))

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Location
            SET village_name = ?, district = ?, province = ?,
                latitude = ?, longitude = ?, altitude = ?
            WHERE location_id = ?
        """, (name, district, province, latitude, longitude, altitude, location_id))
        conn.commit()
        flash('Location updated successfully.', 'success')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.location'))


@admin_bp.route('/location/delete/<int:location_id>', methods=['POST'])
def location_delete(location_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Location WHERE location_id = ?", (location_id,))
        conn.commit()
        flash('Location deleted successfully.', 'success')
    except pyodbc.IntegrityError:
        flash('Cannot delete: location is referenced by farm or weather records.', 'danger')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.location'))