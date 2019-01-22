from datetime import datetime
from api import app
from api.models.user_model import User, UserServices
from api.validators.user_validator import UserValidator
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify, abort, request
import jwt

validator = UserValidator()
user_services = UserServices()


class UserController():
    '''
    Class to handle user related routes

    '''

    def register(self):
        '''
        Function to register a user
        '''
        data = request.get_json()

        if not validator.has_required_fields(data):
            abort(400)

        errors = validator.get_password_errors(data)
        if len(errors) > 0:
            return jsonify({'status': 400, 'data': errors}), 400

        if validator.duplicate_email(data['email']):
            abort(409)

        hashed_password = generate_password_hash(
            data['password'], method='sha256')

        data['date_registered'] = dteRegistered = datetime.utcnow().date()
        data['password'] = hashed_password
        data['is_admin'] = False

        new_user = User(**data)

        user = user_services.add_user(new_user)

        success_response = {'user': user, 'token': 'User created'}
        return jsonify({'status': 201, 'data': [success_response]}), 201

    def login(self):
        '''
        Function to login a user
        The user must be registered
        The function returns a json web token


        '''
        data = request.get_json()
        if not validator.has_login_required_fields(data):
            abort(400)

        user = user_services.get_user_by_email(data['email'])
        if not user:
            abort(401)

        token = jwt.encode({'id': user['id']}, app.config['SECRET_KEY'],
                           algorithm='HS256')

        if check_password_hash(user['password'], data['password']):
            access_token = token
            success_response = {'user': user,
                                'token': access_token.decode("utf-8")}
            return jsonify({'status': 200, 'data': [success_response]}), 200
        abort(401)

