import os

STATICPREFIX=os.environ.get("STATICPREFIX", "/static/")
STARTING_API_KEY=os.environ.get("STARTING_API_KEY", ":)")
DB_URL=os.environ.get("DB_URL", "localhost:3322")
DB_USER=os.environ.get("DB_USER", "immudb")
DB_PASS=os.environ.get("DB_PASS", "immudb")
DB_NAME=os.environ.get("DB_NAME","defaultdb")
STATEFILE=os.environ.get("STATEFILE", None)