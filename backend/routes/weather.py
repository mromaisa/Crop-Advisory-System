from flask import render_template, flash, redirect, url_for, request
from admin import admin_bp, get_conn
import pyodbc
from datetime import datetime

@admin_bp.route('/weather', methods=['GET'])
def weather():
    conn = get_conn()
    cursor = conn.cursor()
    selected_location_id = request.args.get('location_id', type=int)

    try:
        if selected_location_id:
            cursor.execute("""
                SELECT wr.weather_id, wr.location_id,
                       l.village_name + ', ' + l.district AS location_name,
                       wr.record_date, wr.average_temp_c,
                       wr.rainfall_mm, wr.humidity_pct,
                       wr.season_id, s.season_type
                FROM Weather_Record wr
                INNER JOIN Location l ON wr.location_id = l.location_id
                LEFT JOIN Season s ON wr.season_id = s.season_id
                WHERE wr.location_id = ?
                ORDER BY wr.record_date DESC
            """, (selected_location_id,))
        else:
            cursor.execute("""
                SELECT wr.weather_id, wr.location_id,
                       l.village_name + ', ' + l.district AS location_name,
                       wr.record_date, wr.average_temp_c,
                       wr.rainfall_mm, wr.humidity_pct,
                       wr.season_id, s.season_type
                FROM Weather_Record wr
                INNER JOIN Location l ON wr.location_id = l.location_id
                LEFT JOIN Season s ON wr.season_id = s.season_id
                ORDER BY wr.record_date DESC
            """)

        weather_records = [
            {
                'id':            r[0],
                'location_id':   r[1],
                'location_name': r[2],
                'record_date':   r[3].strftime('%Y-%m-%d') if r[3] else '—',
                'temperature':   float(r[4]) if r[4] is not None else 0,
                'rainfall':      float(r[5]) if r[5] is not None else 0,
                'humidity':      float(r[6]) if r[6] is not None else 0,
                'season_id':     r[7] if r[7] is not None else '',
                'season':        r[8] if r[8] is not None else '—',
                'wind_speed':    None,
                'notes':         '',
            }
            for r in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT location_id, village_name + ', ' + district AS name
            FROM Location ORDER BY village_name
        """)
        locations = [{'location_id': r[0], 'name': r[1]} for r in cursor.fetchall()]

        cursor.execute("SELECT season_id, season_type FROM Season ORDER BY season_type")
        seasons = [{'season_id': r[0], 'season_type': r[1]} for r in cursor.fetchall()]

        return render_template(
            'weather.html',
            weather_records=weather_records,
            locations=locations,
            seasons=seasons,
            selected_location_id=selected_location_id,
        )

    except pyodbc.Error as e:
        print(f"DATABASE ERROR: {str(e)}")
        flash(f'Database error: {str(e)}', 'danger')
        return render_template(
            'weather.html',
            weather_records=[], locations=[], seasons=[],
            selected_location_id=None
        )
    finally:
        cursor.close()
        conn.close()


@admin_bp.route('/weather', methods=['POST'])
def weather_create():
    data         = request.form
    location_id  = data.get('location_id', '').strip()
    record_date  = data.get('record_date', '').strip()
    temperature  = data.get('temperature', '0').strip()
    rainfall     = data.get('rainfall', '0').strip()
    humidity     = data.get('humidity', '0').strip()
    season_id    = data.get('season_id', '').strip()

    if not location_id:
        flash('Location is required.', 'warning')
        return redirect(url_for('admin.weather'))

    try:
        location_id  = int(location_id)
        avg_temp     = float(temperature)
        rainfall_mm  = float(rainfall)
        humidity_pct = float(humidity)
        season_id    = int(season_id) if season_id else None
        rec_date     = datetime.strptime(record_date, '%Y-%m-%d').date() if record_date else None
    except ValueError:
        flash('Invalid numeric or date values.', 'warning')
        return redirect(url_for('admin.weather'))

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Weather_Record
                (location_id, record_date, average_temp_c, rainfall_mm, humidity_pct, season_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (location_id, rec_date, avg_temp, rainfall_mm, humidity_pct, season_id))
        conn.commit()
        flash('Weather record added successfully.', 'success')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.weather'))


# ── Distinct prefix 'update' avoids conflict with 'delete/<int>' ──
@admin_bp.route('/weather/update/<int:record_id>', methods=['POST'])
def weather_update(record_id):
    data        = request.form
    location_id = data.get('location_id', '').strip()
    record_date = data.get('record_date', '').strip()
    temperature = data.get('temperature', '0').strip()
    rainfall    = data.get('rainfall', '0').strip()
    humidity    = data.get('humidity', '0').strip()
    season_id   = data.get('season_id', '').strip()

    try:
        location_id  = int(location_id)
        avg_temp     = float(temperature)
        rainfall_mm  = float(rainfall)
        humidity_pct = float(humidity)
        season_id    = int(season_id) if season_id else None
        rec_date     = datetime.strptime(record_date, '%Y-%m-%d').date() if record_date else None
    except ValueError:
        flash('Invalid numeric or date values.', 'warning')
        return redirect(url_for('admin.weather'))

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Weather_Record
            SET location_id = ?, record_date = ?,
                average_temp_c = ?, rainfall_mm = ?,
                humidity_pct = ?, season_id = ?
            WHERE weather_id = ?
        """, (location_id, rec_date, avg_temp, rainfall_mm, humidity_pct, season_id, record_id))
        conn.commit()
        flash('Weather record updated successfully.', 'success')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.weather'))


@admin_bp.route('/weather/delete/<int:record_id>', methods=['POST'])
def weather_delete(record_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Weather_Record WHERE weather_id = ?", (record_id,))
        conn.commit()
        flash('Weather record deleted successfully.', 'success')
    except pyodbc.IntegrityError:
        flash('Cannot delete: record is referenced by advisory logs.', 'danger')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.weather'))