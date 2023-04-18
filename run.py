from web_app import app
import os

if __name__ == "__main__":
    app.run(debug=True if not os.environ.get('DYNO') else False)