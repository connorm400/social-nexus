from app import app
app.app_context().push()
from app import db
db.create_all()