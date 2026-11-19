"""Entry point. Vercel and `flask run` both look for `app` here."""
import os

from pharmacy import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=int(os.environ.get("PORT", "5000")))
