from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema,fields, ValidationError,pre_load
import logging 

app = Flask(__name__, static_folder='web')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://jahnavi:chandaluri@localhost/cms'
db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    name = db.Column(db.String(255) , unique=True)
    complaints = db.relationship('Complaint', backref ='category', lazy=True, cascade="all, delete-orphan")


class Complaint(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    subject = db.Column(db.String(255))
    description = db.Column(db.String(900))
    submitted_by = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    responses= db.relationship('Response', backref ='complaint', lazy=True, cascade="all, delete-orphan")
    
class ComplaintSchema(Schema):
        id = fields.Integer()
        created_date = fields.Date()
        subject = fields.String()
        description = fields.String()
        submitted_by = fields.String()
        category_id = fields.Integer()

class CategorySchema(Schema):
        id = fields.Integer()
        created_date = fields.Date()
        name = fields.String()
        complaints = fields.List(fields.Nested(ComplaintSchema()))


class Response(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    created_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    description = db.Column(db.String(900))
    submitted_by = db.Column(db.String(255))
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'))
    

Category.__table__.create(bind=db.engine,checkfirst=True)
Complaint.__table__.create(bind=db.engine,checkfirst=True)
Response.__table__.create(bind=db.engine,checkfirst=True)

cat_1 = Category(name = 'Canteen')
com_1 = Complaint(
    subject = 'in sufficient benches', 
    description ='not so enough benches during rush hour',
    category = cat_1)

db.session.add(cat_1)
db.session.commit()

cat_2 = Category(name = 'library')
com_2 = Complaint(
    subject = 'difficult to locate books', 
    description ='difficult to locate books',
    category = cat_2)

db.session.add(cat_2)
db.session.commit()
db.session.add(com_2)
db.session.commit()
test = Complaint.query.first()
print(test.subject)

#cat1=Category.query.filter_by(id=test.category_id).all()
#print(len(cat1))
#cat = Category.query.first()
#print(cat.complaints[0].subject)