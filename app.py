from flask import Flask, request, jsonify
import sheet

app = Flask(__name__)

@app.route("/run", methods=["POST", "GET"])
def run_code():
    try:
        project_filter = None
        if request.method == "POST":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON"}), 400
            project_filter = data.get("value")
        output = sheet.process_projects(project_filter=project_filter)
        return jsonify(output)
    except Exception as e:
        app.logger.error(f"Exception in /run: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)  # Still use 0.0.0.0 for local network access