from flask import request, jsonify, json, make_response, Response
from flask_restful import Resource
from ..models import db, Person, PersonSchema, Marriage, MarriageSchema
from sqlalchemy.exc import SQLAlchemyError
from .status import *
from ..helpers import PaginationHelper

marriage_schema = MarriageSchema()

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