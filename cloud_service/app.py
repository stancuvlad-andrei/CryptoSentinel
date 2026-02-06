from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

audit_log = []

@app.route('/')
def home():
    """Landing page to prove the cloud server is running."""
    return """
    <h1>CryptoSentinel Cloud Audit</h1>
    <p>Status: <span style='color:green'>ONLINE</span></p>
    <p>Endpoints: /audit (POST), /logs (GET)</p>
    """

@app.route('/audit', methods=['POST'])
def receive_audit():
    try:
        data = request.json
        
        # Create a log entry
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "price": data.get("price"),
            "source": request.remote_addr, # Shows IP of the sender
            "status": "LOGGED"
        }
        
        audit_log.append(entry)
        
        # Keep only last 10 logs
        if len(audit_log) > 10:
            audit_log.pop(0)
            
        print(f"[CLOUD] Logged event: {entry}")
        return jsonify({"message": "Audit received", "total_logs": len(audit_log)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """View the audit history (JSON)."""
    return jsonify(audit_log)

if __name__ == '__main__':
    app.run(debug=True, port=8080)