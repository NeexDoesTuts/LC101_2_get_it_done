- [Notes from learning to build this app:](#notes-from-learning-to-build-this-app)
- [Object Rational Mapping](#object-rational-mapping)
    - [Database setup](#database-setup)
        - [The connection string](#the-connection-string)
        - [Common DB Errors](#common-db-errors)
    - [Connect db with flask application](#connect-db-with-flask-application)
        - [Create persistent classes (Task model)](#create-persistent-classes-task-model)
    - [Add db information in python shell](#add-db-information-in-python-shell)
    - [Get data from the database](#get-data-from-the-database)
    - [Save data to database via Flask](#save-data-to-database-via-flask)
    - [Delete database data via Flask](#delete-database-data-via-flask)
        - [Delete data via True/False flags](#delete-data-via-true-false-flags)
    - [User model](#user-model)
        - [Remember logged user - implement session object](#remember-logged-user-implement-session-object)


# Notes from learning to build this app:
# Object Rational Mapping

## Database setup

1. Create a database and user for the project via. phpMyAdmin.
   * create user and auto-create database on localhost
   * check what is the PORT the server is running on (in bitnami settings)
2. Install dependencies.
   * the ORM => sqlalchemy (installed automagically with flask-sqlalchemy)
   * the bridge between it and flask (flask-sqlalchemy)
   * mySQL driver to connect to databases (pymysql)

```bash
# conda create -n GTD flask
# source activate GTD
conda install -c conda-forge flask-sqlalchemy # it is not in the official conda repo so we use a different package channel/repository
conda install pymysql # driver
```

3. Add libraries in `app.py` to use SQL:

The `flask_sqlalchemy` module is a "**wrapper**" of SQLAlchemy that makes it work more seamlessly with Flask applications.

```python
from flask_sqlalchemy import SQLAlchemy
```

4. Add SQL `connection string` information to Flask app configuration:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:beproductive@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True 
```

The `app.config['SQLALCHEMY_ECHO'] = True ` will display aka. echo into the terminal all the SQLAlchemy chit-chat with the database.

### The connection string

| db type | +    | db driver | user        | :    | password  | @    | server    | :    | port number | /    | db name     |
| ------- | ---- | --------- | ----------- | ---- | --------- | ---- | --------- | ---- | ----------- | ---- | ----------- |
| mysql   | +    | pymysql   | get-it-done | :    | getitdone | @    | localhost | :    | 3306        | /    | get-it-done |

### Common DB Errors

1. The database is not running.
2. The connection string is not correct, especially port number, user and password.

## Connect db with flask application

Create a database connection and interface for our app. We'll use the `db` object throughout our app, and it will allow us to interact with the database via our Flask/Python code.

```python
db = SQLAlchemy(app)
```

### Create persistent classes (Task model)

Next we'll continue modifying `app.py` and create a persistent class for database data:

```python
class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name):
        self.name = name
```

By extending `Model` class, we'll get a lot of functionality that will allow our class to be managed by SQLAlchemy, and thus stored in the database. We call a class like this a **persistent class**.

## Add db information in python shell

1. Start-up Python Shell (from within the app directory):

```bash
python
```

2. Create the database tables (inside python shell) and add basic data if you like:

```python
>>>
```

```python
from app import db, Task # gives us access to the database object and Task class
```

Create the database table and a few tasks (it is all in python terminal, but I am skipping the >>> indicators):

```python
# create table(s)
db.create_all()

# create tasks
new_task = Task("This is my task one")
second_task = Task("Hello there!")

# add to db session
db.session.add(new_task)
db.session.add(second_task)
# add all to database
db.session.commit()
```

Now the database has one table and 2 tasks in it:

![](db_with_tasks.png)

## Get data from the database

To get data from database (still in python shell), run the following:

```python
tasks = Task.query.all() # get a list of task objects
tasks[0].name # get 1st task's name property 
```
Get data from database in the Flask app:

add this in the handler:

```python
 tasks = Task.query.all()
```

```python
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        task = request.form["task"]
        tasks.append(task)

    tasks = Task.query.all() # !!!

    return render_template("todos.html", title="Get It Done!", tasks=tasks)
```

and change inner `task` to `task.name` in template:

```jinja2
<ul>
    {% for task in tasks %}
    <li>{{task.name}}</li>
    {% endfor %}
</ul>
```

We have to access the name property.

## Save data to database via Flask

Update handler to save new tasks to the database:

```python
@app.route("/", methods=["POST", "GET"])
def index():
    
    if request.method == "POST":
        task_name = request.form["task"]
        new_task = Task(task_name)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.all()
    return render_template("todos.html", title="Get It Done!", tasks=tasks)
```

## Delete database data via Flask

This is the actual deleting from database, which is probably not the best way to handle it (look down for flag deletion).

1. Add a form under the `<li>` in `todos.html` to make a `POST` request:

```jinja2
 <ul>
    {% for task in tasks %}
    <li>{{task.name}}</li>
    <form action="/delete-task" method="POST" style="display:inline-block;">
        <input type="hidden" name="task-id" value="{{task.id}}" />
        <input type="submit" value="Done!" />
 	</form>
    {% endfor %}
</ul>
```

* add form to delete task, to each task
* add hidden input for some value (id) that let's us recognize which task we are talking about, and delete it from the database

2. Make a new request handler for `/delete-task` route:

```python
@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()

    return redirect('/')
```

### Delete data via True/False flags

We have to add another column to our database. because we are in dev environment (and because we are just learning) we will drop the tables, and recreate them with new column. To change table for data after it contains data, one will need migration tools not covered at this point (look:=> [flask-Migrate](https://flask-migrate.readthedocs.io/))

```python
db.create_all() # only creates new, does not update
```

Destroy and redo tables:

```python
db.drop_all()
db.create_all()
```

Change the handler code by adding new property and "adding" (as updating) task in database:

```python
@app.route("/delete-task", methods=["POST"])
def delete_task():
    task_id = int(request.form["task-id"])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect("/")
```

Now the database works as expected:

![](db_delete_with_flag.png)

But the view does not work as expected. We still just show all tasks. And we have to filter only task with `completed=False`. To do this, in index handler split tasks to show completed and not yet completed separately:

```python
(...)
tasks = Task.query.filter_by(completed=False).all()
completed_tasks = Task.query.filter_by(completed=True).all()
return render_template("todos.html", title="Get It Done!", 
    tasks=tasks, completed_tasks=completed_tasks)
```

The completed tasks will work the same in template, and to show completed, we can use the new passed variable:

```jinja2
<hr />
<h2>Completed</h2>
<ul>
    {% for task in completed_tasks %}
    <li>{{task.name}}</li>
    {% endfor %}
</ul>
```

## User model

Create templates and routes for GET request for login and registration of the user. Create User class model:

```python
class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True) # must be unique
    password = db.Column(db.String(120)) # password is just plain text for now

    def __init__(self, email, password):
        self.email = email
        self.password = password
```

Add to database via python shell as usual.

Registration and login is pretty similar to the previous assignment. Here is the no-validation registration:

```python
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        verify = request.form["verify"]

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/")
        else:
            return "duplicate"
    
    return render_template("register.html")
```

This only checks if the user exists, and if not, creates one. 

### Remember logged user - implement session object

A session is an object (specifically, a dictionary) that can be used to store data that is associated with a specific user so that it is available for use across multiple requests. 

* Import session object from flask:

```python
from flask import Flask, request, redirect, render_template, session
```

* Add secret key:

```python
app.secret_key = "#someSecretString: 8FYqLBM0Fgs633*Xxas67!M2wIYGnQc9%h8"
```

* Save user email in session on register and login by implementing outside function which is not route-specific using the decorator `@app.before_request`. This allows us to do checks before handling incoming requests.:

```python
@app.before_request
def require_login():
    allowed_routes = ["login", "register"] # these are names for methods and not request routes!
    if request.endpoint not in allowed_routes and "email" not in session:
        print(request.endpoint)
        return redirect("/login")
```

* create a logout handler to delete session key:

```python
@app.route('/logout', methods=['GET'])
def logout():
    del session['email']
    return redirect('/')
```

* And finally we'll add a logout link to the body of our `base.html`:


```html
<div>
    <a href="./logout">log out</a>
</div>
```

