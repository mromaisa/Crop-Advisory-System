from flask import render_template, flash, redirect, url_for, request
from admin import admin_bp, get_conn
import pyodbc
from datetime import datetime

@admin_bp.route('/soil', methods=['GET'])
def soil():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Soil Profiles with farm name and soil type name
        cursor.execute("""
            SELECT sp.soil_id, sp.farm_id, f.farm_name,
                   sp.soil_type_id, st.soil_type,
                   sp.ph_level, sp.organic_matter_pct, sp.sample_date
            FROM Soil_Profile sp
            INNER JOIN Farm      f  ON sp.farm_id      = f.farm_id
            INNER JOIN Soil_Type st ON sp.soil_type_id = st.soil_type_id
            ORDER BY f.farm_name
        """)
        profiles = [
            {
                'id':              r[0],
                'farm_id':         r[1],
                'farm_name':       r[2],
                'soil_type_id':    r[3],
                'soil_type_name':  r[4],
                'ph_level':        float(r[5]) if r[5] is not None else 0,
                'organic_matter':  float(r[6]) if r[6] is not None else 0,
                'sample_date':     r[7].strftime('%Y-%m-%d') if r[7] else '—',
            }
            for r in cursor.fetchall()
        ]

        # Soil Types
        cursor.execute("SELECT soil_type_id, soil_type FROM Soil_Type ORDER BY soil_type")
        soil_types = [
            {
                'id':   r[0],
                'name': r[1],
            }
            for r in cursor.fetchall()
        ]

        # Farm dropdown for profile modal
        cursor.execute("SELECT farm_id, farm_name FROM Farm ORDER BY farm_name")
        farms = [{'farm_id': r[0], 'name': r[1]} for r in cursor.fetchall()]

        return render_template(
            'soil.html',
            profiles=profiles,
            soil_types=soil_types,
            farms=farms,
        )

    except pyodbc.Error as e:
        print(f"DATABASE ERROR: {str(e)}")
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('soil.html', profiles=[], soil_types=[], farms=[])
    finally:
        cursor.close()
        conn.close()


@admin_bp.route('/soil', methods=['POST'])
def soil_create():
    data    = request.form
    action  = data.get('action', '')

    if action == 'profile':
        farm_id      = data.get('farm_id', '').strip()
        soil_type_id = data.get('soil_type_id', '').strip()
        sample_date  = data.get('sample_date', '').strip()

        try:
            farm_id      = int(farm_id)
            soil_type_id = int(soil_type_id)
            ph_level     = float(data.get('ph_level', 0))
            organic_matter = float(data.get('organic_matter', 0))
            rec_date     = datetime.strptime(sample_date, '%Y-%m-%d').date() if sample_date else None
        except ValueError:
            flash('Invalid numeric or date values.', 'warning')
            return redirect(url_for('admin.soil'))

        if not farm_id or not soil_type_id:
            flash('Farm and soil type are required.', 'warning')
            return redirect(url_for('admin.soil'))

        conn = get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Soil_Profile (farm_id, soil_type_id, ph_level, organic_matter_pct, sample_date)
                VALUES (?, ?, ?, ?, ?)
            """, (farm_id, soil_type_id, ph_level, organic_matter, rec_date))
            conn.commit()
            flash('Soil profile added successfully.', 'success')
        except pyodbc.Error as e:
            flash(f'Database error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    elif action == 'type':
        soil_type = data.get('name', '').strip()

        if not soil_type:
            flash('Soil type name is required.', 'warning')
            return redirect(url_for('admin.soil'))

        conn = get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Soil_Type (soil_type) VALUES (?)
            """, (soil_type,))
            conn.commit()
            flash(f'Soil type "{soil_type}" added successfully.', 'success')
        except pyodbc.IntegrityError:
            flash('Soil type already exists.', 'danger')
        except pyodbc.Error as e:
            flash(f'Database error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.soil'))


@admin_bp.route('/soil/update/<int:profile_id>', methods=['POST'])
def soil_update(profile_id):
    data         = request.form
    farm_id      = data.get('farm_id', '').strip()
    soil_type_id = data.get('soil_type_id', '').strip()
    sample_date  = data.get('sample_date', '').strip()

    try:
        farm_id        = int(farm_id)
        soil_type_id   = int(soil_type_id)
        ph_level       = float(data.get('ph_level', 0))
        organic_matter = float(data.get('organic_matter', 0))
        rec_date       = datetime.strptime(sample_date, '%Y-%m-%d').date() if sample_date else None
    except ValueError:
        flash('Invalid numeric or date values.', 'warning')
        return redirect(url_for('admin.soil'))

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Soil_Profile
            SET farm_id = ?, soil_type_id = ?, ph_level = ?,
                organic_matter_pct = ?, sample_date = ?
            WHERE soil_id = ?
        """, (farm_id, soil_type_id, ph_level, organic_matter, rec_date, profile_id))
        conn.commit()
        flash('Soil profile updated successfully.', 'success')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.soil'))


@admin_bp.route('/soil/profile/delete/<int:profile_id>', methods=['POST'])
def soil_profile_delete(profile_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Soil_Profile WHERE soil_id = ?", (profile_id,))
        conn.commit()
        flash('Soil profile deleted successfully.', 'success')
    except pyodbc.IntegrityError:
        flash('Cannot delete: profile is referenced by advisory logs.', 'danger')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.soil'))


@admin_bp.route('/soil/type/delete/<int:type_id>', methods=['POST'])
def soil_type_delete(type_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Soil_Type WHERE soil_type_id = ?", (type_id,))
        conn.commit()
        flash('Soil type deleted successfully.', 'success')
    except pyodbc.IntegrityError:
        flash('Cannot delete: soil type is used by existing profiles.', 'danger')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.soil'))