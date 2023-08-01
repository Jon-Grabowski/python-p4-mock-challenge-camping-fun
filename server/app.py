#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):

    def get(self):
        campers = [c.to_dict(rules = ('-signups', )) for c in Camper.query.all()]
        return make_response(campers, 200)
    
    def post(self):
        data = request.json

        try:
            new_camper = Camper(
                name = data['name'],
                age = data['age']
            )
        except Exception as e:
            return make_response({ "errors": [str(e)] }, 422)
        
        db.session.add(new_camper)
        db.session.commit()

        return make_response(new_camper.to_dict(rules = ('-signups', )), 201)
    
api.add_resource(Campers, '/campers')

class CampersById(Resource):

    def get(self, id):
        camper = Camper.query.filter_by(id = id).first().to_dict()
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        return make_response(camper, 200)
    
    def patch(self, id):
        camper = Camper.query.filter_by(id = id).first()
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        

        data = request.json
        try:
            for attr in data:
                setattr(camper, attr, data[attr])
        except Exception as e_value:
            return make_response({"errors": [str(e_value)]}, 422)
        
        db.session.commit()
        return make_response(camper.to_dict(rules = ('-signups', )), 200)

api.add_resource(CampersById, '/campers/<int:id>')

class Activities(Resource):

    def get(self):
        return make_response([a.to_dict(rules = ('-signups', )) for a in Activity.query.all()], 200)

api.add_resource(Activities, '/activities')

class ActivitiesById(Resource):
    
    def delete(self, id):
        activity = Activity.query.filter_by(id = id).first()
        if not activity:
            return make_response({"error": "Activity not found"}, 404)
        
        db.session.delete(activity)
        db.session.commit()

        return make_response({}, 200)

api.add_resource(ActivitiesById, '/activities/<int:id>')

class Signups(Resource):

    def post(self):
        data = request.json
        try:
            new_signup = Signup(
                camper_id = data['camper_id'],
                activity_id = data['activity_id'],
                time = data['time']
            )
        except Exception as e:
            return make_response({"errors": [str(e)]}, 422)
        
        db.session.add(new_signup)
        db.session.commit()

        return make_response(new_signup.to_dict(), 200)

api.add_resource(Signups, '/signups')
if __name__ == '__main__':
    app.run(port=5555, debug=True)
