from marshmallow import Schema, fields, pre_load
from marshmallow import validate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

class AddUpdateDelete():
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()

kinship = db.Table('kinship',
    db.Column('parent_id', db.Integer, db.ForeignKey('person.id')),
    db.Column('child_id', db.Integer, db.ForeignKey('person.id')),
    db.PrimaryKeyConstraint('parent_id', 'child_id'))

class Person(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    dateOfBirth = db.Column(db.Date, nullable=True)
    dateOfDeath = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(1), nullable=False)    
    children = db.relationship('Person', secondary=kinship,
        primaryjoin=(kinship.c.child_id == id),
        secondaryjoin=(kinship.c.parent_id == id), 
        backref=db.backref('parents', lazy='dynamic'), lazy='dynamic')

    @property
    def marriages(self):
        result = []
        for b in self.brides:
            result.append(b)
        for g in self.grooms:
            result.append(g)
        return result

    def __init__(self, firstName, lastName, dateOfBirth, dateOfDeath, gender):
        self.firstName = firstName
        self.lastName = lastName
        self.dateOfBirth = dateOfBirth
        self.dateOfDeath = dateOfDeath
        self.gender = gender
        self.parents = []

class PersonSchema(ma.Schema):
    id = fields.Integer(required=False)
    firstName = fields.String(required=True)
    lastName = fields.String(required=True)
    dateOfBirth = fields.Date(allow_none=True)
    dateOfDeath = fields.Date(allow_none=True)
    gender = fields.String(required=True, validate=validate.Length(1, 1))
    children = fields.Nested('NestedPersonSchema', many=True)
    parents = fields.Nested('NestedPersonSchema', many=True)  
    marriages = fields.Nested('MarriageSchema', many=True)
    url = ma.URLFor('api.personresource', id='<id>', _external=True)

class NestedPersonSchema(ma.Schema):
    id = fields.Integer(required=True)
    firstName = fields.String(required=True)
    lastName = fields.String(required=True)
    dateOfBirth = fields.Date(allow_none=True)
    dateOfDeath = fields.Date(allow_none=True)
    gender = fields.String(required=True, validate=validate.Length(1, 1))
    url = ma.URLFor('api.personresource', id='<id>', _external=True)

class Marriage(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    bride_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    groom_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    bride = db.relationship('Person', foreign_keys=[bride_id], backref=db.backref('grooms', lazy='dynamic'))
    groom = db.relationship('Person', foreign_keys=[groom_id], backref=db.backref('brides', lazy='dynamic'))
    dateOfWedding = db.Column(db.Date, nullable=False)    

    def __init__(self, bride, groom, dateOfWedding):
        self.bride = bride
        self.groom = groom
        self.dateOfWedding = dateOfWedding

class MarriageSchema(ma.Schema):
    bride = fields.Nested('NestedPersonSchema', only=('id', 'firstName', 'lastName', 'dateOfBirth', 'dateOfDeath', 'gender'))
    groom = fields.Nested('NestedPersonSchema', only=('id', 'firstName', 'lastName', 'dateOfBirth', 'dateOfDeath', 'gender'))
    dateOfWedding = fields.String()   #tried to use fields.Date but was getting error 'value' can't be formatted as Date 