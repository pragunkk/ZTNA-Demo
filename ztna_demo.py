"""
Legacy entrypoint kept for convenience.
Preferred: `gunicorn wsgi:app` or `python -m flask --app wsgi run`
"""
from ztna_demo.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
