#Imports
from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
import requests
import json

#My App
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)


#Get the latest high and low prices for the items that we have data for,
# and the Unix timestamp when that transaction took place. 
# Map from itemId (see here for a reference) to an object of {high, highTime, low, lowTime}. 
# If we've never seen an item traded, it won't be in the response.
# If we've never seen an instant-buy price, then high and highTime will be null 
# (and similarly for low and lowTime if we've never seen an instant-sell). 
# 


#This model is meant to hold the data from /latest.
# That is, for each id: {high, highTime, low, lowTime}
class LatestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    high = db.Column(db.Integer)
    highTime = db.Column(db.DateTime)
    low = db.Column(db.Integer)
    lowTime = db.Column(db.DateTime)
    fetched_date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"Task {self.id}"

#Testing to verify I can get the output from the API and display it in my HTML
@app.route("/latest", methods=["GET"])
def latest():

    # Does it make sense to split this up like the other function below where we have an if/else to split GET/POST?
    #We should make separate functions - one that we can call easily just to get the latest data.
    #Another to take that data and store it.
    #We'll do that for all of the possible API's - write my own API to completely consume this one.
    #After that, we can build the app to actually use this API as we see fit.



    base_request_url = 'https://prices.runescape.wiki/api/v1/osrs'
    url = base_request_url + "/latest"

    headers = {
        'User-Agent': 'Learning to use the API - @Runesr4nerds on discord',
        'From': 'Runesr4nerds'
    }

    response = requests.get(url, headers=headers)

    #TODO: Read into LatestModel and store in the DB.

    data = response.json()
    #I have a dictionary, and we're turning it into a string with json.dumps()
    parsed = json.dumps(data)

    print(f"parsed: {parsed}")

    

    return render_template("latest.html", response=parsed)


# We're going to need to store our mapped data in the db so we know which items we're dealing with:
# https://oldschool.runescape.wiki/w/Module:GEIDs/data.json



















class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Integer, default=0)
    created_date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"Task {self.id}"

#Home Page
@app.route("/", methods=["POST", "GET"])
def index():
    #Add a task
    if request.method == "POST":
        current_task = request.form['content']
        new_task = MyTask(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"
    #See current tasks
    else:
        tasks = MyTask.query.order_by(MyTask.created_date).all()
        return render_template("index.html", tasks=tasks)


#Delete
@app.route("/delete/<int:id>")
def delete(id:int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"Error:{e}"

#Edit an item
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id:int):
    task = MyTask.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect("/")

        except Exception as e:
            return f"Error:{e}"
    else:
        return render_template('edit.html', task=task)

if __name__ in "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)


