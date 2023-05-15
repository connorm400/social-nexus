from flask import Flask, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime

from secretkey import *

app = Flask(__name__)
app.secret_key = secretkey

bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submissions.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

post_likes = db.Table('post_likes',
                         db.Column('post_id', db.Integer, db.ForeignKey('entry.id'), primary_key=True),
                         db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True)
                         )

class User(UserMixin, db.Model):   
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    #password = db.Column(db.String(20), nullable=False)
    pw_hash = db.Column(db.String(400), nullable=False)
    
    def __repr__(self):
        return "<user %r>" %self.id

class entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.String(400), nullable=False)
    image = db.Column(db.String(500), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    votes = db.Column(db.Integer, default=0)
    voters = db.relationship('User', secondary=post_likes, backref=db.backref('liked_posts', lazy='dynamic'))
    author = db.Column(db.Integer, nullable=False)
    author_name = db.Column(db.String(20), nullable=False)
    comments = db.relationship('comment', backref="entry", lazy=True, cascade='all, delete')
    def __repr__(self):
        return "<entry %r>" % self.id


class comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    votes = db.Column(db.Integer, default=0)
    author = db.Column(db.Integer, nullable=False)
    author_name = db.Column(db.String(20), nullable=False) # this is a terrible solution to a problem I have but whatever
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'),
        nullable=False)
    def __repr__(self):
        return "<comment %r>" % self.id

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST' :
        username = request.form['username']
        username = username.lower()
        pw_candidate = request.form['password']
        
        if request.form.get('remember-me') != True:
            remember_me = False
        try:
            user_to_login = User.query.filter_by(name=username).first()
            if bcrypt.check_password_hash(user_to_login.pw_hash, pw_candidate):
                login_user(user_to_login, remember=remember_me)
                return redirect('/')
            else:
                return 'Invalid username or password.', 'error'
        except:
            flash ('user doesnt exist')
            return redirect('/')
        
    elif request.method == 'GET':
        return render_template('login.html')
    
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        username = username.lower()
        password = request.form['password']

        # check if a user already has that name
        if User.query.filter_by(name=username).first():
            flash ('Someone already has that username sorry')
            return redirect('/signup')
        else:
            pw_hash = bcrypt.generate_password_hash(password)
            new_user = User(name=username, pw_hash=pw_hash)
            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect('/')
            except:
                return 'error with making new user in database'
    elif request.method == 'GET':
        return render_template('signup.html')
    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash ("succesfully logged out")
    return redirect('/')
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', logged_in=current_user.is_authenticated, name=current_user.name)
    else:
        return render_template('index.html', logged_in=current_user.is_authenticated)

@app.route('/dropper', methods=['POST', 'GET'])
@login_required
def submit():
    if request.method == 'POST':
        submission_content = request.form['content'] # extracting data from the form
        post_title = request.form['title']
        image = request.form['image']
        author = current_user.id
        author_name = current_user.name
        new_submission = entry(content=submission_content, title=post_title, author=author, author_name=author_name, image=image) 

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
    if current_user.is_authenticated:
        return render_template('recipient.html', submissions=submissions, logged_in=current_user.is_authenticated, name=current_user.name)
    else:
        return render_template('recipient.html', submissions=submissions, logged_in=current_user.is_authenticated)

@app.route('/del/<int:id>')
@login_required
def deleteentry(id):
    entry_to_delete = entry.query.get_or_404(id)
    if entry_to_delete.author == current_user.id:
        try: #have a try statement just incase something goes wrong
            db.session.delete(entry_to_delete)
            db.session.commit()
            return redirect('/recipient')
        except:
            return 'issue with deleting entry in database'
    else:
        flash ("need to be the author to delete this post")
        return redirect('/post/%r' %id)

@app.route('/del/comment/<int:post_id>/<int:comment_id>')
@login_required
def deletecomment(post_id, comment_id):
    comment_to_delete = comment.query.get_or_404(comment_id)
    if comment_to_delete.author == current_user.id:
        try: #have a try statement just incase something goes wrong
            db.session.delete(comment_to_delete)
            db.session.commit()
            return redirect('/post/%r' %post_id)
        except:
            return 'issue with deleting comment in database'
    else:
        flash ("need to be the author to delete this comment")
        return redirect('/post/%r' %post_id)
    
@app.route('/upvote-post/<int:id>')
@login_required
def upvotepost(id):
    try:
        entry_to_upvote = entry.query.get_or_404(id)
        if current_user in entry_to_upvote.voters:
            flash ('You already liked this post')
            return redirect('/post/%r' %id)
        else:
            entry_to_upvote.votes += 1
            entry_to_upvote.voters.append(current_user)
            try:
                db.session.commit()
                return redirect('/post/%r' % id)
            except:
                return 'issue with voting whoops'
    except:
        return 'issue with upvoting post'

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
    comments = comment.query.filter_by(entry_id=id).all()
    specific_post = entry.query.get_or_404(id)
    if current_user.is_authenticated:
        return render_template('post.html', post=specific_post, comments=comments, logged_in=current_user.is_authenticated, name=current_user.name)
    else:
        return render_template('post.html', post=specific_post, comments=comments, logged_in=current_user.is_authenticated)
    
    
@app.route('/comment/<int:id>', methods=['POST'])
@login_required
def commentPage(id):
    comment_content = request.form['content']
    author = current_user.id
    author_name = current_user.name
    new_comment = comment(content=comment_content, entry_id=id, author=author, author_name=author_name)
    
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
