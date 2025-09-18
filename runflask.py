import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Flask running at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)