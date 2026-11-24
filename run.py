import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug só liga se você pedir: $env:FLASK_DEBUG = "1"
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")