from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submissions.db'
db = SQLAlchemy(app)

class entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.String(400), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self):
        return "<entry %r>" % self.id


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dropper', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        submission_content = request.form['content'] # extracting data from the form
        post_title = request.form['title']
        new_submission = entry(content=submission_content, title=post_title) 

        try: 
            db.session.add(new_submission) # adding the task extracted from the form to the database and commiting to save
            db.session.commit()
            return redirect('/') # redirecting to the index; since this would be a GET method thingy it would be served the html document
        except: # if there is ever an error itl show this message
            return 'there was an issue making your submission'
    elif request.method == 'GET':
        return render_template('dropper.html')

@app.route('/recipient')
def viewentries():
    submissions = entry.query.order_by(entry.date_created).all()
    return render_template('recipient.html', submissions=submissions)

@app.route('/del/<int:id>')
def delete(id):
    entry_to_delete = entry.query.get_or_404(id)

    try: #have a try statement just incase something goes wrong
        db.session.delete(entry_to_delete)
        db.session.commit()
        return redirect('/recipient')
    except:
        return 'issue with deleting entry in database'

@app.route('/post/<int:id>')
def fullpagepost(id):
    specific_post = entry.query.get_or_404(id)
    return render_template('post.html', post=specific_post)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
