"""
user_routes.py — Farmer Operations Blueprint
"""
"""
security.py — Session Protection and Role-Based Access Control
"""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import requests
from admin import get_conn

# Define the user blueprint
user_bp = Blueprint('user', __name__, template_folder='templates')



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check if user is authenticated
        if not session.get("farmer_id"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        
        # 2. Check if the user has the correct authorization role
        if session.get("role") != "farmer":
            flash("Access denied. Authorized farmers only.", "danger")
            return redirect(url_for("auth.login"))
            
        return f(*args, **kwargs)
    return decorated_function

#-------------------------------------------------------
# USER DASHBOARD ROUTE
#-------------------------------------------------------
@user_bp.route("/dashboard")
@login_required
def dashboard():
    farmer_id = session.get("farmer_id")

    try:
        conn = get_conn()
        cursor = conn.cursor()

        # 1. Fetch Farmer Core Details (added phone_number)
        cursor.execute("""
            SELECT farmer_id, full_name, email, phone_number 
            FROM Farmer 
            WHERE farmer_id = ?
        """, (farmer_id,))
        farmer_row = cursor.fetchone()

        if not farmer_row:
            flash("Farmer profile details not found.", "danger")
            return redirect(url_for('auth.logout'))

        farmer = {
            "farmer_id":    farmer_row[0],   # template uses farmer.farmer_id
            "full_name":    farmer_row[1],
            "email":        farmer_row[2],
            "phone_number": farmer_row[3]    # template uses farmer.phone_number
        }

        # 2. Farm Count Check
        cursor.execute("SELECT COUNT(*) FROM Farm WHERE farmer_id = ?", (farmer_id,))
        farm_count = cursor.fetchone()[0]

        if farm_count == 0:
            flash("Please register a farm to initialize your profile dashboard.", "info")
            return redirect(url_for('user.create_farm_view'))

        # 3. Fetch Crop Recommendations via Stored Procedure
        # Template iterates `recommended_crops` with: crop_name, crop_category,
        # total_score, temp_score, rainfall_score, ph_score
        cursor.execute("EXEC GetBestCropRecommendationsByFarmer ?", (farmer_id,))
        rec_rows = cursor.fetchall()

        recommended_crops = []
        for row in rec_rows:
            recommended_crops.append({
                "crop_name":      row[0] if len(row) > 0 else "N/A",
                "crop_category":  row[1] if len(row) > 1 else "N/A",
                "total_score":    row[2] if len(row) > 2 else "N/A",
                "temp_score":     row[3] if len(row) > 3 else "N/A",
                "rainfall_score": row[4] if len(row) > 4 else "N/A",
                "ph_score":       row[5] if len(row) > 5 else "N/A",
            })

         # 4. Fetch Latest Weather Record
        # FIX: query Weather_Record (same table farm creation inserts into)
        # not WeatherApiTest which may be empty or a different table
        weather = None
        try:
            cursor.execute("""
                SELECT TOP 1
                    l.village_name,
                    wr.record_date,
                    wr.min_temp_c,
                    wr.average_temp_c,
                    wr.max_temp_c,
                    wr.rainfall_mm,
                    wr.humidity_pct
                FROM Weather_Record wr
                INNER JOIN Location l ON wr.location_id = l.location_id
                INNER JOIN Farm f ON f.location_id = l.location_id
                WHERE f.farmer_id = ?
                ORDER BY wr.record_date DESC
            """, (farmer_id,))
            weather_row = cursor.fetchone()

            if weather_row:
                weather = {
                    "city_name":    weather_row[0],
                    "record_date":  weather_row[1],
                    "min_temp_c":   weather_row[2],
                    "avg_temp_c":   weather_row[3],
                    "max_temp_c":   weather_row[4],
                    "rainfall_mm":  weather_row[5],
                    "humidity_pct": weather_row[6],
                }
        except Exception as weather_err:
            print(f"[WEATHER QUERY ERROR] {weather_err}")

        # 5. Fetch Farms as (farm_obj, location_obj) tuple pairs
        # Template does: {% for farm, location in farms %}
        # and accesses farm.farm_name, farm.area_acres, farm.farm_type
        # and location.village_name, location.district, location.province
        cursor.execute("""
            SELECT 
                f.farm_id, f.farm_name, f.area_acres,
                l.village_name, l.district, l.province
            FROM Farm f
            INNER JOIN Location l ON f.location_id = l.location_id
            WHERE f.farmer_id = ?
        """, (farmer_id,))
        farm_rows = cursor.fetchall()

        # Build as list of (farm_dict, location_dict) tuples to match
        # the {% for farm, location in farms %} unpacking in the template
        farms = []
        for row in farm_rows:
            farm_obj = {
                "farm_id":    row[0],
                "farm_name":  row[1],
                "area_acres": row[2],
            }
            location_obj = {
                "village_name": row[3],
                "district":     row[4],
                "province":     row[5],
            }
            farms.append((farm_obj, location_obj))

        # 6. Fetch Advisory History for all farmer's farms
        advisory_history = []
        try:
            for farm_obj, location_obj in farms:
                cursor.execute("EXEC GetAdvisoryHistory ?", (farm_obj["farm_name"],))
                rows = cursor.fetchall()
                for row in rows:
                    advisory_history.append({
                        "advisory_id":   row[0],
                        "generated_date": row[1].strftime('%Y-%m-%d %H:%M') if row[1] else "N/A",
                        "crop_name":     row[2],
                        "crop_category": row[3],
                        "match_score":   round(float(row[4]), 1) if row[4] else "N/A",
                        "avg_temp_c":    row[5],
                        "rainfall_mm":   row[6],
                        "farm_name":     farm_obj["farm_name"],  # attach farm name for display
                    })
                # consume any extra result sets pyodbc may hold
                while cursor.nextset():
                    pass
        except Exception as hist_err:
            print(f"[ADVISORY HISTORY ERROR] {hist_err}")

        conn.close()

        return render_template(
            "user_dashboard.html",
            farmer=farmer,
            farms=farms,
            recommended_crops=recommended_crops,
            weather=weather,
            advisory_history=advisory_history
        )

        

    except Exception as e:
        print(f"[BLUEPRINT DASHBOARD ERROR] {e}")
        flash("An error occurred trying to parse your dashboard telemetry.", "danger")
        return render_template(
            "user_dashboard.html",
            farmer=None,
            farms=[],
            recommended_crops=[],
            weather=None,
            advisory_history=[]
        )


# ───────────────────────────────────────────────────────────────────
# FARM MANAGEMENT ROUTES (CREATE & VIEW)
# ───────────────────────────────────────────────────────────────────
@user_bp.route("/farms/create", methods=["GET"])
@login_required
def create_farm_view():
    """
    GET: Renders the farm page with the farmer's existing farms listed.
    Session farmer_id is used to fetch only THIS farmer's farms.
    """
    farmer_id = session.get("farmer_id")
    farms = []

    try:
        conn = get_conn()
        cursor = conn.cursor()

        # Fetch all farms belonging to the logged-in farmer
        # Flat dict here because user_Farm.html iterates as: {% for f in farms %}
        # and accesses f.farm_name, f.area_acres, f.farm_type, f.village_name etc.
        cursor.execute("""
            SELECT
                f.farm_id,
                f.farm_name,
                f.area_acres,
                l.village_name,
                l.district,
                l.province
            FROM Farm f
            INNER JOIN Location l ON f.location_id = l.location_id
            WHERE f.farmer_id = ?
            ORDER BY f.farm_id DESC
        """, (farmer_id,))

        rows = cursor.fetchall()
        for row in rows:
            farms.append({
                "farm_id":      row[0],
                "farm_name":    row[1],
                "area_acres":   row[2],
                "village_name": row[3],
                "district":     row[4],
                "province":     row[5],
            })
        rows = cursor.fetchall()
        if rows:
            print(f"[DEBUG] Column count per row: {len(rows[0])}")
            print(f"[DEBUG] First row raw: {rows[0]}")
        conn.close()

    except Exception as e:
        print(f"[FARM VIEW ERROR] {e}")
        flash("Could not load your farm records.", "danger")

    return render_template("user_Farm.html", farms=farms)


@user_bp.route("/farms/create", methods=["POST"])
@login_required
def process_create_farm():
    """Processes weather API pulling, location inserts, and new farm generation."""
    farmer_id = session.get("farmer_id")
    
    village_name = request.form.get("village_name", "").strip()
    district = request.form.get("district", "").strip()
    province = request.form.get("province", "").strip()
    farm_name = request.form.get("farm_name", "").strip()
    area_acres = request.form.get("area_acres", "0").strip()
    established_date_str = request.form.get("established_date", "")

    if not all([village_name, district, province, farm_name, established_date_str]):
        flash("Please populate all missing form parameters.", "warning")
        return redirect(url_for('user.create_farm_view'))

    # Initialize Weather and Geo-coordinate Variables with reasonable fallback defaults
    temp_c, avg_temp_c, min_temp_c, max_temp_c, rainfall_mm, humidity_pct = 25.0, 25.0, 20.0, 30.0, 0.0, 50
    latitude, longitude, altitude = 30.3753, 69.3451, 200.0  # Safe generic coordinates for Pakistan baseline

    # --- 1. Real-time Weather & Geo-Data Extraction (Moved Up) ---
    api_key = "7429773056a34ee688c183031251012"
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={village_name}&days=1"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            weather_data = response.json()
            
            # Extract Geo-coordinates safely for the Location Table
            location_meta = weather_data.get("location", {})
            latitude = float(location_meta.get("lat", latitude))
            longitude = float(location_meta.get("lon", longitude))
            
            # WeatherAPI returns elevation in meters ('val' keys can be handled smoothly)
            # WeatherAPI uses 'val' arrays or a straight 'tz_id' sibling float based on payload tier
            # We map it safely, otherwise relying on our custom decimal fallback
            altitude = float(location_meta.get("alt", 150.0)) if "alt" in location_meta else altitude
            
            # Extract Weather Telemetry
            current = weather_data["current"]
            day = weather_data["forecast"]["forecastday"][0]["day"]
            
            temp_c = current.get("temp_c", temp_c)
            avg_temp_c = day.get("avgtemp_c", avg_temp_c)
            min_temp_c = day.get("mintemp_c", min_temp_c)
            max_temp_c = day.get("maxtemp_c", max_temp_c)
            rainfall_mm = current.get("precip_mm", rainfall_mm)
            humidity_pct = current.get("humidity", humidity_pct)
        else:
            print(f"[WEATHER API WARNING] Status code {response.status_code}. Using coordinates/weather fallback.")
    except Exception as api_err:
        print(f"[WEATHER API FAILURE] Fallback coordinates and metrics assigned: {api_err}")

    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        # --- 2. Database connection insertion for Location with coordinates fixed ---
        cursor.execute("""
            INSERT INTO Location (village_name, district, province, latitude, longitude, altitude)
            OUTPUT INSERTED.location_id
            VALUES (?, ?, ?, ?, ?, ?)
        """, (village_name, district, province, latitude, longitude, altitude))
        
        location_id = cursor.fetchone()[0]

        # --- 3. Create Farm Record ---
        established_date = datetime.strptime(established_date_str, "%Y-%m-%d").date()
        cursor.execute("""
            INSERT INTO Farm (farmer_id, location_id, farm_name, area_acres, established_date)
            VALUES (?, ?, ?, ?, ?)
        """, (farmer_id, location_id, farm_name, float(area_acres), established_date))

        # --- 4. Save Extracted Data into Weather_Record ---
        # Note: Making sure column configuration matches what we declared earlier
        cursor.execute("""
            INSERT INTO Weather_Record 
                (location_id, record_date, average_temp_c, min_temp_c, max_temp_c, rainfall_mm, humidity_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (location_id, datetime.utcnow(), avg_temp_c, min_temp_c, max_temp_c, rainfall_mm, humidity_pct))

        conn.commit()
        conn.close()
        
        flash("Farm asset parameters and location weather profiles synced successfully!", "success")
        return redirect(url_for('user.farm_added_confirmation'))

    except Exception as e:
        print(f"[CATASTROPHIC FARM CREATION FAILURE] {e}")
        flash(f"Database error during generation: {str(e)}", "danger")
        return redirect(url_for('user.create_farm_view'))


@user_bp.route("/farm-added")
@login_required
def farm_added_confirmation():
    return redirect(url_for('user.create_farm_view'))



    # ───────────────────────────────────────────────────────────────────
# SOIL PROFILE ROUTES
# ───────────────────────────────────────────────────────────────────

@user_bp.route("/farms/<int:farm_id>/add-soil", methods=["GET"])
@login_required
def add_soil_view(farm_id):
    """
    GET: Renders soil form for a specific farm.
    Verifies the farm belongs to the logged-in farmer before showing the form.
    """
    farmer_id = session.get("farmer_id")

    try:
        conn   = get_conn()
        cursor = conn.cursor()

        # Security check: verify this farm belongs to THIS farmer
        # Prevents farmer A from accessing farmer B's farm by guessing the URL
        cursor.execute("""
            SELECT farm_id, farm_name
            FROM Farm
            WHERE farm_id = ? AND farmer_id = ?
        """, (farm_id, farmer_id))
        farm_row = cursor.fetchone()

        if not farm_row:
            flash("Farm not found or access denied.", "danger")
            return redirect(url_for('user.create_farm_view'))

        farm = {
            "farm_id":   farm_row[0],
            "farm_name": farm_row[1],
        }

        # Fetch all soil type options for the dropdown
        cursor.execute("SELECT soil_type_id, soil_type FROM Soil_Type")
        soil_types = [
            {"soil_type_id": row[0], "soil_type": row[1]}
            for row in cursor.fetchall()
        ]

        conn.close()

        return render_template("soil_form.html", farm=farm, soil_types=soil_types)

    except Exception as e:
        print(f"[SOIL FORM VIEW ERROR] {e}")
        flash("Could not load soil configuration form.", "danger")
        return redirect(url_for('user.create_farm_view'))


@user_bp.route("/farms/<int:farm_id>/add-soil", methods=["POST"])
@login_required
def process_add_soil(farm_id):
    """
    POST: Validates and inserts a Soil_Profile row for the given farm.
    After saving, redirects to advisory so the farmer sees recommendations immediately.
    """
    farmer_id = session.get("farmer_id")

    try:
        conn   = get_conn()
        cursor = conn.cursor()

        # Security check again on POST — never trust the URL alone
        cursor.execute("""
            SELECT farm_id FROM Farm
            WHERE farm_id = ? AND farmer_id = ?
        """, (farm_id, farmer_id))

        if not cursor.fetchone():
            flash("Farm not found or access denied.", "danger")
            return redirect(url_for('user.create_farm_view'))

        # Pull form values
        soil_type_id   = int(request.form.get("soil_type_id"))
        ph_level       = float(request.form.get("ph_level", 6.5))
        sample_date_str = request.form.get("sample_date", "")

        # organic_matter is optional — store NULL if not provided
        organic_matter_raw = request.form.get("organic_matter", "").strip()
        organic_matter = float(organic_matter_raw) if organic_matter_raw else None

        if not sample_date_str:
            flash("Sample date is required.", "warning")
            return redirect(url_for('user.add_soil_view', farm_id=farm_id))

        sample_date = datetime.strptime(sample_date_str, "%Y-%m-%d").date()

        # Insert into Soil_Profile
        cursor.execute("""
            INSERT INTO Soil_Profile
                (farm_id, soil_type_id, ph_level, organic_matter_pct, sample_date)
            VALUES (?, ?, ?, ?, ?)
        """, (farm_id, soil_type_id, ph_level, organic_matter, sample_date))

        conn.commit()
        conn.close()

        flash("Soil profile saved successfully!", "success")
        # Send farmer straight to advisory after setup is complete
        return redirect(url_for('user.advisory'))

    except Exception as e:
        print(f"[SOIL PROFILE SAVE ERROR] {e}")
        flash(f"Could not save soil profile: {str(e)}", "danger")
        return redirect(url_for('user.add_soil_view', farm_id=farm_id))

# ─────────────────────────────────────────────────────────────
#  POST /user/generate_advisory
#  Fetches live weather, inserts it, runs SP, returns crops
# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
#  POST /user/generate_advisory
#  Generates advisory based on farm_id, calls API, updates records
# ─────────────────────────────────────────────────────────────
@user_bp.route("/generate_advisory", methods=["POST"])
@login_required
def generate_advisory():
    farmer_id = session.get("farmer_id")
    if not farmer_id:
        return jsonify({"error": "Unauthorized"}), 401
 
    # Grab incoming JSON payload
    data = request.get_json() if request.is_json else {}
    farm_id = data.get("farm_id")
    
    if not farm_id:
        return jsonify({"error": "farm_id is required"}), 400
 
    conn   = get_conn()
    cursor = conn.cursor()
 
    try:
        # ── STEP 1: GET FARM + LOCATION ──────────────────────
        cursor.execute(
            "SELECT farm_name, location_id FROM Farm WHERE farm_id = ? AND farmer_id = ?",
            (farm_id, farmer_id)
        )
        farm_row = cursor.fetchone()
        if not farm_row:
            return jsonify({"error": "Farm not found or access denied"}), 404
 
        farm_name   = farm_row[0]
        location_id = farm_row[1]

        cursor.execute(
            "SELECT COUNT(*) FROM Advisory_Logs WHERE farm_id = ?", 
            (farm_id,)
        )
        logs_exist = cursor.fetchone()[0] > 0

        if logs_exist:
            print(f"[BYPASS TRIGGERED] Advisory already exists for farm_id {farm_id}. Skipping calculation pipeline.")
            # Skip straight to reading the records (Step 6)
        else:
            print(f"[PIPELINE TRIGGERED] No logs found for farm_id {farm_id}. Executing calculation pipeline.")
 
        # ── STEP 2: GET VILLAGE NAME ─────────────────────────
            cursor.execute(
                "SELECT village_name FROM Location WHERE location_id = ?",
                (location_id,)
            )
            loc_row = cursor.fetchone()
            village = loc_row[0] if loc_row else "Taxila"
    
            # ── STEP 3: CALL WEATHER API ─────────────────────────
            api_key = "7429773056a34ee688c183031251012"
            url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={village}&days=1"
            
            # Initial fallbacks
            temp_c, avg_temp_c, min_temp_c, max_temp_c, rainfall_mm, humidity_pct = 25.0, 25.0, 20.0, 30.0, 0.0, 50
            
            try:
                weather_resp = requests.get(url, timeout=5)
                if weather_resp.status_code == 200:
                    weather_data = weather_resp.json()
                    current_w = weather_data["current"]
                    day       = weather_data["forecast"]["forecastday"][0]["day"]
                    
                    avg_temp_c   = day.get("avgtemp_c", avg_temp_c)
                    min_temp_c   = day.get("mintemp_c", min_temp_c)
                    max_temp_c   = day.get("maxtemp_c", max_temp_c)
                    rainfall_mm  = day.get("totalprecip_mm", rainfall_mm)
                    humidity_pct = current_w.get("humidity", humidity_pct)
            except Exception as api_err:
                print(f"[WEATHER API FALLBACK IN ADVISORY GENERATION] {api_err}")
    
            # ── STEP 4: INSERT WEATHER INTO DB (FIXED: Duplicated location_id parameter removed) ──
            cursor.execute("""
                INSERT INTO Weather_Record (
                    location_id, record_date, rainfall_mm, humidity_pct, average_temp_c, min_temp_c, max_temp_c
                )
                VALUES (?, GETDATE(), ?, ?, ?, ?, ?)
            """, (
                location_id,
                rainfall_mm,
                int(humidity_pct),
                avg_temp_c,
                min_temp_c,
                max_temp_c,
            ))
            conn.commit()
    
            # ── STEP 5: RUN STORED PROCEDURE (FIXED: Realigned to use farmer_id wrapper) ──
            cursor.execute("EXEC GetCropByFarmName ?", (farm_name,))
            while cursor.nextset():
                pass
            conn.commit()
 
        # ── STEP 6: READ ADVISORY RESULTS (FIXED: Re-using clean sequential cursor, match_score used) ──
        cursor.execute("""
            SELECT TOP 10
                c.crop_name,
                c.crop_category,
                al.generated_date,
                al.match_score
            FROM Advisory_Logs al
            INNER JOIN Crops c ON c.crop_id = al.crop_id
            WHERE al.farm_id = ?
            ORDER BY al.generated_date DESC
        """, (farm_id,))
 
        columns = [col[0] for col in cursor.description]
        recommendations = []
        for row in cursor.fetchall():
            recommendations.append(dict(zip(columns, row)))
 

        # ── STEP 7: GAP ANALYSIS ─────────────────────────────
        try:
            cursor.execute("{CALL GetCropGapAnalysis(?)}", (farm_name,)) 
            
            # Fetch column names to map rows to dictionaries
            columns = [column[0] for column in cursor.description]
            
            filtered_crops = []
            
            for row in cursor.fetchall():
                # Convert row tuple into a handy dictionary
                crop_data = dict(zip(columns, row))
                
                # 2. Track only the metrics that failed for this crop
                failures = {}
                
                if crop_data.get('temp_status') == 'FAIL':
                    failures['temperature'] = {
                        'gap': round(float(crop_data['temp_distance_from_threshold']), 2)
                    }
                    
                if crop_data.get('rain_status') == 'FAIL':
                    failures['rainfall'] = {
                        'gap': round(float(crop_data['rain_distance_from_threshold']), 0) # Whole number for rain
                    }
                    
                if crop_data.get('ph_status') == 'FAIL':
                    failures['ph'] = {
                        'gap': round(float(crop_data['ph_distance_from_threshold']), 2)
                    }
                
                # 3. Only include the crop if it actually has at least one failure
                if failures:
                    filtered_crops.append({
                        "crop_name": crop_data['crop_name'],
                        "proximity_score": round(float(crop_data['proximity_score']), 1),
                        "failures": failures
                    })
                print(f"[GAP ANALYSIS DEBUG] Crop: {crop_data['crop_name']}, Failures: {failures}")
        except Exception as gap_err:
            print(f"[GAP ANALYSIS ERROR] {gap_err}")
            filtered_crops = []

        return jsonify({
            "success": True,
            "recommendations": recommendations,
            "gap_analysis": filtered_crops
        })
 
    except Exception as e:
        conn.rollback()
        print(f"[generate_advisory ERROR] {e}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
 
    finally:
        cursor.close()
        conn.close()
 
 
# ─────────────────────────────────────────────────────────────
#  GET /user/advisory
#  Renders the advisory page with farm list + gap analysis
# ─────────────────────────────────────────────────────────────
@user_bp.route("/advisory", methods=["GET"])
@login_required
def advisory():
    farmer_id    = session.get("farmer_id")
    farms        = []
    
 
    try:
        conn   = get_conn()
        cursor = conn.cursor()
 
        # Farm dropdown list
        cursor.execute("""
            SELECT farm_id, farm_name
            FROM Farm
            WHERE farmer_id = ?
            ORDER BY farm_id DESC
        """, (farmer_id,))
 
        for row in cursor.fetchall():
            farms.append({
                "farm_id":   row[0],
                "farm_name": row[1],
            })
 
        # Gap analysis SP — pyodbc rows use index access
        # Ensure 'GetCropGapAnalysis' exists or handles farmer parameters gracefully 
    except Exception as e:
        print(f"[ADVISORY VIEW ERROR] {e}")
        flash("Could not load advisory data.", "danger")
 
    return render_template(
        "user_advisory.html",
        farms=farms,
    )
 
 
# ─────────────────────────────────────────────────────────────
#  GET /user/api/farm-details/<farm_id>
# ─────────────────────────────────────────────────────────────
@user_bp.route("/api/farm-details/<int:farm_id>", methods=["GET"])
@login_required
def api_farm_details(farm_id):
    farmer_id = session.get("farmer_id")
    if not farmer_id:
        return jsonify({"error": "Unauthorized"}), 401
 
    try:
        conn   = get_conn()
        cursor = conn.cursor()
 
        # 1. Verify ownership + fetch farm & location data
        cursor.execute("""
            SELECT f.farm_name, f.area_acres,
                   l.village_name, l.district, f.location_id
            FROM Farm f
            INNER JOIN Location l ON f.location_id = l.location_id
            WHERE f.farm_id = ? AND f.farmer_id = ?
        """, (farm_id, farmer_id))
 
        farm_row = cursor.fetchone()
        if not farm_row:
            conn.close()
            return jsonify({"error": "Farm not found or access denied"}), 404
 
        farm_name    = farm_row[0]
        area_acres   = farm_row[1]
        village_name = farm_row[2]
        district     = farm_row[3]
        location_id  = farm_row[4]
 
        # 2. Latest weather record for this location
        cursor.execute("""
            SELECT TOP 1 average_temp_c, rainfall_mm, humidity_pct
            FROM Weather_Record
            WHERE location_id = ?
            ORDER BY record_date DESC
        """, (location_id,))
 
        weather_row = cursor.fetchone()
        avg_temp = weather_row[0] if weather_row else "N/A"
        rainfall = weather_row[1] if weather_row else "N/A"
        humidity = weather_row[2] if weather_row else "N/A"
 
        # 3. Latest soil profile for this farm
        cursor.execute("""
            SELECT TOP 1 st.soil_type, sp.ph_level
            FROM Soil_Profile sp
            INNER JOIN Soil_Type st ON sp.soil_type_id = st.soil_type_id
            WHERE sp.farm_id = ?
            ORDER BY sp.sample_date DESC
        """, (farm_id,))
 
        soil_row  = cursor.fetchone()
        soil_type = soil_row[0] if soil_row else "No profile added"
        ph_level  = soil_row[1] if soil_row else "N/A"
 
        conn.close()
 
        return jsonify({
            "farm_name":    farm_name,
            "area_acres":   area_acres,
            "village_name": village_name,
            "district":     district,
            "avg_temp":     avg_temp,
            "rainfall":     rainfall,
            "humidity":     humidity,
            "soil_type":    soil_type,
            "ph_level":     ph_level,
        })
 
    except Exception as e:
        print(f"[API FARM DETAILS ERROR] {e}")
        return jsonify({"error": str(e)}), 500