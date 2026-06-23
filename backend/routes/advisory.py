from flask import render_template, flash, redirect, url_for, request
from admin import admin_bp, get_conn
import pyodbc
from datetime import datetime

@admin_bp.route('/advisory', methods=['GET'])
def advisory():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Farm dropdown — HTML: f.farm_id, f.name, f.farmer_name
        cursor.execute("""
            SELECT f.farm_id, f.farm_name, fa.full_name
            FROM Farm f
            INNER JOIN Farmer fa ON f.farmer_id = fa.farmer_id
            ORDER BY f.farm_name
        """)
        farms = [
            {
                'farm_id':     r[0],
                'name':        r[1],
                'farmer_name': r[2],
            }
            for r in cursor.fetchall()
        ]

        # Season dropdown — HTML: s.season_id, s.name
        cursor.execute("SELECT season_id, season_type FROM Season ORDER BY season_type")
        seasons = [{'season_id': r[0], 'name': r[1]} for r in cursor.fetchall()]

        # Advisory history table
        cursor.execute("""
            SELECT
                al.advisory_id,
                f.farm_name,
                c.crop_name,
                al.match_score,
                al.generated_date
            FROM Advisory_Logs al
            INNER JOIN Farm  f ON al.farm_id = f.farm_id
            INNER JOIN Crops c ON al.crop_id = c.crop_id
            ORDER BY al.generated_date DESC
        """)
        advisory_logs = [
            {
                'id':               r[0],               # HTML: log.id
                'farm_name':        r[1],
                'crop_name':        r[2],
                'suitability_score': round(float(r[3]), 0) if r[3] is not None else 0,  # HTML: log.suitability_score
                'notes':            '',                  # not in DB schema, placeholder
                'generated_at':     r[4].strftime('%Y-%m-%d') if r[4] else '—',         # HTML: log.generated_at
            }
            for r in cursor.fetchall()
        ]

        return render_template(
            'advisory.html',
            farms=farms,
            seasons=seasons,
            advisory_logs=advisory_logs,
            results=None,
            selected_farm_id=None,
            selected_season_id=None,
        )

    except pyodbc.Error as e:
        print(f"DATABASE ERROR: {str(e)}")
        flash(f'Database error: {str(e)}', 'danger')
        return render_template(
            'advisory.html',
            farms=[], seasons=[], advisory_logs=[],
            results=None, selected_farm_id=None, selected_season_id=None
        )
    finally:
        cursor.close()
        conn.close()


