import os
from dashboard import app
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    app.run(debug=os.environ.get('DEBUG', False), host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get('PORT', 5000)))