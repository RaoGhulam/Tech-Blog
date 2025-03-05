from flask import Flask, render_template, request, session, redirect, render_template_string, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Loading JSON File
with app.open_instance_resource('config.json') as config_file:
    params = json.load(config_file)["params"]

local_server = params['local_server']

# Connetcing with Database
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['production_uri']
    
db = SQLAlchemy(app)

# Posts Table
class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    subtitle = db.Column(db.Text, nullable=True)
    author = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Pending_Posts Table
class Pending_Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    subtitle = db.Column(db.Text, nullable=True)
    author = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Contacts Table
class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    phone_num = db.Column(db.Text, nullable=False)
    mes = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.Text, nullable=False)
    pass_word = db.Column(db.Text, nullable=False)


# Create tables
with app.app_context():
    db.create_all()

# Index Page
@app.route('/')
def home():
    _posts = Post.query.limit(params['no_of_posts']).all()
    return render_template('index.html', posts=_posts, params=params)

# About Page
@app.route('/about')
def about():
    return render_template('about.html', params=params)


# Contact Page
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        entry = Contact(name=name, phone_num=phone, mes=message, email=email)
        db.session.add(entry)
        db.session.commit()
    
    return render_template('contact.html', params=params)

# Slug Page for a Post
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()  # Fetch the specific post

    if not post:
        return "Post not found", 404
    
    return render_template('post.html', post=post, params=params)


# Dashboard Page
@app.route("/dashboard")
def dashboard():
    if 'user' in session and session['user']==params['admin_username']:
        action = request.args.get('action')  # Get action from URL
        sno = request.args.get('sno', type=int)  # Get sno and convert to int
        username = request.args.get('username') # Get username

        if action == "render_pending_post":
            _pending_posts = Pending_Post.query.all()
            return render_template('pending_posts.html', params=params, posts=_pending_posts)
        
        elif action == "approve_post" and sno is not None:
            post = Pending_Post.query.filter_by(sno=sno).first() # Search post in Pending Posts
            if post:
                approved_post = Post(title=post.title, subtitle=post.subtitle, author=post.author, slug=post.slug, content=post.content, date=post.date)
                db.session.add(approved_post)
                db.session.delete(post) # Remove from pending posts
                db.session.commit()
                return redirect('/dashboard')  # Redirect back to dashboard

        elif action == "render_manage_users":
            users = User.query.all()
            return render_template('users.html', params=params, users=users)
        
        elif action == "remove_user":
            user_ = User.query.filter_by(user_name=username).first()
            if user_:
                db.session.delete(user_)
                db.session.commit()
                return redirect('/dashboard')
            
        _posts = Post.query.all()
        response = make_response(render_template('dashboard.html', params=params, posts=_posts))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response
    
    else:
        return redirect('/login')




# Edit Page
@app.route("/edit/<string:sno>", methods=['GET','POST'])
def edit(sno):
    if 'user' in session:
        user = User.query.filter_by(user_name=session['user']).first()  # Get logged-in user
        if request.method=='POST':
            _title = request.form.get('title')
            _subtitle = request.form.get('subtitle')
            _author = "Admin" if session['user']==params['admin_username'] else user.user_name
            _slug = request.form.get('slug')
            _content = request.form.get('content')
            _date = datetime.now(timezone.utc)

            if sno=='0':
                if(session['user']==params['admin_username']): # Admin adding new post
                    post = Post(title=_title, subtitle=_subtitle, author=_author,slug=_slug, content=_content, date=_date)
                    db.session.add(post)
                    db.session.commit()
                    return redirect('/dashboard')
                else:                                          # User Adding new post
                    post = Pending_Post(title=_title, subtitle=_subtitle, author=_author,slug=_slug, content=_content, date=_date)
                    db.session.add(post)
                    db.session.commit()
                    session.pop('user')
                    return redirect('/')

            else:                                               # Edit Post
                post = Post.query.filter_by(sno=sno).first()
                if post.author == params['admin_username']:
                    post.title = _title
                    post.subtitle = _subtitle
                    post.slug = _slug
                    post.content = _content
                    post.date = _date
                    db.session.add(post)
                    db.session.commit()
                    return redirect('/dashboard')
                else:                                           # Edit persmission denied
                    return render_template_string("""
                        <h1>Error</h1>
                        <p>Admin does not have permission to edit other posts.</p>
                    """)

        _post = Post.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=_post, sno=sno)

# Delete Post
@app.route("/delete")
def delete():
    if 'user' in session and session['user']==params['admin_username']:
        action = request.args.get('action')  # Get action from URL
        sno = request.args.get('sno', type=int)  # Get sno and convert to int
        if action == "delete_pending_post":
            _post = Pending_Post.query.filter_by(sno=sno).first()  # Fetch the specific post in Post
            db.session.delete(_post)
            db.session.commit()
        elif action == "delete_post":
            _post = Post.query.filter_by(sno=sno).first()  # Fetch the specific post in Post
            db.session.delete(_post)
            db.session.commit()
        
        return redirect('/dashboard')

# Logout
@app.route("/logout")
def logout():
    session.pop('user')    
    return redirect('/')


# Login Page
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check for Admin
        if username==params['admin_username'] and password==params['admin_password']:
            session['user']=params['admin_username']
            return redirect('/dashboard')
        
        else:
            user = User.query.filter_by(user_name=username, pass_word=password).first()
            if user:  # If user exists, login successful
                session['user'] = user.user_name
                return redirect('/edit/0')
            else:
                return render_template('login.html', params=params, error="Invalid credentials")
    
    response = make_response(render_template('login.html', params=params))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# Sign-Up Page
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        _username = request.form.get('username')
        _psw = request.form.get('psw')

        # Check if username already exists
        existing_user = User.query.filter_by(user_name=_username).first()
        if existing_user:
            return render_template('signup.html', error="Username already taken")
        
        user = User(user_name=_username, pass_word=_psw)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    
    return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug=True)