@admin_bp.route('/advisory', methods=['POST'])
def advisory_generate():
    farm_id   = request.form.get('farm_id', '').strip()
    season_id = request.form.get('season_id', '').strip()

    if not farm_id:
        flash('Please select a farm.', 'warning')
        return redirect(url_for('admin.advisory'))

    farm_id   = int(farm_id)
    season_id = int(season_id) if season_id else None

    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Get farm name and farmer for results header
        cursor.execute("""
            SELECT f.farm_name, fa.full_name
            FROM Farm f
            INNER JOIN Farmer fa ON f.farmer_id = fa.farmer_id
            WHERE f.farm_id = ?
        """, (farm_id,))
        farm_row = cursor.fetchone()
        farm_name = f"{farm_row[0]} ({farm_row[1]})" if farm_row else '—'

        # Get latest soil profile for this farm
        cursor.execute("""
            SELECT TOP 1 sp.ph_level, sp.soil_type_id
            FROM Soil_Profile sp
            WHERE sp.farm_id = ?
            ORDER BY sp.sample_date DESC
        """, (farm_id,))
        soil_row = cursor.fetchone()
        farm_ph       = float(soil_row[0]) if soil_row and soil_row[0] else None
        farm_soil_type = soil_row[1] if soil_row else None

        # Get latest weather for this farm's location
        cursor.execute("""
            SELECT TOP 1
                wr.average_temp_c,
                wr.rainfall_mm,
                wr.season_id
            FROM Weather_Record wr
            INNER JOIN Farm f ON f.farm_id = ?
            WHERE wr.location_id = (SELECT location_id FROM Farm WHERE farm_id = ?)
            ORDER BY wr.record_date DESC
        """, (farm_id, farm_id))
        weather_row   = cursor.fetchone()
        farm_temp     = float(weather_row[0]) if weather_row and weather_row[0] else None
        farm_rainfall = float(weather_row[1]) if weather_row and weather_row[1] else None

        # Get all crops, optionally filtered by season
        if season_id:
            cursor.execute("""
                SELECT DISTINCT
                    c.crop_id, c.crop_name, c.crop_category,
                    c.min_temp_c, c.max_temp_c,
                    c.min_rainfall_mm, c.max_rainfall_mm,
                    c.min_ph, c.max_ph
                FROM Crops c
                INNER JOIN Crop_Season_Junction csj ON c.crop_id = csj.crop_id
                WHERE csj.season_id = ?
                ORDER BY c.crop_name
            """, (season_id,))
        else:
            cursor.execute("""
                SELECT
                    crop_id, crop_name, crop_category,
                    min_temp_c, max_temp_c,
                    min_rainfall_mm, max_rainfall_mm,
                    min_ph, max_ph
                FROM Crops
                ORDER BY crop_name
            """)
        crop_rows = cursor.fetchall()

        # Score each crop against farm conditions
        recommendations = []
        for r in crop_rows:
            crop_id       = r[0]
            crop_name     = r[1]
            category      = r[2]
            min_temp      = float(r[3]) if r[3] is not None else None
            max_temp      = float(r[4]) if r[4] is not None else None
            min_rain      = float(r[5]) if r[5] is not None else None
            max_rain      = float(r[6]) if r[6] is not None else None
            min_ph        = float(r[7]) if r[7] is not None else None
            max_ph        = float(r[8]) if r[8] is not None else None

            score    = 0
            checks   = 0
            conditions = []

            if farm_temp is not None and min_temp is not None and max_temp is not None:
                checks += 1
                if min_temp <= farm_temp <= max_temp:
                    score += 1
                    conditions.append(f"✓ Temp {farm_temp}°C within {min_temp}–{max_temp}°C")
                else:
                    conditions.append(f"✗ Temp {farm_temp}°C outside {min_temp}–{max_temp}°C")

            if farm_rainfall is not None and min_rain is not None and max_rain is not None:
                checks += 1
                if min_rain <= farm_rainfall <= max_rain:
                    score += 1
                    conditions.append(f"✓ Rainfall {farm_rainfall}mm within {min_rain}–{max_rain}mm")
                else:
                    conditions.append(f"✗ Rainfall {farm_rainfall}mm outside {min_rain}–{max_rain}mm")

            if farm_ph is not None and min_ph is not None and max_ph is not None:
                checks += 1
                if min_ph <= farm_ph <= max_ph:
                    score += 1
                    conditions.append(f"✓ pH {farm_ph} within {min_ph}–{max_ph}")
                else:
                    conditions.append(f"✗ pH {farm_ph} outside {min_ph}–{max_ph}")

            suitability = round((score / checks) * 100) if checks > 0 else 0

            recommendations.append({
                'crop_id':            crop_id,
                'crop_name':          crop_name,
                'category':           category or '—',
                'suitability_score':  suitability,
                'matching_conditions': conditions,
                'notes':              f"Matched {score}/{checks} conditions.",
            })

        # Sort best matches first
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)

        # Save top result to Advisory_Logs if any recommendations exist
        if recommendations:
            top = recommendations[0]
            cursor.execute("""
                INSERT INTO Advisory_Logs
                    (farm_id, crop_id, generated_date, match_score)
                VALUES (?, ?, ?, ?)
            """, (farm_id, top['crop_id'], datetime.utcnow().date(), top['suitability_score']))
            conn.commit()

        results = {
            'farm_name':       farm_name,
            'recommendations': recommendations,
        }

        # Reload dropdowns and logs for re-render
        cursor.execute("""
            SELECT f.farm_id, f.farm_name, fa.full_name
            FROM Farm f INNER JOIN Farmer fa ON f.farmer_id = fa.farmer_id
            ORDER BY f.farm_name
        """)
        farms = [{'farm_id': r[0], 'name': r[1], 'farmer_name': r[2]} for r in cursor.fetchall()]

        cursor.execute("SELECT season_id, season_type FROM Season ORDER BY season_type")
        seasons = [{'season_id': r[0], 'name': r[1]} for r in cursor.fetchall()]

        cursor.execute("""
            SELECT al.advisory_id, f.farm_name, c.crop_name, al.match_score, al.generated_date
            FROM Advisory_Logs al
            INNER JOIN Farm  f ON al.farm_id = f.farm_id
            INNER JOIN Crops c ON al.crop_id = c.crop_id
            ORDER BY al.generated_date DESC
        """)
        advisory_logs = [
            {
                'id':               r[0],
                'farm_name':        r[1],
                'crop_name':        r[2],
                'suitability_score': round(float(r[3]), 0) if r[3] is not None else 0,
                'notes':            '',
                'generated_at':     r[4].strftime('%Y-%m-%d') if r[4] else '—',
            }
            for r in cursor.fetchall()
        ]

        return render_template(
            'advisory.html',
            farms=farms,
            seasons=seasons,
            advisory_logs=advisory_logs,
            results=results,
            selected_farm_id=farm_id,
            selected_season_id=season_id,
        )

    except pyodbc.Error as e:
        print(f"DATABASE ERROR: {str(e)}")
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('admin.advisory'))
    finally:
        cursor.close()
        conn.close()


@admin_bp.route('/advisory/delete/<int:log_id>', methods=['POST'])
def advisory_delete(log_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Advisory_Logs WHERE advisory_id = ?", (log_id,))
        conn.commit()
        flash('Advisory log deleted.', 'success')
    except pyodbc.Error as e:
        flash(f'Database error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.advisory'))