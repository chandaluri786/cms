from flask import Flask , render_template
from db_model import Complaint,Response,Category,db,app
#app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/home")
def home():
    user = { 'username': 'jahnavi'}
    complaints = Complaint.query.all()
    for complaint in complaints:
        print(complaint.subject)
    return render_template('index.html', title='Home', user=user, complaints=complaints)