from flask import Flask , render_template,request, jsonify
from flask_restful import Resource,Api
from flask_user import login_required,UserManager,UserMixin, current_user
from db_model import Complaint, ComplaintSchema, Response, Vote, Category, CategorySchema, db, app
#app = Flask(__name__)
api = Api(app)


@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/home")
#@login_required
def home():
    user = current_user
    complaints = Complaint.query.all()
    for complaint in complaints:
        print(complaint.name)
    return render_template('index.html', title='Home', user=user, complaints=complaints)


class CategoryList(Resource):
    def get(self):
        categories = Category.query.all()
        return {'category' : CategorySchema(many=True).dump(categories) }

    def post(self):
        name = request.json['name']
        category = Category(name = name)
        db.session.add(category)
        db.session.commit()
        return { 'category' : CategorySchema().dump(category) }

api.add_resource(CategoryList, '/api/category')

class CategoryItem(Resource):
    def get(self,id):
        category = Category.query.filter_by(id=id).first()
        return { 'category' : CategorySchema().dump(category) }
    def delete(self, id):
        category = Category.query.filter_by(id=id).first()
        db.session.delete(category)
        db.session.commit()
        return { 'category' : CategorySchema().dump(category) }
    
    def put(self, id):
        category = Category.query.filter_by(id=id).first()
        name = request.json['name']
        category.name = name
        db.session.commit()
        return { 'category' : CategorySchema().dump(category) }


        



api.add_resource(CategoryItem, '/api/category/<string:id>')

class ComplaintList(Resource):
    def get(self):
        complaints = Complaint.query.all()
        for complaint in complaints :
            liked_count = Vote.query.filter_by(complaint_id = complaint.id).filter_by( liked = 1).count()
            disliked_count = Vote.query.filter_by(complaint_id = complaint.id).filter_by( liked = 0).count()
            complaint.liked_count = liked_count
            complaint.disliked_count = disliked_count
  
        return { 'complaint' : ComplaintSchema(many=True).dump(complaints) }
    
    def post(self):
        subject = request.json['subject']
        description = request.json['description']
        category_id =request.json['category_id']
        submitted_by = request.json['submitted_by']
        complaint = Complaint(subject = subject,description = description, category_id = category_id,submitted_by = submitted_by)
        db.session.add(complaint)
        db.session.commit()
        return { 'complaint' : ComplaintSchema().dump(complaint) }


api.add_resource(ComplaintList, '/api/complaint')

class ComplaintItem(Resource):
    def get(self, id):
        complaint = Complaint.query.filter_by(id=id).first()
        return { 'complaint' : ComplaintSchema().dump(complaint) }
    
    def delete(self, id):
        complaint = Complaint.query.filter_by(id=id).first()
        db.session.delete(complaint)
        db.session.commit()
        return { 'complaint' : ComplaintSchema().dump(complaint) }
    
    def put(self, id):
        complaint = Complaint.query.filter_by(id=id).first()
        subject = request.json['subject']
        complaint.subject = subject
        db.session.commit()
        return { 'complaint' : ComplaintSchema().dump(complaint) }
    
    
    


api.add_resource(ComplaintItem, '/api/complaint/<string:id>')

