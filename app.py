from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://get-it-done:getitdone@localhost:3306/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "8FYqLBM0Fgs633*Xxas67!M2wIYGnQc9%h8" # needed for session (right now)

class Task(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id")) # one-to-many

    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner # the owner object not just the id, 
                           # for now, I am assuming it is the backref that fixes the setup

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    # set relationship, and allow to get all tasks via owner
    tasks = db.relationship("Task", backref="owner") 

    def __init__(self, email, password):
        self.email = email
        self.password = password

# @app.before_request
# def require_login():
#     allowed_routes = ["login", "register"]
#     # if ("email" not in session) and (request.endpoint not in allowed_routes):
#     if request.endpoint not in allowed_routes and 'email' not in session:
#         return redirect("/login")

@app.before_request
def require_login():
    allowed_routes = ["login", "register"] # these are names for methods and not request routes!
    if request.endpoint not in allowed_routes and "email" not in session:
        print(request.endpoint)
        return redirect("/login")

@app.route("/", methods=["POST", "GET"])
def index():
    # if we are here, the user is logged in
    # get the owner object grabbing user's email from session
    owner = User.query.filter_by(email=session["email"]).first()
    
    if request.method == "POST":
        task_name = request.form["task"]
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    # only want tasks that belong to current user
    tasks = Task.query.filter_by(completed=False, owner=owner).all()
    completed_tasks = Task.query.filter_by(completed=True, owner=owner).all()
    return render_template("todos.html", title="Get It Done!", 
        tasks=tasks, completed_tasks=completed_tasks, user=session["email"])


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first() # user return or None

        # if user exists and verified password
        if user and user.password == password:
            session["email"] = email
            flash("You are logged in!")
            return redirect("/")
        else:
            flash("Password is incorrect, or user does not exist", "error")

        return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        verify = request.form["verify"]
        # TODO: validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session["email"] = email
            flash("Welcome! You are registered and logged in!")
            return redirect("/")
        else:
            flash("Please try again.")
            # TODO: add exact error messages later

    return render_template("register.html")

@app.route("/logout")
def logout():
    del session["email"]
    flash("You are logged out!")
    return redirect("/")

@app.route("/delete-task", methods=["POST"])
def delete_task():
    task_id = int(request.form["task-id"])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect("/")
    
# keep for true delete
# @app.route("/delete-task", methods=["POST"])
# def delete_task():
#     task_id = int(request.form["task-id"])
#     task = Task.query.get(task_id)
#     db.session.delete(task)
#     db.session.commit()

#     return redirect("/")


if __name__ == "__main__":
    app.run()


    # TODO:
    # naming convention when spliting post and get request