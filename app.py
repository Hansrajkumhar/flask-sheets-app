from flask import Flask, jsonify
import sheet
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "✅ Flask Sheets API is running",
        "usage": {
            "GET": "/run",
            "POST": "/run with JSON { 'value': 'ProjectName' } (currently ignored, matches local script)"
        }
    })

@app.route("/run", methods=["GET"])
def run_code():
    try:
        # Call the sheet processing function
        output = sheet.process_projects()
        return jsonify(output)
    except Exception as e:
        app.logger.error(f"Exception in /run: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Port 5000 for local testing; Render will use $PORT
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
