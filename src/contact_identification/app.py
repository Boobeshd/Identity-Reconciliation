from flask import Flask
from flask_restx import Api, Resource, fields
from datetime import datetime
import logging
from contact_handler import identify_contact

app = Flask(__name__)
api = Api(app, version='1.0', title='Contact Identification API', description='API to identify and consolidate contacts')

contact_model = api.model('Contact', {
    'email': fields.String(required=False, description='Email address'),
    'phoneNumber': fields.String(required=False, description='Phone number')
})

contact_response = api.model('ContactResponse', {
    'primaryContactId': fields.Integer(description='Primary contact ID'),
    'emails': fields.List(fields.String, description='List of emails'),
    'phoneNumbers': fields.List(fields.String, description='List of phone numbers'),
    'secondaryContactIds': fields.List(fields.Integer, description='List of secondary contact IDs')
})

@api.route('/identify')
class IdentifyContact(Resource):
    @api.expect(contact_model, validate=True)
    @api.response(200, 'Success', contact_response)
    def post(self):
        try:
            logging.info("api_executed")
            data = api.payload
            response = identify_contact(data)
            return response
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return {'message': 'Internal Server Error'}, 500