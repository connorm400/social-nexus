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
    votes = db.Column(db.Integer, default=0)
    comments = db.relationship('comment', backref="entry", lazy=True, cascade='all, delete')
    def __repr__(self):
        return "<entry %r>" % self.id

class comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    votes = db.Column(db.Integer, default=0)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'),
        nullable=False)
    def __repr__(self):
        return "<comment %r>" % self.id

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
def deleteentry(id):
    entry_to_delete = entry.query.get_or_404(id)
    try: #have a try statement just incase something goes wrong
        db.session.delete(entry_to_delete)
        db.session.commit()
        return redirect('/recipient')
    except:
        return 'issue with deleting entry in database'

@app.route('/del/comment/<int:post_id>/<int:comment_id>')
def deletecomment(post_id, comment_id):
    comment_to_delete = comment.query.get_or_404(comment_id)
    try: #have a try statement just incase something goes wrong
        db.session.delete(comment_to_delete)
        db.session.commit()
        return redirect('/post/%r' %post_id)
    except:
        return 'issue with deleting comment in database'

@app.route('/upvote-post/<int:id>')
def upvotepost(id):
    entry_to_upvote = entry.query.get_or_404(id)

    entry_to_upvote.votes += 1
    try:
        db.session.commit()
        return redirect('/post/%r' % id)
    except:
        return 'issue with voting whoops'

@app.route('/upvote-comment/<int:post_id>/<int:comment_id>')
def upvotecomment(post_id, comment_id):

    comment_to_upvote = comment.query.get_or_404(comment_id)

    comment_to_upvote.votes += 1
    try:
        db.session.commit()
        return redirect('/post/%r' % post_id)
    except:
        return 'issue with voting whoops'
    
@app.route('/post/<int:id>', methods=['POST', 'GET'])
def fullpagepost(id):
    if request.method == 'GET':
        comments = comment.query.filter_by(entry_id=id).all()
        specific_post = entry.query.get_or_404(id)
        return render_template('post.html', post=specific_post, comments=comments)
    
    
    elif request.method == 'POST': # for making comments
        comment_content = request.form['content']
        new_comment = comment(content=comment_content, entry_id=id)

        try:
            db.session.add(new_comment)
            db.session.commit()
            return redirect('/post/%r' %id)
        except:
            return "issue with making comment"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
