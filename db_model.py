from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema,fields, ValidationError,pre_load
import logging ,enum
from marshmallow_enum import EnumField
from flask_user import login_required,UserManager,UserMixin,current_user

app = Flask(__name__, static_folder='web')
app.config['USER_APP_NAME'] = "Complaint Management System"
app.config['SECRET_KEY']='thisisasecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://jahnavi:chandaluri@localhost/cms'
app.config['CSRF_ENABLED'] = True
app.config['USER_ENABLE_EMAIL'] = False
db = SQLAlchemy(app)



logging.basicConfig(level=logging.INFO)

    
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50),unique=True,nullable=False)
    password = db.Column(db.String(255),server_default='',nullable=False)
    active = db.Column(db.Boolean(),server_default='0',nullable=False)
    # votes=db.relationship('Vote',secondary=user_vote,backref=db.backref('voters',lazy='dynamic'))
    votes= db.relationship('Vote', backref ='user', uselist=False)
    responses = db.relationship('Response', backref ='user', lazy=True, cascade="all, delete-orphan")
    complaints = db.relationship('Complaint', backref ='user', lazy=True, cascade="all, delete-orphan")

#db_adapter = SQLAlchemyAdapter(db,User)
user_manager = UserManager(app,db,User)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    name = db.Column(db.String(255) , unique=True)
    complaints = db.relationship('Complaint', backref ='category', lazy=True, cascade="all, delete-orphan")

class StatusEnum(enum.Enum):
    new = 1
    inProgress = 2
    resolved = 3
    rejected = 4
    

class Complaint(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    name = db.Column(db.String(255))
    description = db.Column(db.String(900))
    status = db.Column(db.Enum(StatusEnum),default=StatusEnum.new,nullable=False)
    votes= db.relationship('Vote', backref ='complaint', lazy='dynamic', cascade="all, delete-orphan")
    responses = db.relationship('Response', backref ='complaint', lazy=True, cascade="all, delete-orphan")
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    liked_count = db.Column(db.Integer);
    disliked_count = db.Column(db.Integer);

class Response(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    created_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    comment = db.Column(db.String(900))
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    
class Vote(db.Model):
    __table_args__ = (db.UniqueConstraint('user_id','complaint_id', name = 'user_complaint'),)
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    liked = db.Column(db.Boolean)
    user_id =db.Column(db.Integer,db.ForeignKey('user.id'))
    complaint_id = db.Column(db.Integer,db.ForeignKey('complaint.id'))
    
  
class UserSchema(Schema):
        id = fields.Integer()
        username = fields.String()
        #complaints = fields.List(fields.Nested(ComplaintSchema()))

class CategorySchema(Schema):
        id = fields.Integer()
        created_date = fields.Date()
        name = fields.String()
        #complaints = fields.List(fields.Nested(ComplaintSchema()))





class ResponseSchema(Schema):
        id = fields.Integer()
        created_date = fields.Date()
        comment = fields.String()
        complaint_id = fields.Integer()
        user = fields.Nested(UserSchema())

class VoteSchema(Schema):
        id = fields.Integer()
        created_date = fields.Date()
        liked = fields.Boolean()
        user = fields.Nested(UserSchema())
        complaint_id = fields.Integer()
        
class ComplaintSchema(Schema):
        id = fields.Integer()
        created_date = fields.Date()
        name = fields.String()
        description = fields.String()
        liked_count = fields.Integer()
        disliked_count = fields.Integer()
        category = fields.Nested(CategorySchema())
        user = fields.Nested(UserSchema())
        status = EnumField(StatusEnum)
        votes = fields.List(fields.Nested(VoteSchema()))
        responses = fields.List(fields.Nested(ResponseSchema()))



#Category.__table__.create(bind=db.engine,checkfirst=True)
#Complaint.__table__.create(bind=db.engine,checkfirst=True)
#Response.__table__.create(bind=db.engine,checkfirst=True)
#User.__table__.create(bind=db.engine,checkfirst=True)
#Vote.__table__.create(bind=db.engine,checkfirst=True)
#Subs.__table__.create(bind=db.engine,checkfirst=True)
db.create_all()



#testing database entries
user1 = User(username='user1', password='Password1')
user2 = User(username='user2', password='Password2')
db.session.add(user1)
db.session.add(user2)
db.session.commit()

cat1=Category(name='Hostel')
cat2=Category(name='Canteen')
db.session.add(cat1)
db.session.add(cat2)
db.session.commit()

c1 = Complaint(
    name='Maintenance',
    description='The bathrooms are not haveing soap dispencers',
    user_id=1,
    category_id=1,
    status=StatusEnum.new)
c2 = Complaint(
    name='Insufficient furniture',
    description='There is insufficient tables and chairs during the rush hours',
    user_id=1,
    category_id=2
    )
db.session.add(c1)
db.session.add(c2)
db.session.commit()


r1 = Response(comment='we have placed an order for soap dispencers and it will arrive in a time span of two weeks' ,complaint=c1,user=user2)
r2 = Response(comment='we have taked with higher officials and are planning for an expansion' ,complaint=c1,user_id=2)
db.session.add(r1)
db.session.add(r2)
db.session.commit()

v1 = Vote(user = user1,complaint=c1,liked=True)
v2 = Vote(user = user1, complaint = c2 ,liked=False)
v3 =Vote(user=user2,complaint=c1,liked=True)
db.session.add(v1)
db.session.add(v2)
db.session.add(v3)
db.session.commit()

complaints = Complaint.query.all()
for complaint in complaints:
    print (
    'subject', complaint.name, 
    'description',complaint.description,
    'categoryName',complaint.category.name,
    'submittedBy',complaint.user.username
    )
    liked_count = Vote.query.filter_by(complaint_id = complaint.id).filter_by( liked = 1).count()
    disliked_count = Vote.query.filter_by(complaint_id = complaint.id).filter_by( liked = 0).count()
    print('likedCount',liked_count)
    print('dislikedCount',disliked_count)
    responses = complaint.responses
    print ('printing response attributes')
    for res in responses:
        print ('description',res.comment,
        'submittedBy',res.user.username)



#for c in complaints:
    
