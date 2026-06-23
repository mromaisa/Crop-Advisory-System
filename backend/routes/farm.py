from flask import render_template, flash, redirect, url_for, request
from admin import admin_bp, get_conn
import pyodbc
from datetime import datetime

@admin_bp.route('/farm')
def farm():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT f.farm_id, f.farm_name, fa.farmer_id, fa.full_name,
                   l.location_id, l.village_name, l.district,
                   f.area_acres, f.established_date
            FROM Farm f
            INNER JOIN Farmer   fa ON f.farmer_id   = fa.farmer_id
            INNER JOIN Location l  ON f.location_id = l.location_id
            ORDER BY f.farm_id DESC
        """)
        farms = [
            {
                'farm_id':       r[0],
                'name':          r[1],                          # HTML: farm.name
                'farmer_id':     r[2],                          # HTML: farm.farmer_id (edit modal)
                'farmer_name':   r[3],                          # HTML: farm.farmer_name
                'location_id':   r[4],                          # HTML: farm.location_id (edit modal)
                'location_name': f"{r[5]}, {r[6]}",            # HTML: farm.location_name
                'area_hectares': float(r[7]) if r[7] else 0,   # HTML: farm.area_hectares (DB stores area_acres)
                'created_at':    r[8].strftime('%Y-%m-%d') if r[8] else '—',  # HTML: farm.created_at
            }
            for r in cursor.fetchall()
        ]

        # Farmer dropdown options — HTML: f.farmer_id, f.name
        cursor.execute("SELECT farmer_id, full_name FROM Farmer ORDER BY full_name")
        farmers = [{'farmer_id': r[0], 'name': r[1]} for r in cursor.fetchall()]

        # Location dropdown options — HTML: l.location_id, l.name, l.country
        cursor.execute("SELECT location_id, village_name, district, province FROM Location ORDER BY village_name")
        locations = [
            {
                'location_id': r[0],
                'name':        r[1],
                'country':     f"{r[2]}, {r[3]}"   # HTML uses l.country, mapping district+province
            }
            for r in cursor.fetchall()
        ]

        return render_template('farms.html', farms=farms, farmers=farmers, locations=locations)

    except pyodbc.Error as e:
        print(f"DATABASE ERROR: {str(e)}")
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('farms.html', farms=[], farmers=[], locations=[])
    finally:
        cursor.close()
        conn.close()


@admin_bp.route('/farm', methods=['POST'])
def farm_create():
    data        = request.form
    farmer_id   = data.get('farmer_id', '').strip()
    location_id = data.get('location_id', '').strip()
    farm_name   = data.get('name', '').strip()          # HTML form field is 'name'
    area        = data.get('area_hectares', '0').strip() # HTML form field is 'area_hectares'
    farm_type   = data.get('farm_type', '').strip()     # not in DB, ignore for now

    if not all([farmer_id, location_id, farm_name]):
        flash('Farmer, location, and farm name are required.', 'warning')
        return redirect(url_for('admin.farm'))

    try:
        farmer_id   = int(farmer_id)
        location_id = int(location_id)
        area_acres  = float(area)
    except ValueError:
        flash('Invalid area value.', 'warning')
        return redirect(url_for('admin.farm'))

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Farm (farmer_id, location_id, farm_name, area_acres, established_date)
            VALUES (?, ?, ?, ?, ?)
        """, (farmer_id, location_id, farm_name, area_acres, datetime.utcnow().date()))
        conn.commit()
        flash(f'Farm "{farm_name}" created successfully.', 'success')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.farm'))


@admin_bp.route('/farm/<int:farm_id>', methods=['POST'])
def farm_update(farm_id):
    data        = request.form
    farmer_id   = data.get('farmer_id', '').strip()
    location_id = data.get('location_id', '').strip()
    farm_name   = data.get('name', '').strip()
    area        = data.get('area_hectares', '0').strip()

    if not farm_name:
        flash('Farm name is required.', 'warning')
        return redirect(url_for('admin.farm'))

    try:
        farmer_id   = int(farmer_id)
        location_id = int(location_id)
        area_acres  = float(area)
    except ValueError:
        flash('Invalid input values.', 'warning')
        return redirect(url_for('admin.farm'))

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Farm
            SET farmer_id = ?, location_id = ?, farm_name = ?, area_acres = ?
            WHERE farm_id = ?
        """, (farmer_id, location_id, farm_name, area_acres, farm_id))
        conn.commit()
        flash('Farm updated successfully.', 'success')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.farm'))


@admin_bp.route('/farm/delete/<int:farm_id>', methods=['POST'])
def farm_delete(farm_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Farm WHERE farm_id = ?", (farm_id,))
        conn.commit()
        flash('Farm deleted successfully.', 'success')
    except pyodbc.IntegrityError:
        flash('Cannot delete: farm has dependent soil or advisory records.', 'danger')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.farm'))