import argparse
import logging
import threading
import traceback
from flask import Flask, request, jsonify, render_template

# Import your UFO modules from the Microsoft UFO framework
from ufo.config.config import Config
from ufo.module.client import UFOClientManager
from ufo.module.sessions.session import SessionFactory

# Set up logging if needed
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def run_ufo_task(task, mode, plan, req):
    """
    Function to run the UFO task.
    This wraps the existing logic from your main() function.
    """
    try:
        # Create a session using the provided parameters
        sessions = SessionFactory().create_session(
            task=task,
            mode=mode,
            plan=plan,
            request=req,
        )
        # Instantiate and run the UFO client(s)
        clients = UFOClientManager(sessions)
        clients.run_all()
    except Exception as e:
        logger.error("Error running UFO task: %s", str(e))
        logger.error(traceback.format_exc())

# Route to render the homepage with a form
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/probe', methods=['GET'])
def probe():
    """
    A simple endpoint to verify that the service is up.
    """
    return jsonify({"status": "Service is operational"}), 200

@app.route('/ufo', methods=['POST'])
def ufo_endpoint():
    """
    This endpoint accepts either JSON or form data to trigger a UFO task.
    Expected keys: task, mode, plan, request.
    """
    # Determine if the request is JSON or form data
    if request.is_json:
        data = request.get_json(force=True)
    else:
        data = request.form

    task = data.get("task", "default_task")
    mode = data.get("mode", "normal")
    plan = data.get("plan", "")
    req = data.get("request", "")
    
    # Launch the task in a separate thread to avoid blocking the web server
    thread = threading.Thread(target=run_ufo_task, args=(task, mode, plan, req))
    thread.start()
    
    # Respond with a JSON message (you could also redirect to a status page)
    return jsonify({"status": "UFO task started", "task": task}), 200

if __name__ == '__main__':
    # Optionally add argument parsing for port or log file if needed
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="Port to run the Flask server on", type=int, default=5000)
    args = parser.parse_args()
    
    app.run(debug=True, host="0.0.0.0", port=args.port)
