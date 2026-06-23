from flask import render_template, flash, redirect, url_for, request
from admin import admin_bp, get_conn
import pyodbc

@admin_bp.route('/crop')
def crop():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Fetch all crops
        cursor.execute("""
            SELECT crop_id, crop_name, crop_category,
                   min_temp_c, max_temp_c,
                   min_rainfall_mm, max_rainfall_mm,
                   min_ph, max_ph
            FROM Crops
            ORDER BY crop_category, crop_name
        """)
        raw_crops = cursor.fetchall()

        # Fetch soil junction: crop_id → [soil_type strings]
        cursor.execute("""
            SELECT csj.crop_id, st.soil_type
            FROM Crop_Soil_Junction csj
            INNER JOIN Soil_Type st ON csj.soil_type_id = st.soil_type_id
        """)
        crop_soil_map = {}
        for row in cursor.fetchall():
            crop_soil_map.setdefault(row[0], []).append(row[1])

        # Fetch season junction: crop_id → [season_type strings]
        cursor.execute("""
            SELECT csj.crop_id, s.season_type
            FROM Crop_Season_Junction csj
            INNER JOIN Season s ON csj.season_id = s.season_id
        """)
        crop_season_map = {}
        for row in cursor.fetchall():
            crop_season_map.setdefault(row[0], []).append(row[1])

        # Build list with keys matching the HTML template exactly
        crops = [
            {
                'id':              r[0],
                'name':            r[1],
                'category':        r[2],
                'duration_days':   '—',          # not in your DB schema, placeholder
                'min_temperature': float(r[3]) if r[3] is not None else 0,
                'max_temperature': float(r[4]) if r[4] is not None else 0,
                'min_rainfall':    float(r[5]) if r[5] is not None else 0,
                'max_rainfall':    float(r[6]) if r[6] is not None else 0,
                'min_ph':          float(r[7]) if r[7] is not None else 0,
                'max_ph':          float(r[8]) if r[8] is not None else 0,
                'description':     '',
                'seasons':         crop_season_map.get(r[0], []),
                'soil_types':      crop_soil_map.get(r[0], []),
            }
            for r in raw_crops
        ]

        return render_template('crop.html', crops=crops)

    except pyodbc.Error as e:
        print(f"DATABASE ERROR: {str(e)}")
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('crop.html', crops=[])
    finally:
        cursor.close()
        conn.close()


def _sync_crop_junctions(cursor, crop_id, soil_ids, season_ids):
    cursor.execute("DELETE FROM Crop_Soil_Junction   WHERE crop_id = ?", (crop_id,))
    cursor.execute("DELETE FROM Crop_Season_Junction WHERE crop_id = ?", (crop_id,))
    for sid in soil_ids:
        cursor.execute("INSERT INTO Crop_Soil_Junction (crop_id, soil_type_id) VALUES (?, ?)", (crop_id, int(sid)))
    for sea_id in season_ids:
        cursor.execute("INSERT INTO Crop_Season_Junction (crop_id, season_id) VALUES (?, ?)", (crop_id, int(sea_id)))


@admin_bp.route('/crop/create', methods=['POST'])
def crop_create():
    data          = request.form
    crop_name     = data.get('name', '').strip()        # HTML form field is 'name'
    crop_category = data.get('category', '').strip()    # HTML form field is 'category'
    soil_ids      = data.getlist('soil_type_ids')
    season_ids    = data.getlist('season_ids')

    try:
        min_temp     = float(data.get('min_temperature', 0))
        max_temp     = float(data.get('max_temperature', 0))
        min_rainfall = float(data.get('min_rainfall', 0))
        max_rainfall = float(data.get('max_rainfall', 0))
        min_ph       = float(data.get('min_ph', 0))
        max_ph       = float(data.get('max_ph', 0))
    except ValueError:
        flash('All threshold fields must be valid numbers.', 'warning')
        return redirect(url_for('admin.crop'))

    if not crop_name:
        flash('Crop name is required.', 'warning')
        return redirect(url_for('admin.crop'))

    conn   = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Crops (crop_name, crop_category, min_temp_c, max_temp_c, min_rainfall_mm, max_rainfall_mm, min_ph, max_ph)
            OUTPUT INSERTED.crop_id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (crop_name, crop_category, min_temp, max_temp, min_rainfall, max_rainfall, min_ph, max_ph))
        new_crop_id = cursor.fetchone()[0]
        _sync_crop_junctions(cursor, new_crop_id, soil_ids, season_ids)
        conn.commit()
        flash(f'Crop "{crop_name}" created successfully.', 'success')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.crop'))


@admin_bp.route('/crop/update/<int:crop_id>', methods=['POST'])
def crop_update(crop_id):
    data          = request.form
    crop_name     = data.get('name', '').strip()
    crop_category = data.get('category', '').strip()
    soil_ids      = data.getlist('soil_type_ids')
    season_ids    = data.getlist('season_ids')

    try:
        min_temp     = float(data.get('min_temperature', 0))
        max_temp     = float(data.get('max_temperature', 0))
        min_rainfall = float(data.get('min_rainfall', 0))
        max_rainfall = float(data.get('max_rainfall', 0))
        min_ph       = float(data.get('min_ph', 0))
        max_ph       = float(data.get('max_ph', 0))
    except ValueError:
        flash('All threshold fields must be valid numbers.', 'warning')
        return redirect(url_for('admin.crop'))

    conn   = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Crops
            SET crop_name = ?, crop_category = ?,
                min_temp_c = ?, max_temp_c = ?,
                min_rainfall_mm = ?, max_rainfall_mm = ?,
                min_ph = ?, max_ph = ?
            WHERE crop_id = ?
        """, (crop_name, crop_category, min_temp, max_temp, min_rainfall, max_rainfall, min_ph, max_ph, crop_id))
        _sync_crop_junctions(cursor, crop_id, soil_ids, season_ids)
        conn.commit()
        flash(f'Crop updated successfully.', 'success')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.crop'))


@admin_bp.route('/crop/delete/<int:crop_id>', methods=['POST'])
def crop_delete(crop_id):
    conn   = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Crop_Soil_Junction   WHERE crop_id = ?", (crop_id,))
        cursor.execute("DELETE FROM Crop_Season_Junction WHERE crop_id = ?", (crop_id,))
        cursor.execute("DELETE FROM Crops WHERE crop_id = ?", (crop_id,))
        conn.commit()
        flash('Crop deleted successfully.', 'success')
    except pyodbc.IntegrityError:
        flash('Cannot delete: crop is referenced by advisory logs.', 'danger')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.crop'))