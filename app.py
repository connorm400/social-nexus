# Import libraries - 
# Flask is for backend, sqlalchemy is for the database, flask_login for session management / login, Bcrypt for password encryption

from flask import Flask, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime

# Import secretkey from secretkey.py (its supposed to be secret so you'd need to generate it yourself)
from secretkey import *
# custom banned words from censoredWords.py
from censoredWords import *

# Set up flask
app = Flask(__name__)
app.secret_key = secretkey

# set up bcrypt
bcrypt = Bcrypt(app)

# Set up sqlalchemy (Edit next line to change database uri)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
db = SQLAlchemy(app)

# set up flask_login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Set up database relationship with post likes and comment likes
# (Every post like needs a post to like, etc)
post_likes = db.Table('post_likes',
                         db.Column('post_id', db.Integer, db.ForeignKey('entry.id'), primary_key=True),
                         db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True)
                         )

comment_likes = db.Table('comment_likes',
                         db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'), primary_key=True),
                         db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True)
                         )

# Configure User table 
# (UserMixin is a flask_login module that adds methods needed for login ex: is_authenticated)
class User(UserMixin, db.Model):   
    __tablename__ = 'User' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    pw_hash = db.Column(db.String(400), nullable=False) # Password is stored in hashed form with bcrypt
    deleted = db.Column(db.Boolean, nullable=False) # Wether or not the user has been deleted (defaults to np)
    bio = db.Column(db.String(400), nullable=True) # user bio (Isnt required)
    def __repr__(self): # representation so its more convinient to work with in python shell
        return "<user %r>" %self.id

class entry(db.Model): # entry basically means post
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False) # title has a max of 150 characters
    content = db.Column(db.String(400), nullable=False) # content has a max of 400 characters
    image = db.Column(db.String(500), nullable=True) # link to an image (optional)
    tag = db.Column(db.String(50), nullable=True) # tag with the post
    date_created = db.Column(db.DateTime, default=datetime.now)
    votes = db.Column(db.Integer, default=0) # voter relationship is there so that a user can only like a post once
    voters = db.relationship('User', secondary=post_likes, backref=db.backref('post_likes', lazy='dynamic'), 
                             primaryjoin=(post_likes.c.post_id == id), 
                             secondaryjoin=(post_likes.c.user_id == User.id)
    )
    author = db.Column(db.Integer, nullable=False) # user ID of author
    author_name = db.Column(db.String(20), nullable=False) # authors name to show on the post
    comments = db.relationship('comment', backref="entry", lazy=True, cascade='all, delete') # relationship with the comments on the post
    def __repr__(self):
        return "<entry %r>" % self.id


class comment(db.Model): #all of this is basically the same to the entry table
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    votes = db.Column(db.Integer, default=0)
    voters = db.relationship('User', secondary=comment_likes, backref=db.backref('comment_likes', lazy='dynamic'), 
                             primaryjoin=(comment_likes.c.comment_id == id), 
                             secondaryjoin=(comment_likes.c.user_id == User.id)
    )
    author = db.Column(db.Integer, nullable=False)
    author_name = db.Column(db.String(20), nullable=False) 
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'), # relationship with original post
        nullable=False)
    def __repr__(self): 
        return "<comment %r>" % self.id

# function tht checks if phrase has any censored words
def has_censored_words(phrase): 
    for censored_word in censored_words:
        if phrase.find(censored_word) != -1: # .find() returns -1 if it doesn't find the phrase
            return True

# these lines are needed for flask_login 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# first app route. GET method is a regular request that returns the webpage.
# POST request is when the login form is submitted
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST' :
        # request username and password candidate 
        username = request.form['username']
        username = username.lower() # password are automatically lowercase
        pw_candidate = request.form['password']
        
        # remember me checkbox
        if request.form.get('remember-me') != True:
            remember_me = False
        try: # put into a try statement so that a flask error message doesn't show up if anything goes wrong
            user_to_login = User.query.filter_by(name=username).first() # finds the user with the same username
            if bcrypt.check_password_hash(user_to_login.pw_hash, pw_candidate): # checks if password hash and password candidate's hash are the same 
                login_user(user_to_login, remember=remember_me) # actually log in user
                flash ('succesfully logged in')
                return redirect('/') # redirect to index once logged in
            else:
                flash ('Invalid username or password.')
                return redirect('/login')
        except:
            flash ('user doesnt exist')
            return redirect('/login')
        
    elif request.method == 'GET':
        return render_template('login.html') # render ./login.html 
                                             # render_template basically renders an html document with jinja2 
    
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        # extract username and new password from form
        username = request.form['username']
        username = username.lower()
        password = request.form['password']

        if has_censored_words(username):
            flash ('username has banned words')
            return redirect ('/signup') # redirect early if username has banned words

        # check if a user already has that name
        if User.query.filter_by(name=username).first():
            flash ('Someone already has that username sorry')
            return redirect('/signup')
        else:
            pw_hash = bcrypt.generate_password_hash(password) # store password in database as a password hash (encrypted)
            new_user = User(name=username, pw_hash=pw_hash, deleted=False)
            try:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                return redirect('/')
            except:
                return 'error with making new user in database'
    elif request.method == 'GET':
        return render_template('signup.html')
    
