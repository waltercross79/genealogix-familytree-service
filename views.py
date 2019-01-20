from flask import Blueprint, request, jsonify, json, make_response, Response
from flask_restful import Api, Resource
from models import db, Person, PersonSchema, Marriage, MarriageSchema
from sqlalchemy.exc import SQLAlchemyError
import status
from helpers import PaginationHelper

api_bp = Blueprint('api', __name__)
person_schema = PersonSchema()
marriage_schema = MarriageSchema()
api = Api(api_bp)

class PersonResource(Resource):
    def get(self, id):
        person = Person.query.get_or_404(id)
        result = person_schema.dump(person).data
        return result

    def patch(self, id):
        person = Person.query.get_or_404(id)
        person_dict = request.get_json(force=True)
        if 'firstName' in person_dict:
            person.firstName = person_dict['firstName']
        if 'lastName' in person_dict:
            person.lastName = person_dict['lastName']
        if 'dateOfBirth' in person_dict:
            person.dateOfBirth = person_dict['dateOfBirth']
        if 'dateOfDeath' in person_dict:
            person.dateOfDeath = person_dict['dateOfDeath']
        if 'gender' in person_dict:
            person.gender = person_dict['gender']
        if 'parents' in person_dict:
            if person_dict['parents'] != None:
                # delete existing parents
                for p in person.parents:
                    person.parents.remove(p)
                # add parents from incoming list
                for p in person_dict['parents']:                    
                    parent = Person.query.filter_by(id=p['id']).first()
                    person.parents.append(parent)       
        
        dumped_person, dump_errors = person_schema.dump(person)
        if dump_errors:
            return dump_errors, status.HTTP_400_BAD_REQUEST
        
        validate_errors = person_schema.validate(dumped_person)
        if validate_errors:
            return validate_errors, status.HTTP_400_BAD_REQUEST

        try:
            person.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_400_BAD_REQUEST

    def delete(self, id):
        person = Person.query.get_or_404(id)
        try:
            person.delete(person)
            response = make_response()
            return response, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_401_UNAUTHORIZED

class PersonListResource(Resource):
    def get(self):
        pagination_helper = PaginationHelper(
            request, 
            query=Person.query,
            resource_for_url='api.personlistresource',
            key_name='results',
            schema=person_schema)
        
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        person_dict = request.get_json()
        if not person_dict:
            response = {"message": "No input data provided"}
            return response, status.HTTP_400_BAD_REQUEST
        
        errors = person_schema.validate(person_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        
        try:            
            person = Person(
                firstName=person_dict['firstName'],
                lastName=person_dict['lastName'],
                dateOfBirth=person_dict['dateOfBirth'], 
                dateOfDeath=None,               
                gender=person_dict['gender']
            )
            if 'dateOfDeath' in person_dict:
                person.dateOfDeath=person_dict['dateOfDeath']
            
            person.add(person)
            query = Person.query.get(person.id)
            result = person_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            message = json.dumps({"error": str(e)})
            return Response(message, status=status.HTTP_400_BAD_REQUEST, mimetype='application/json')

class MarriageListResource(Resource):
    def get(self):
        pagination_helper = PaginationHelper(
            request, 
            query=Marriage.query,
            resource_for_url='api.marriagelistresource',
            key_name='results',
            schema=marriage_schema)
        
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        marriage_dict = request.get_json()
        if not marriage_dict:
            response = {"message": "No input data provided"}
            return response, status.HTTP_400_BAD_REQUEST
        
        errors = marriage_schema.validate(marriage_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        
        try:            
            bride = Person.query.get_or_404(marriage_dict['bride_id'])
            groom = Person.query.get_or_404(marriage_dict['groom_id'])
            weddingDate = marriage_dict['dateOfWedding']

            marriage = Marriage(
                bride=bride,
                groom=groom,
                dateOfWedding=weddingDate)            

            marriage.update()
                        
            query = Marriage.query.get(marriage.id)

            result = marriage_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            message = json.dumps({"error": str(e)})
            return Response(message, status=status.HTTP_400_BAD_REQUEST, mimetype='application/json')

api.add_resource(PersonListResource, '/persons/')
api.add_resource(PersonResource, '/persons/<int:id>')
api.add_resource(MarriageListResource, '/marriages/')