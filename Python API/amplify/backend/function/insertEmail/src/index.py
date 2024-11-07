import json
import os
from functools import wraps
from requests import HTTPError
from http import HTTPStatus
import boto3
from botocore.exceptions import ClientError
import uuid
import datetime
import hashlib

TABLE_NAME = os.environ.get('STORAGE_USERS_NAME', 'users')
boto3.setup_default_session(region_name='eu-west-1')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def generate_token(email: str, user_id: str) -> str:
    """Genère token grace a email & user_id"""
    combined = f"{email}:{user_id}".encode('utf-8')
    return hashlib.sha256(combined).hexdigest()

def exception_handler(func):
    @wraps(func)
    def wrapper(event, context):
        print(f"insersiont avec l'email {event['body']['email']} \n")
        response = {}
        
        try:
            if 'x-api-key' not in event.get('headers', {}):
                raise PermissionError('x-api-key absant')

            result = func(event, context)
            response['statusCode'] = HTTPStatus.OK
            response['body'] = json.dumps(result)

        except HTTPError as error:
            response['statusCode'] = error.response.status_code
            response['body'] = json.dumps({'error': error.response.json()})
        except PermissionError as error:
            response['statusCode'] = HTTPStatus.FORBIDDEN
            response['body'] = json.dumps({'error': str(error)})
        except ValueError as error:
            response['statusCode'] = HTTPStatus.BAD_REQUEST
            response['body'] = json.dumps({'error': str(error)})
        except Exception as error:
            print(f"Unexpected error: {str(error)}")
            response['statusCode'] = HTTPStatus.INTERNAL_SERVER_ERROR
            response['body'] = json.dumps({'error': 'Internal server error'})
            
        return response
    return wrapper

@exception_handler
def insert_email(event, context):
    """Creer User avec Email"""
    if not event.get('body') or 'email' not in event['body']:
        raise ValueError('email manquant dans requete')

    email = event['body']['email']

    try:
        existing_users = table.query(
            IndexName='emails',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={
                ':email': email
            }
        )

        if existing_users.get('Items'):
            user = existing_users['Items'][0]
            if 'token' not in user:
                token = generate_token(email, user['id'])
                table.update_item(
                    Key={'id': user['id']},
                    UpdateExpression='SET #token = :token',
                    ExpressionAttributeNames={'#token': 'token'},
                    ExpressionAttributeValues={':token': token}
                )
                return {'token': token, 'id': user['id']}
            return {'token': user['token'], 'id': user['id']}

        user_id = str(uuid.uuid4())
        token = generate_token(email, user_id)
        
        item = {
            'id': user_id,
            'email': email,
            'token': token,
            'created_at': datetime.datetime.now().isoformat()
        }

        table.put_item(Item=item)
        return {'token': token, 'id': user_id}

    except ClientError as e:
        print(f"DynamoDB Error: {str(e)}")
        raise

def handler(event, context):
    return insert_email(event, context)