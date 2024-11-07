import json
import os
from functools import wraps
from requests import HTTPError
from http import HTTPStatus
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get('STORAGE_USERS_NAME', 'users')
boto3.setup_default_session(region_name='eu-west-1')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def exception_handler(func):
    @wraps(func)
    def wrapper(event, context):
        print(f"recherche de user avec toekn : {event['body']['token']} \n")
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
def handler(event, context):
    """Recup mail avec le token"""
    if not event.get('body') or 'token' not in event['body']:
        raise ValueError('token manquant dans requete')
        
    token = event['body']['token']

    try:
        response = table.scan(
            FilterExpression='#token = :token',
            ExpressionAttributeNames={
                '#token': 'token'
            },
            ExpressionAttributeValues={
                ':token': token
            }
        )
        
        items = response.get('Items', [])
        if not items:
            raise ValueError('token invalide')
            
        user = items[0]
        return {
            'email': user['email']
        }
        
    except ClientError as e:
        print(f"DynamoDB Error: {str(e)}")
        raise