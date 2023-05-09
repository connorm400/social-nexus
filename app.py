from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submissions.db'
db = SQLAlchemy(app)

class entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(400), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "<entry %r>" % self.id


@app.route('/')
def index():
    return render_template('index.html')

'''
@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
'''

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
