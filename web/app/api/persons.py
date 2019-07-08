from flask import request, jsonify, json, make_response, Response
from flask_restful import Resource
from ..models import db, Person, PersonSchema, Marriage, MarriageSchema
from sqlalchemy.exc import SQLAlchemyError
from .status import *
from ..helpers import PaginationHelper
from dateutil import parser

person_schema = PersonSchema()

class PersonResource(Resource):
    def get(self, id):
        person = Person.query.get_or_404(id)
        result = person_schema.dump(person).data
        return result

    def patch(self, id):
        person = Person.query.get_or_404(id)
        person_dict = request.get_json()
            
        if 'firstName' in person_dict:
            person.firstName = person_dict['firstName']
        if 'lastName' in person_dict:
            person.lastName = person_dict['lastName']
        if 'dateOfBirth' in person_dict:
            if person_dict['dateOfBirth'] != None:
                person.dateOfBirth = parser.parse(person_dict['dateOfBirth'])
            else:
                person.dateOfBirth = None
        if 'dateOfDeath' in person_dict:
            if person_dict['dateOfDeath'] != None:
                person.dateOfDeath = parser.parse(person_dict['dateOfDeath'])
            else:
                person.dateOfDeath = None
        if 'gender' in person_dict:
            person.gender = person_dict['gender']
        if 'parents' in person_dict:
            if person_dict['parents'] != None:
                # get list of parent IDs greater than 0
                id_list = [p['id'] for p in person_dict['parents'] if p['id'] > 0]

                if len(id_list) > 0:
                    # delete existing parents
                    for p in person.parents:
                        person.parents.remove(p)
                    # add parents from incoming list
                    for i in id_list:  
                        parent = Person.query.filter_by(id=i).first()
                        person.parents.append(parent)       
            
        dumped_person, dump_errors = person_schema.dump(person)
        if dump_errors:
            return dump_errors, HTTP_400_BAD_REQUEST
        
        validate_errors = person_schema.validate(dumped_person)
        if validate_errors:
            return validate_errors, HTTP_400_BAD_REQUEST

        try:
            person.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, HTTP_400_BAD_REQUEST

    def delete(self, id):
        person = Person.query.get_or_404(id)
        try:
            person.delete(person)
            response = make_response()
            return response, HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, HTTP_401_UNAUTHORIZED

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
            return response, HTTP_400_BAD_REQUEST
        
        errors = person_schema.validate(person_dict)
        if errors:
            return errors, HTTP_400_BAD_REQUEST
        
        try:    
            dob = None    
            if 'dateOfBirth' in person_dict: 
                if person_dict['dateOfBirth'] != None:
                    dob = parser.parse(person_dict['dateOfBirth'])
            
            dod = None
            if 'dateOfDeath' in person_dict:
                if person_dict['dateOfDeath'] != None:
                    dob = parser.parse(person_dict['dateOfDeath'])

            person = Person(
                firstName=person_dict['firstName'],
                lastName=person_dict['lastName'],
                dateOfBirth=dob, 
                dateOfDeath=dod,               
                gender=person_dict['gender']
            )
            #if 'dateOfDeath' in person_dict:
            #    person.dateOfDeath=person_dict['dateOfDeath']
            
            person.add(person)
            query = Person.query.get(person.id)
            result = person_schema.dump(query).data
            return result, HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            message = json.dumps({"error": str(e)})
            return Response(message, status=HTTP_400_BAD_REQUEST, mimetype='application/json')
