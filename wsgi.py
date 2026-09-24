import os
from app import create_app, db

app = create_app('production')

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
