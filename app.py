from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://get-it-done:getitdone@localhost:3306/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        task = request.form["task"]
        tasks.append(task)

    return render_template("todos.html", title="Get It Done!", tasks=tasks)

if __name__ == "__main__":
    app.run()