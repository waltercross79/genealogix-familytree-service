from flask import Blueprint
from flask_restful import Api

bp = Blueprint('api', __name__)

from .persons import PersonListResource, PersonResource
from .marriages import MarriageListResource

api = Api(bp)

api.add_resource(PersonListResource, '/persons/')
api.add_resource(PersonResource, '/persons/<int:id>')
api.add_resource(MarriageListResource, '/marriages/')
