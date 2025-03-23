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


# Model representing the published posts table
class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    subtitle = db.Column(db.Text, nullable=True)
    author = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False, default="General")  # New category field
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Model representing the pending posts table
class Pending_Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    subtitle = db.Column(db.Text, nullable=True)
    author = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False, default="General")  # New category field
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Model representing the contacts table
class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    phone_num = db.Column(db.Text, nullable=False)
    mes = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Model representing User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.Text, nullable=False)
    pass_word = db.Column(db.Text, nullable=False)


# Create tables
with app.app_context():
    db.create_all()

# Index Page Route
@app.route('/')
def home():
    category_filter= request.args.get('category','all')
    if category_filter=='all':
        _posts = Post.query.limit(params['no_of_posts']).all()  # Fetch a limited number of posts as defined in params
    else: 
        _posts=Post.query.filter_by(category=category_filter).limit(params['no_of_posts']).all()
    return render_template('index.html', posts=_posts, params=params,selected_category=category_filter)

# About Page Route
@app.route('/about')
def about():
    return render_template('about.html', params=params)


# Contact Page Route
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        entry = Contact(name=name, phone_num=phone, mes=message, email=email)
        db.session.add(entry)
        db.session.commit()
    
    return render_template('contact.html', params=params)

# Route to display a post based on its slug
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first() # Fetch the post with the given slug

    if not post:
        return "Post not found", 404
    
    return render_template('post.html', post=post, params=params)


# Dashboard Page Route
@app.route("/dashboard")
def dashboard():
    # Check if the user is logged in and is the admin
    if 'user' in session and session['user'] == params['admin_username']:
        action = request.args.get('action')  # Retrieve action parameter from URL
        sno = request.args.get('sno', type=int)  # Retrieve post serial number (sno) and convert to int
        username = request.args.get('username')  # Retrieve username from URL parameters

        # Render the pending posts page (Triggered from dashboard.html)
        if action == "render_pending_post":  
            _pending_posts = Pending_Post.query.all()
            return render_template('pending_posts.html', params=params, posts=_pending_posts)
        
        # Approve a pending post and move it to the main posts table (Triggered from pending_posts.html)
        elif action == "approve_post" and sno is not None:  
            post = Pending_Post.query.filter_by(sno=sno).first()  # Find the post in Pending_Post table
            if post:
                approved_post = Post(
                    title=post.title, subtitle=post.subtitle, author=post.author,
                    slug=post.slug, content=post.content, category=post.category, date=post.date
                )
                db.session.add(approved_post)
                db.session.delete(post)  # Remove post from the Pending_Post table
                db.session.commit()
                return redirect('/dashboard')  # Redirect back to the dashboard
        
        # Render the user management page (Triggered from dashboard.html)
        elif action == "render_manage_users":  
            users = User.query.all()
            return render_template('users.html', params=params, users=users)
        
        # Remove a user from the database (Triggered from users.html)
        elif action == "remove_user":  
            user_ = User.query.filter_by(user_name=username).first()
            if user_:
                db.session.delete(user_)
                db.session.commit()
                return redirect('/dashboard')
        
        # Default: Render the dashboard with all approved posts
        # (Accessed by default or after an action from various pages)
        _posts = Post.query.all()
        response = make_response(render_template('dashboard.html', params=params, posts=_posts))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response
    
    else:
        return redirect('/')  # Redirect to the home page if the user is not authorized

# Edit Post Route
@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session:
        user = User.query.filter_by(user_name=session['user']).first()  # Retrieve logged-in user details

        if request.method == 'POST':
            _title = request.form.get('title')
            _subtitle = request.form.get('subtitle')
            _author = "Admin" if session['user'] == params['admin_username'] else user.user_name
            _slug = request.form.get('slug')
            _content = request.form.get('content')
            _date = datetime.now(timezone.utc)
            _category = request.form.get('category')  # Retrieve selected category

            # Admin or user adding a new post (Triggered from edit.html with sno='0')
            if sno == '0':
                if session['user'] == params['admin_username']:  # Admin adding a new post
                    post = Post(
                        title=_title, subtitle=_subtitle, author=_author,
                        slug=_slug, content=_content,category=_category, date=_date
                    )
                    db.session.add(post)
                    db.session.commit()
                    return redirect('/dashboard')  # Redirect to dashboard after posting
                
                else:  # Regular user submitting a new post (Goes to pending review)
                    post = Pending_Post(
                        title=_title, subtitle=_subtitle, author=_author,
                        slug=_slug, content=_content,category=_category, date=_date
                    )
                    db.session.add(post)
                    db.session.commit()
                    session.pop('user')  # Log the user out after submission
                    return redirect('/')  # Redirect to home page

            # Editing an existing post (Triggered from edit.html with valid sno)
            else:
                post = Post.query.filter_by(sno=sno).first()
                if post.author == params['admin_username']:  # Admin editing their own post
                    post.title = _title
                    post.subtitle = _subtitle
                    post.slug = _slug
                    post.content = _content
                    post.category=_category
                    post.date = _date
                    db.session.add(post)
                    db.session.commit()
                    return redirect('/dashboard')  # Redirect back to dashboard
                
                else:  # Admin cannot edit posts created by regular users
                    return render_template_string("""
                        <h1>Error</h1>
                        <p>Admin does not have permission to edit other posts.</p>
                    """)

        # Render the edit post page (Triggered from dashboard.html or edit.html)
        _post = Post.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=_post, sno=sno)


# Route to delete a post (either pending or published)
@app.route("/delete")
def delete():
    # Ensure only the admin can delete
    if 'user' in session and session['user']==params['admin_username']:
        action = request.args.get('action')  # Get action from URL
        sno = request.args.get('sno', type=int)  # Get sno and convert to int

        if action == "delete_pending_post": # Deleting a pending post (Triggered from pending_posts.html)
            _post = Pending_Post.query.filter_by(sno=sno).first()  # Fetch the specific pending post
            db.session.delete(_post)
            db.session.commit()
        elif action == "delete_post": # Deleting a published post (Triggered from dashboard.html)
            _post = Post.query.filter_by(sno=sno).first()  # Fetch the specific published post
            db.session.delete(_post)
            db.session.commit()
        
        return redirect('/dashboard')

# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Route for user and admin login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Admin login check
        if username == params['admin_username'] and password == params['admin_password']:
            session['user'] = params['admin_username']  # Store admin session
            return redirect('/dashboard')  # Redirect admin to dashboard
        
        else:
            # Check if user exists in the database
            user = User.query.filter_by(user_name=username, pass_word=password).first()
            if user:  # If valid user credentials, log in the user
                session['user'] = user.user_name
                return redirect('/edit/0')  # Redirect user to create a new post
            else:
                return render_template('login.html', params=params, error="Invalid credentials")
    
    # Render login page with cache disabled to prevent storing sensitive login data
    response = make_response(render_template('login.html', params=params))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response


# Route for user registration (Sign-Up)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        _username = request.form.get('username')
        _psw = request.form.get('psw')

        # Check if the username is already taken
        existing_user = User.query.filter_by(user_name=_username).first()
        if existing_user:
            return render_template('signup.html', error="Username already taken")
        
        # Create a new user and add to database
        user = User(user_name=_username, pass_word=_psw)
        db.session.add(user)
        db.session.commit()
        
        return redirect('/login')  # Redirect to login page after successful sign-up
    
    return render_template('signup.html')  # Render sign-up page for GET request


# Run App
if __name__ == "__main__":
    app.run(debug=True)