# logs out current user. Requires login 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash ("succesfully logged out")
    return redirect('/')

# render index (the page with all the posts etc)
@app.route('/')
def index():
    submissions = entry.query.order_by(entry.votes.desc()).all() # sort posts by most vores
    return render_template(
        'index.html', current_user=current_user, submissions=submissions,tagpage=False
        )
    
# same as index but posts are sorted by newest
@app.route('/new')
def newsort():
    submissions = entry.query.order_by(entry.date_created.desc()).all()
    return render_template(
        'index.html', current_user=current_user, submissions=submissions, tagpage=False
        )

# only show posts for a certain tag
# path is like this: /tag/help
@app.route('/tag/<string:tag>')
def tagsearch(tag):
    submissions = entry.query.filter_by(tag=tag).order_by(entry.votes.desc()).all()
    return render_template(
        'index.html', current_user=current_user, submissions=submissions, tagpage=True, currenttag=tag
        )

# /tag but sorted by new
@app.route('/tag/<string:tag>/new')
def tagsearchnew(tag):
    submissions = entry.query.filter_by(tag=tag).order_by(entry.date_created.desc()).all()
    return render_template(
        'index.html', current_user=current_user, submissions=submissions, tagpage=True, currenttag=tag
        )

# dropper is where posts are made. 
@app.route('/dropper', methods=['POST', 'GET'])
@login_required
def submit():
    if request.method == 'POST':
        # extracting data from the form
        submission_content = request.form['content'] 
        post_title = request.form['title']
        post_tag = request.form['tag']
        image = request.form['image']
        author = current_user.id
        author_name = current_user.name
        if has_censored_words(submission_content) or has_censored_words(post_title):
            flash ('Post has banned words')
            return redirect ('/dropper')

        new_submission = entry(content=submission_content, title=post_title, tag=post_tag, author=author, author_name=author_name, image=image)

        try: 
            db.session.add(new_submission) # adding the task extracted from the form to the database and commiting to save
            db.session.commit()
            return redirect('/post/%r' %new_submission.id) # redirecting to the index; since this would be a GET method thingy it would be served the html document
        except: # if there is ever an error itl show this message
            return 'there was an issue making your submission'
    elif request.method == 'GET':
        return render_template('dropper.html') # render ./dropper.html

# deletes post with id in app route. Must be the author or the admin to delete the post
@app.route('/del/<int:id>')
@login_required
def deleteentry(id):
    entry_to_delete = entry.query.get_or_404(id)
    if entry_to_delete.author == current_user.id or current_user.name == 'admin':
        try: #have a try statement just incase something goes wrong
            db.session.delete(entry_to_delete)
            db.session.commit()
            return redirect('/')
        except:
            return 'issue with deleting entry in database'
    else:
        flash ("need to be the author to delete this post")
        return redirect('/post/%r' %id) # redirect back to original post

# deletes comment
@app.route('/del/comment/<int:post_id>/<int:comment_id>')
@login_required
def deletecomment(post_id, comment_id):
    comment_to_delete = comment.query.get_or_404(comment_id)
    if comment_to_delete.author == current_user.id or current_user.name == 'admin':
        try: #have a try statement just incase something goes wrong
            db.session.delete(comment_to_delete)
            db.session.commit()
            return redirect('/post/%r' %post_id)
        except:
            return 'issue with deleting comment in database'
    else:
        flash ("need to be the author to delete this comment")
        return redirect('/post/%r' %post_id)
    
# like a post. Finds post to like. Appends current_user's id to the post's voters so that you can only like a post once 
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

