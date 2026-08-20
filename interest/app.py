from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

import mysql.connector
from flask import Flask, jsonify, render_template, request
from mysql.connector import Error

from config import DB_CONFIG

app = Flask(__name__)

DAYS_PER_YEAR = Decimal("365")


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def round_currency(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def round_interest(value):
    return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def calculate_interest(loan_amount, interest_rate, pledge_date, return_date):
    loan = Decimal(str(loan_amount))
    rate = Decimal(str(interest_rate))
    start = parse_date(pledge_date) if isinstance(pledge_date, str) else pledge_date
    end = parse_date(return_date) if isinstance(return_date, str) else return_date

    if end < start:
        raise ValueError("Return date cannot be before pledge date.")

    total_days = (end - start).days
    if total_days < 0:
        raise ValueError("Invalid date range.")

    # Annual rate converted to daily interest
    per_day_interest = (loan * rate / Decimal("100")) / DAYS_PER_YEAR
    total_interest = per_day_interest * Decimal(str(total_days))
    final_amount = loan + total_interest

    return {
        "total_days": total_days,
        "per_day_interest": float(round_interest(per_day_interest)),
        "total_interest": float(round_currency(total_interest)),
        "final_amount": float(round_currency(final_amount)),
    }


def row_to_dict(row):
    if row is None:
        return None

    data = dict(row)
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif hasattr(value, "isoformat"):
            data[key] = value.isoformat()
        elif isinstance(value, Decimal):
            data[key] = float(value)
    return data


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    payload = request.get_json(silent=True) or {}

    try:
        loan_amount = payload.get("loan_amount")
        interest_rate = payload.get("interest_rate")
        pledge_date = payload.get("pledge_date")
        return_date = payload.get("return_date")

        if not all([loan_amount, interest_rate, pledge_date, return_date]):
            return jsonify({"error": "Loan amount, interest rate, pledge date, and return date are required."}), 400

        if float(loan_amount) <= 0:
            return jsonify({"error": "Loan amount must be greater than zero."}), 400

        if float(interest_rate) < 0:
            return jsonify({"error": "Interest rate cannot be negative."}), 400

        result = calculate_interest(loan_amount, interest_rate, pledge_date, return_date)
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({"error": "Unable to calculate interest."}), 500


@app.route("/api/pledges", methods=["GET"])
def list_pledges():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT *
            FROM pledges
            ORDER BY created_at DESC
            """
        )
        pledges = [row_to_dict(row) for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return jsonify(pledges)
    except Error:
        return jsonify({"error": "Unable to fetch pledge records."}), 500


@app.route("/api/pledges", methods=["POST"])
def create_pledge():
    payload = request.get_json(silent=True) or {}

    required_fields = [
        "customer_name",
        "customer_phone",
        "jewellery_type",
        "jewellery_weight",
        "loan_amount",
        "interest_rate",
        "pledge_date",
        "return_date",
    ]

    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        calculation = calculate_interest(
            payload["loan_amount"],
            payload["interest_rate"],
            payload["pledge_date"],
            payload["return_date"],
        )

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO pledges (
                customer_name,
                customer_phone,
                customer_address,
                jewellery_type,
                jewellery_weight,
                jewellery_purity,
                jewellery_description,
                loan_amount,
                interest_rate,
                pledge_date,
                return_date,
                total_days,
                per_day_interest,
                total_interest,
                final_amount,
                status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                payload["customer_name"].strip(),
                payload["customer_phone"].strip(),
                payload.get("customer_address", "").strip() or None,
                payload["jewellery_type"].strip(),
                payload["jewellery_weight"],
                payload.get("jewellery_purity", "").strip() or None,
                payload.get("jewellery_description", "").strip() or None,
                payload["loan_amount"],
                payload["interest_rate"],
                payload["pledge_date"],
                payload["return_date"],
                calculation["total_days"],
                calculation["per_day_interest"],
                calculation["total_interest"],
                calculation["final_amount"],
                payload.get("status", "active"),
            ),
        )
        connection.commit()
        pledge_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({"id": pledge_id, **calculation, "message": "Pledge saved successfully."}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Error:
        return jsonify({"error": "Unable to save pledge record."}), 500


@app.route("/api/pledges/<int:pledge_id>", methods=["GET"])
def get_pledge(pledge_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pledges WHERE id = %s", (pledge_id,))
        pledge = row_to_dict(cursor.fetchone())
        cursor.close()
        connection.close()

        if not pledge:
            return jsonify({"error": "Pledge not found."}), 404
        return jsonify(pledge)
    except Error:
        return jsonify({"error": "Unable to fetch pledge record."}), 500


@app.route("/api/pledges/<int:pledge_id>", methods=["PUT"])
def update_pledge(pledge_id):
    payload = request.get_json(silent=True) or {}

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pledges WHERE id = %s", (pledge_id,))
        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            connection.close()
            return jsonify({"error": "Pledge not found."}), 404

        merged = {**existing, **payload}
        calculation = calculate_interest(
            merged["loan_amount"],
            merged["interest_rate"],
            merged["pledge_date"].isoformat() if hasattr(merged["pledge_date"], "isoformat") else merged["pledge_date"],
            merged["return_date"].isoformat() if hasattr(merged["return_date"], "isoformat") else merged["return_date"],
        )

        cursor.execute(
            """
            UPDATE pledges SET
                customer_name = %s,
                customer_phone = %s,
                customer_address = %s,
                jewellery_type = %s,
                jewellery_weight = %s,
                jewellery_purity = %s,
                jewellery_description = %s,
                loan_amount = %s,
                interest_rate = %s,
                pledge_date = %s,
                return_date = %s,
                total_days = %s,
                per_day_interest = %s,
                total_interest = %s,
                final_amount = %s,
                status = %s
            WHERE id = %s
            """,
            (
                merged.get("customer_name", existing["customer_name"]).strip(),
                merged.get("customer_phone", existing["customer_phone"]).strip(),
                (merged.get("customer_address") or "").strip() or None,
                merged.get("jewellery_type", existing["jewellery_type"]).strip(),
                merged.get("jewellery_weight", existing["jewellery_weight"]),
                (merged.get("jewellery_purity") or "").strip() or None,
                (merged.get("jewellery_description") or "").strip() or None,
                merged.get("loan_amount", existing["loan_amount"]),
                merged.get("interest_rate", existing["interest_rate"]),
                merged.get("pledge_date", existing["pledge_date"]),
                merged.get("return_date", existing["return_date"]),
                calculation["total_days"],
                calculation["per_day_interest"],
                calculation["total_interest"],
                calculation["final_amount"],
                merged.get("status", existing["status"]),
                pledge_id,
            ),
        )
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"id": pledge_id, **calculation, "message": "Pledge updated successfully."})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Error:
        return jsonify({"error": "Unable to update pledge record."}), 500


@app.route("/api/pledges/<int:pledge_id>", methods=["DELETE"])
def delete_pledge(pledge_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM pledges WHERE id = %s", (pledge_id,))
        connection.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        connection.close()

        if not deleted:
            return jsonify({"error": "Pledge not found."}), 404
        return jsonify({"message": "Pledge deleted successfully."})
    except Error:
        return jsonify({"error": "Unable to delete pledge record."}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
