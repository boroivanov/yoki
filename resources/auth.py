import os

from botocore.exceptions import ClientError
from flask_restful import Resource, reqparse
from warrant import Cognito


class Auth(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help='Username cannot be blank.')
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help='Password cannot be blank.')

    def post(self):
        data = self.parser.parse_args()
        u = Cognito(os.environ['COGNITO_USERPOOL_ID'],
                    os.environ['COGNITO_APP_CLIENT_ID'],
                    username=data['username'])
        try:
            u.authenticate(password=data['password'])
        except ClientError as e:
            return {'message': str(e)}
        return {'access_token': u.id_token}
