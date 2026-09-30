from flask import Flask, jsonify
from flask_cors import CORS
import subprocess, sys, os
app = Flask(__name__)
CORS(app) # allow frontend calls
@app.route("/")
def run_jobs():
    try:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        result = subprocess.run(
        [sys.executable, "app.py"],
        cwd=backend_dir,
        capture_output=True,
        text=True
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500
        return jsonify({"output": result.stdout.strip().split("\n")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(debug=True, port=5000)