# upvote a comment
@app.route('/upvote-comment/<int:post_id>/<int:comment_id>')
def upvotecomment(post_id, comment_id):

    comment_to_upvote = comment.query.get_or_404(comment_id)
    if current_user in comment_to_upvote.voters:
        flash ('You already liked this post')
        return redirect('/post/%r' % post_id)
    else:
        comment_to_upvote.votes += 1
        comment_to_upvote.voters.append(current_user)
        try:
            db.session.commit()
            return redirect('/post/%r' % post_id)
        except:
            return 'issue with voting whoops'
    
# full page post. Shows all comments and such
@app.route('/post/<int:id>', methods=['POST', 'GET'])
def fullpagepost(id):
    comments = comment.query.filter_by(entry_id=id).order_by(comment.votes.desc()).all()
    
    specific_post = entry.query.get_or_404(id)
    return render_template(
        'post.html', post=specific_post, comments=comments, current_user=current_user
        )

# write a comment. Login required. <int:id> is for the original post id
@app.route('/comment/<int:id>', methods=['POST'])
@login_required
def commentPage(id):
    comment_content = request.form['content']
    author = current_user.id
    author_name = current_user.name

    if has_censored_words(comment_content):
        flash ('Comment includes banned words')
        return redirect('/post/%r' %id)

    new_comment = comment(content=comment_content, entry_id=id, author=author, author_name=author_name)
    
    try:
        db.session.add(new_comment)
        db.session.commit()
        return redirect('/post/%r' %id)
    except:
        return "issue with making comment"

# User's page. Shows all their post and comments plus bio
@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = entry.query.filter_by(author=user_id).all()
    comments = comment.query.filter_by(author=user_id).all()

    return render_template(
        'profile.html', current_user=current_user, posts=posts, user=user, comments=comments
        )

# settings page. only has a GET method
@app.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template(
        'settings/settings.html', user=current_user
        )

# change user bio
@app.route('/change-bio', methods=['POST'])
@login_required
def change_bio():
    new_bio = request.form['content']
    if has_censored_words(new_bio):
        flash ('bio contains banned words')
        return redirect('/settings')
    try:
        current_user.bio = new_bio
        db.session.commit()
        flash ('bio succesfully changed')
        return redirect('/settings')
    except:
        flash ('issue with changing account bio')
        return redirect('/settings')

# delete account. Get method returns a form that asks for your password 
# POST method will delete all posts and comments assuming the password is correct 
@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delaccount():
    if request.method == 'GET':
        return render_template(
            'settings/delete-account.html', user=current_user
            )
    elif request.method == 'POST':
        user_to_delete = current_user
        pw_candidate = request.form['password']
        if bcrypt.check_password_hash(user_to_delete.pw_hash, pw_candidate):
            
            # find posts made by the user to delete to replace author name with 'deleted user'
            posts = entry.query.filter_by(author=user_to_delete.id).all()
            comments = comment.query.filter_by(author=user_to_delete.id).all()
            try:
                #comments = comment.query.filter_by(entry_id=id).order_by(comment.votes.desc()).all()
                for post in posts:
                    post.author_name = '[deleted user]'
                    post.content = 'author of this post has been deleted'
                for Comment in comments:
                    Comment.author_name = '[deleted user]'
                    Comment.content = 'author of this post has been deleted'
                
                #db.session.delete(user_to_delete) #you cant just delete the user otherwise the id for the other users will be messed up
                user_to_delete.name = 'deleted'
                user_to_delete.bio = 'this user has been deleted'
                user_to_delete.pw_hash = '0'
                user_to_delete.deleted = True
                db.session.commit()
                logout_user()
                flash ('account deleted')
                return redirect ('/')
            except:
                return 'Unable to delete account'
        else: 
            flash ('Incorrect password')
            return redirect ('/settings')
        
# password change page. GET method is for the password change form
# POST will change password if the form gives the right original password
@app.route('/pw-change', methods=['GET', 'POST'])
@login_required
def pw_change():
    if request.method == 'GET':
        return render_template(
            'settings/pw-change.html', user=current_user
            )
    if request.method == 'POST':
        pw_candidate = request.form['password']
        new_pw = request.form['newpassword']
        if bcrypt.check_password_hash(current_user.pw_hash, pw_candidate):
            pw_hash = bcrypt.generate_password_hash(new_pw)
            try:
                current_user.pw_hash = pw_hash
                db.session.commit()
                flash ('password succesfully changed')
                return redirect('/')
            except:
                return "didnt work"
        else:
            flash ('incorrect password')
            return redirect ('/pw-change')
        
# more flask settings stuff
if __name__ == "__main__":
    with app.app_context(): # look at setupdb.py
        db.create_all()
    app.run(debug=False)
