import os
import logging
import numpy as np
import joblib
from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import pooling, Error

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")

# Environment & Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "battery_rul_db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# ------------------------------------------------------------------------------
# 1. Graceful Database Connection Setup
# ------------------------------------------------------------------------------
db_pool = None

def init_db_pool():
    global db_pool
    try:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="battery_pool",
            pool_size=5,
            pool_reset_session=True,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info(f"Database connection pool successfully established to '{DB_NAME}' at {DB_HOST}:{DB_PORT}.")
    except Error as e:
        db_pool = None
        logger.warning(f"Unable to connect to MySQL database ({e}). Application running in NO-DB/OFFLINE mode.")

init_db_pool()

# ------------------------------------------------------------------------------
# 2. ML Artifact Loading (Model & Scaler)
# ------------------------------------------------------------------------------
MODEL_PATH = os.path.join("models", "mlp_rul_model.pkl")
SCALER_PATH = os.path.join("models", "scaler.pkl")

# Fallback to root directory if not present in models/
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "mlp_rul_model.pkl"
if not os.path.exists(SCALER_PATH):
    SCALER_PATH = "scaler.pkl"

model = None
scaler = None

try:
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        logger.info("ML model and scaler loaded successfully.")
    else:
        logger.error(f"Artifacts not found at {MODEL_PATH} or {SCALER_PATH}. Run 'python models/trainer.py' first.")
except Exception as e:
        logger.error(f"Failed to load ML artifacts: {e}")

# ------------------------------------------------------------------------------
# 3. Web UI Routes
# ------------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/login")
def login():
    return render_template("login.html")

# ------------------------------------------------------------------------------
# 4. REST API Endpoints
# ------------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None,
        "database_connected": db_pool is not None
    }), 200


@app.route("/api/predict", methods=["POST"])
def predict_rul():
    if model is None or scaler is None:
        return jsonify({"error": "ML Model artifacts are not loaded. Train the model first."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400

        # Extract features with defaults
        capacity_ah = float(data.get("capacity_ah", 2.0))
        peak_voltage_v = float(data.get("peak_voltage_v", 4.2))
        avg_temp_c = float(data.get("avg_temp_c", 25.0))
        internal_resistance_ohm = float(data.get("internal_resistance_ohm", 0.015))

        # 1. Compute State of Health (SOH %) based on nominal 2.0 Ah
        nominal_capacity = 2.0
        soh_percent = min(100.0, max(0.0, (capacity_ah / nominal_capacity) * 100.0))

        # 2. Scale features & predict RUL using MLP Regressor
        input_features = np.array([[capacity_ah, peak_voltage_v, avg_temp_c, internal_resistance_ohm]])
        input_scaled = scaler.transform(input_features)
        
        predicted_rul = float(model.predict(input_scaled)[0])
        predicted_rul = max(0.0, round(predicted_rul, 2))

        # 3. Save prediction to MySQL if database is connected
        if db_pool:
            try:
                conn = db_pool.get_connection()
                cursor = conn.cursor()
                query = """
                    INSERT INTO predictions 
                    (capacity_ah, peak_voltage_v, avg_temp_c, internal_resistance_ohm, soh_percent, predicted_rul_cycles)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (capacity_ah, peak_voltage_v, avg_temp_c, internal_resistance_ohm, round(soh_percent, 2), predicted_rul))
                conn.commit()
                cursor.close()
                conn.close()
            except Error as db_err:
                logger.warning(f"Failed to persist prediction log to MySQL: {db_err}")

        # 4. Return response payload to dashboard
        return jsonify({
            "status": "success",
            "capacity_ah": capacity_ah,
            "soh_percent": round(soh_percent, 2),
            "predicted_rul_cycles": predicted_rul,
            "database_logged": db_pool is not None
        }), 200

    except Exception as e:
        logger.error(f"Inference error: {e}")
        return jsonify({"error": str(e)}), 400


@app.route("/api/history", methods=["GET"])
def get_history():
    if not db_pool:
        return jsonify({"status": "offline", "data": [], "message": "Database disconnected. Running in offline mode."}), 200

    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 20")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "data": records}), 200
    except Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------------------------------------------------------------------
# 5. Server Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting Battery RUL Prediction Flask Server...")
    app.run(host="127.0.0.1", port=5000, debug=True)