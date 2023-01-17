# Import library

from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

# Create flask instance

app = Flask(__name__)
# Secret key
app.config['SECRET_KEY'] = 'VeryWiredK3y!'

# MySql db
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'socialmedia'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

# Register Form Class


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User register page
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s,%s,%s,%s)",
                    (name, email, username, password))
        mysql.connection.commit()
        cur.close()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))

    return render_template('registration.html', form=form)


# User login page


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()

        result = cur.execute(
            "SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dash'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Create dashboard


@app.route('/dash')
@is_logged_in
def dash():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('dash.html', posts=posts)
    else:
        msg = 'No Posts Found'
        return render_template('dash.html', msg=msg)

# Single post page
@app.route('/post/<string:id>/')
def post(id):

    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM posts WHERE id = %s", [id])
    post = cur.fetchone()

    return render_template('post.html', post=post)


class PostForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Add post function


@app.route('/add_post', methods=['GET', 'POST'])
@is_logged_in
def add_post():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO posts(title, body, author) VALUES(%s, %s, %s)",
                    (title, body, session['username']))
        mysql.connection.commit()
        cur.close()

        flash('Post Created', 'success')

        return redirect(url_for('dash'))

    return render_template('add_posts.html', form=form)


# Edit Post function
@app.route('/edit_post/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_post(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM posts WHERE id = %s", [id])
    post = cur.fetchone()
    cur.close()
    form = PostForm(request.form)
    form.title.data = post['title']
    form.body.data = post['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        cur = mysql.connection.cursor()
        app.logger.info(title)
        cur.execute("UPDATE posts SET title=%s, body=%s WHERE id=%s",
                    (title, body, id))
        mysql.connection.commit()
        cur.close()

        flash('Post Updated', 'success')

        return redirect(url_for('dash'))

    return render_template('edit_post.html', form=form)


# Delete post function
@app.route('/delete_post/<string:id>', methods=['POST'])
@is_logged_in
def delete_post(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM posts WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()

    flash('Post Deleted', 'success')

    return redirect(url_for('dash'))


# Users page
@app.route('/users')
def users():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('users.html', users=users)


#  Single user
@app.route('/user/<string:id>/')
def user(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users WHERE id = %s", [id])
    user = cur.fetchone()

    return render_template('user.html', user=user)


# Edit users 
@app.route('/edit_user/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_user(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users WHERE id = %s", [id])
    user = cur.fetchone()
    cur.close()
    form = RegisterForm(request.form)
    form.name.data = user['name']
    form.username.data = user['username']
    form.email.data = user['email']

    if request.method == 'POST' and 'name' in request.form and 'username' in request.form and 'email' in request.form:
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']

        cur = mysql.connection.cursor()
        app.logger.info(name)
        cur.execute("UPDATE users SET name=%s, username=%s, email=%s WHERE id=%s",
                    (name, username, email, (id)))
        mysql.connection.commit()
        cur.close()

        flash('User Updated', 'success')

        return redirect(url_for('users'))

    return render_template('edit_user.html', form=form)

# Delete user


@app.route('/delete_user/<string:id>', methods=['POST'])
@is_logged_in
def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()

    flash('User Deleted', 'success')

    return redirect(url_for('users'))

# Search post function

@app.route('/search_result', methods=["GET", "POST"])
def search_result():

    search = request.args.get("search")
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM posts WHERE title LIKE %s OR body LIKE %s", (search, search))
    mysql.connection.commit()
    posts = cur.fetchall()
    return render_template('search_result.html', posts=posts, search=search)


@app.route('/email')
def email():
    return render_template('email.html')


if __name__ == '__main__':
    app.run(debug=True)
