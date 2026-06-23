from flask import render_template, flash, session
from admin import admin_bp, get_conn
import pyodbc

@admin_bp.route('/dashboard')
def dashboard():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM Farmer")
        total_farmers = cursor.fetchone()[0]
        print(f"DEBUG total_farmers: {total_farmers}")

        cursor.execute("SELECT COUNT(*) FROM Farm")
        total_farms = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Crops")
        total_crops = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Advisory_Logs")
        total_advisories = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Weather_Record")
        total_weather_records = cursor.fetchone()[0]

        cursor.execute("""
            SELECT TOP 5
                al.advisory_id,
                f.farm_name,
                c.crop_name,
                al.match_score,
                al.generated_date
            FROM Advisory_Logs al
            INNER JOIN Farm f       ON al.farm_id  = f.farm_id
            INNER JOIN Crops c      ON al.crop_id  = c.crop_id
            ORDER BY al.generated_date DESC
        """)
        recent_advisories = [
            {
                'farm_name': row[1],
                'crop_name': row[2],
                'suitability_score': round(float(row[3]), 0) if row[3] else 0,
                'generated_at': row[4].strftime('%Y-%m-%d') if row[4] else '—'
            }
            for row in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT TOP 5
                c.crop_name,
                c.crop_category,
                COUNT(*) as recommendation_count
            FROM Advisory_Logs al
            INNER JOIN Crops c ON al.crop_id = c.crop_id
            GROUP BY c.crop_name, c.crop_category
            ORDER BY recommendation_count DESC
        """)
        top_crops = [
            {
                'crop_name': row[0],
                'category': row[1],
                'recommendation_count': row[2]
            }
            for row in cursor.fetchall()
        ]

        stats = {
            'total_farmers': total_farmers,
            'total_farms': total_farms,
            'total_crops': total_crops,
            'total_advisories': total_advisories,
            'total_weather_records': total_weather_records,
        }
        print (f"DEBUG stats: {stats}")

        return render_template(
            'dashboard.html',
            stats=stats,
            recent_advisories=recent_advisories,
            top_crops=top_crops
        )

    except pyodbc.Error as e:
        print(f"DATABASE ERROR: {str(e)}")  
        flash(f'Database error: {str(e)}', 'danger')
        return render_template(
            'dashboard.html',
            stats={'total_farmers':0,'total_farms':0,'total_crops':0,'total_advisories':0,'total_weather_records':0},
            recent_advisories=[],
            top_crops=[]
        )
    finally:
        cursor.close()
        conn.close()