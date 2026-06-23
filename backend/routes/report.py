from flask import render_template, flash
from admin import admin_bp, get_conn
import pyodbc

@admin_bp.route('/report')
def report():
    conn = get_conn()
    cursor = conn.cursor()

    rainfall_trend        = []
    seasonal_distribution = []
    weather_summary       = []
    top_crops             = []

    try:
        # ── 1. Monthly Rainfall & Temperature Trend ──────────────────────────
        # Groups Weather_Record by year-month, returns last 12 months
        cursor.execute("""
            SELECT TOP 12
                FORMAT(record_date, 'MMM yyyy')  AS month,
                AVG(rainfall_mm)                 AS avg_rainfall,
                AVG(average_temp_c)              AS avg_temperature
            FROM Weather_Record
            WHERE record_date IS NOT NULL
            GROUP BY FORMAT(record_date, 'MMM yyyy'),
                     YEAR(record_date),
                     MONTH(record_date)
            ORDER BY YEAR(record_date) DESC,
                     MONTH(record_date) DESC
        """)
        rows = cursor.fetchall()
        # Reverse so chart shows oldest → newest left to right
        rainfall_trend = [
            {
                'month':           row[0],
                'avg_rainfall':    round(float(row[1]), 1) if row[1] is not None else 0,
                'avg_temperature': round(float(row[2]), 1) if row[2] is not None else 0,
            }
            for row in reversed(rows)
        ]

        # ── 2. Crop Distribution by Season ───────────────────────────────────
        # Counts how many distinct crops are linked to each season
        cursor.execute("""
            SELECT
                s.season_type          AS season_name,
                COUNT(csj.crop_id)     AS crop_count
            FROM Season s
            LEFT JOIN Crop_Season_Junction csj ON s.season_id = csj.season_id
            GROUP BY s.season_type
            ORDER BY crop_count DESC
        """)
        seasonal_distribution = [
            {
                'season_name': row[0],
                'crop_count':  row[1] or 0,
            }
            for row in cursor.fetchall()
        ]

        # ── 3. Weather Summary by Location ───────────────────────────────────
        cursor.execute("""
            SELECT
                l.village_name + ', ' + l.district  AS location_name,
                AVG(wr.average_temp_c)               AS avg_temperature,
                AVG(wr.rainfall_mm)                  AS avg_rainfall,
                AVG(wr.humidity_pct)                 AS avg_humidity,
                COUNT(*)                             AS record_count
            FROM Weather_Record wr
            INNER JOIN Location l ON wr.location_id = l.location_id
            GROUP BY l.village_name, l.district
            ORDER BY record_count DESC
        """)
        weather_summary = [
            {
                'location_name':   row[0],
                'avg_temperature': round(float(row[1]), 1) if row[1] is not None else 0,
                'avg_rainfall':    round(float(row[2]), 1) if row[2] is not None else 0,
                'avg_humidity':    round(float(row[3]), 1) if row[3] is not None else 0,
                'record_count':    row[4],
            }
            for row in cursor.fetchall()
        ]

        # ── 4. Top Recommended Crops by Advisory Count ───────────────────────
        cursor.execute("""
            SELECT TOP 8
                c.crop_name,
                COUNT(al.advisory_id) AS recommendation_count
            FROM Advisory_Logs al
            INNER JOIN Crops c ON al.crop_id = c.crop_id
            GROUP BY c.crop_name
            ORDER BY recommendation_count DESC
        """)
        top_crops = [
            {
                'crop_name':           row[0],
                'recommendation_count': row[1],
            }
            for row in cursor.fetchall()
        ]

    except pyodbc.Error as e:
        print(f"DATABASE ERROR in report: {str(e)}")
        flash(f'Database error loading report: {str(e)}', 'danger')

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'report.html',
        rainfall_trend=rainfall_trend,
        seasonal_distribution=seasonal_distribution,
        weather_summary=weather_summary,
        top_crops=top_crops
    )