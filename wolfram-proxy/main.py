from flask import Flask, request, jsonify
from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr
import threading

app = Flask(__name__)
session_lock = threading.Lock()

# Initialize Wolfram session (lazy loading)
_session = None

def get_session():
    global _session
    if _session is None:
        with session_lock:
            if _session is None:
                _session = WolframLanguageSession("/usr/local/bin/WolframKernel")
    return _session

@app.route('/eval', methods=['GET', 'POST'])
def evaluate():
    """Evaluate Wolfram code from 'code' parameter"""
    code = request.args.get('code') if request.method == 'GET' else request.form.get('code')
    
    if not code:
        return jsonify({'error': 'Missing code parameter'}), 400
    
    try:
        session = get_session()
        result = session.evaluate(wlexpr(code))
        return jsonify({'result': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8010, debug=False)
