# import json
# import boto3
# import os
# import uuid
# import logging

# # Set up logging
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

# # Initialize AWS clients and resources
# dynamodb = boto3.resource('dynamodb')
# survey_table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])
# answers_table = dynamodb.Table(os.environ['ANSWERS_TABLE_NAME'])
# sns_client = boto3.client('sns')

# def handler(event, context):
#     logger.info('Event: %s', json.dumps(event))
#     method = event.get('httpMethod')
#     path = event.get('path')
    
#     try:
#         if path == '/survey' and method == 'POST':
#             return create_survey(event)
#         elif path == '/survey' and method == 'GET':
#             return get_survey(event)
#         elif path == '/survey' and method == 'PUT':
#             return update_survey(event)
#         elif path == '/survey' and method == 'DELETE':
#             return delete_survey(event)
#         elif path == '/survey/answer' and method == 'POST':
#             return answer_survey(event)
#         else:
#             return {
#                 'statusCode': 405,
#                 'body': json.dumps('Method Not Allowed')
#             }
#     except Exception as e:
#         logger.error('Error: %s', str(e))
#         return {
#             'statusCode': 500,
#             'body': json.dumps(f'Internal Server Error: {str(e)}')
#         }


# def create_survey(event):
#     try:
#         data = json.loads(event['body'])
#         logger.info('Creating survey with data: %s', json.dumps(data))
#         survey_id = str(uuid.uuid4())
#         survey = {
#             'survey_id': survey_id,
#             'title': data['title'],
#             'description': data['description'],
#             'questions': data['questions']
#         }
#         survey_table.put_item(Item=survey)
#         send_notification("New Survey Created", f"A new survey titled '{data['title']}' has been created.")
#         return {
#             'statusCode': 201,
#             'body': json.dumps({'survey_id': survey_id})
#         }
#     except Exception as e:
#         logger.error('Error in create_survey: %s', str(e))
#         return {
#             'statusCode': 500,
#             'body': json.dumps(f'Internal Server Error: {str(e)}')
#         }

# def get_survey(event):
#     try:
#         survey_id = event['queryStringParameters']['survey_id']
#         logger.info('Fetching survey with ID: %s', survey_id)
#         response = survey_table.get_item(Key={'survey_id': survey_id})
#         item = response.get('Item')
#         if item:
#             return {
#                 'statusCode': 200,
#                 'body': json.dumps(item)
#             }
#         else:
#             return {
#                 'statusCode': 404,
#                 'body': json.dumps('Survey not found')
#             }
#     except Exception as e:
#         logger.error('Error in get_survey: %s', str(e))
#         return {
#             'statusCode': 500,
#             'body': json.dumps(f'Internal Server Error: {str(e)}')
#         }

# def update_survey(event):
#     try:
#         data = json.loads(event['body'])
#         logger.info('Updating survey with data: %s', json.dumps(data))
#         survey_id = data['survey_id']
#         update_expression = "SET title = :title, description = :description, questions = :questions"
#         expression_attribute_values = {
#             ':title': data['title'],
#             ':description': data['description'],
#             ':questions': data['questions']
#         }
#         survey_table.update_item(
#             Key={'survey_id': survey_id},
#             UpdateExpression=update_expression,
#             ExpressionAttributeValues=expression_attribute_values
#         )
#         send_notification("Survey Updated", f"The survey titled '{data['title']}' has been updated.")
#         return {
#             'statusCode': 200,
#             'body': json.dumps('Survey updated')
#         }
#     except Exception as e:
#         logger.error('Error in update_survey: %s', str(e))
#         return {
#             'statusCode': 500,
#             'body': json.dumps(f'Internal Server Error: {str(e)}')
#         }

# def delete_survey(event):
#     try:
#         survey_id = event['queryStringParameters']['survey_id']
#         logger.info('Deleting survey with ID: %s', survey_id)
#         survey_table.delete_item(Key={'survey_id': survey_id})
#         return {
#             'statusCode': 200,
#             'body': json.dumps('Survey deleted')
#         }
#     except Exception as e:
#         logger.error('Error in delete_survey: %s', str(e))
#         return {
#             'statusCode': 500,
#             'body': json.dumps(f'Internal Server Error: {str(e)}')
#         }

# def answer_survey(event):
#     try:
#         data = json.loads(event['body'])
#         logger.info('Submitting answers with data: %s', json.dumps(data))
#         answer_id = str(uuid.uuid4())
#         answer = {
#             'answer_id': answer_id,
#             'survey_id': data['survey_id'],
#             'answers': data['answers']
#         }
#         answers_table.put_item(Item=answer)
#         return {
#             'statusCode': 201,
#             'body': json.dumps({'answer_id': answer_id})
#         }
#     except Exception as e:
#         logger.error('Error in answer_survey: %s', str(e))
#         return {
#             'statusCode': 500,
#             'body': json.dumps(f'Internal Server Error: {str(e)}')
#         }

# def send_notification(subject, message):
#     try:
#         logger.info('Sending notification with subject: %s and message: %s', subject, message)
#         sns_client.publish(
#             TopicArn=os.environ['SNS_TOPIC_ARN'],
#             Subject=subject,
#             Message=message
#         )
#     except Exception as e:
#         logger.error('Error in send_notification: %s', str(e))

####################################################################################

# import json
# import boto3
# import os
# import uuid
# import logging
# import jwt
# from jwt.algorithms import RSAAlgorithm
# import requests
# from jwt.exceptions import InvalidTokenError

# # Set up logging
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

# # Initialize AWS clients and resources
# dynamodb = boto3.resource('dynamodb')
# survey_table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])
# answers_table = dynamodb.Table(os.environ['ANSWERS_TABLE_NAME'])
# sns_client = boto3.client('sns')

# # Cognito Configuration
# cognito_region = os.environ.get('APP_AWS_REGION')
# user_pool_id = os.environ.get('COGNITO_USER_POOL_ID')
# app_client_id = os.environ.get('COGNITO_USER_POOL_CLIENT_ID')

# def handler(event, context):
#     logger.info('Event: %s', json.dumps(event))
#     method = event.get('httpMethod')
#     path = event.get('path')
    
#     try:
#         if method == 'OPTIONS':
#             return build_cors_response(200, '')
        
#         # Validate JWT token
#         if not is_authorized(event):
#             return build_response(401, {'error': 'Unauthorized'})

#         if path == '/survey' and method == 'POST':
#             return create_survey(event)
#         elif path == '/survey' and method == 'GET':
#             return get_survey(event)
#         elif path == '/survey' and method == 'PUT':
#             return update_survey(event)
#         elif path == '/survey' and method == 'DELETE':
#             return delete_survey(event)
#         elif path == '/survey/answer' and method == 'POST':
#             return answer_survey(event)
#         else:
#             return build_response(405, {'error': 'Method Not Allowed'})
#     except Exception as e:
#         logger.error('Error: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def is_authorized(event):
#     token = get_jwt_token_from_event(event)
#     if not token:
#         logger.warning("No token provided.")
#         return False
#     decoded_token = validate_jwt_token(token)
#     if not decoded_token:
#         logger.warning("Invalid token provided.")
#         return False
#     return True

# def get_jwt_token_from_event(event):
#     auth_header = event['headers'].get('Authorization', '')
#     logger.info(f"Authorization header: {auth_header}")
#     if auth_header.startswith('Bearer '):
#         return auth_header.split(" ")[1]
#     return None

# def validate_jwt_token(token):
#     try:
#         # Fetch AWS Cognito's public keys
#         keys_url = f'https://cognito-idp.{cognito_region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
#         response = requests.get(keys_url)
#         keys = response.json()['keys']

#         # Get the key ID from the token header
#         headers = jwt.get_unverified_header(token)
#         kid = headers['kid']

#         # Find the corresponding public key
#         key = next((k for k in keys if k['kid'] == kid), None)
#         if not key:
#             logger.error('Public key not found in jwks.json')
#             return None

#         # Construct the public key
#         public_key = RSAAlgorithm.from_jwk(json.dumps(key))

#         # Decode and verify the token
#         decoded_token = jwt.decode(
#             token,
#             key=public_key,
#             algorithms=['RS256'],
#             audience=app_client_id,
#             issuer=f'https://cognito-idp.{cognito_region}.amazonaws.com/{user_pool_id}'
#         )
#         return decoded_token
#     except Exception as e:
#         logger.error(f"Token validation error: {e}", exc_info=True)
#         return None


# def build_response(status_code, body):
#     return {
#         'statusCode': status_code,
#         'headers': {
#             'Access-Control-Allow-Origin': '*',
#             'Access-Control-Allow-Headers': 'Content-Type,Authorization',
#             'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
#         },
#         'body': json.dumps(body)
#     }

# def build_cors_response(status_code, body):
#     return {
#         'statusCode': status_code,
#         'headers': {
#             'Access-Control-Allow-Origin': '*',
#             'Access-Control-Allow-Headers': 'Content-Type,Authorization',
#             'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
#         },
#         'body': body
#     }

# def create_survey(event):
#     try:
#         data = json.loads(event['body'])
#         logger.info('Creating survey with data: %s', json.dumps(data))
#         survey_id = str(uuid.uuid4())
#         survey = {
#             'survey_id': survey_id,
#             'title': data['title'],
#             'description': data.get('description', ''),
#             'questions': data['questions']
#         }
#         survey_table.put_item(Item=survey)
#         send_notification("New Survey Created", f"A new survey titled '{data['title']}' has been created.")
#         return build_response(201, {'survey_id': survey_id})
#     except Exception as e:
#         logger.error('Error in create_survey: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def get_survey(event):
#     try:
#         survey_id = event['queryStringParameters'].get('survey_id')
#         logger.info('Fetching survey with ID: %s', survey_id)
#         response = survey_table.get_item(Key={'survey_id': survey_id})
#         item = response.get('Item')
#         if item:
#             return build_response(200, item)
#         else:
#             return build_response(404, {'error': 'Survey not found'})
#     except Exception as e:
#         logger.error('Error in get_survey: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def update_survey(event):
#     try:
#         data = json.loads(event['body'])
#         logger.info('Updating survey with data: %s', json.dumps(data))
#         survey_id = data['survey_id']
#         update_expression = "SET title = :title, description = :description, questions = :questions"
#         expression_attribute_values = {
#             ':title': data['title'],
#             ':description': data.get('description', ''),
#             ':questions': data['questions']
#         }
#         survey_table.update_item(
#             Key={'survey_id': survey_id},
#             UpdateExpression=update_expression,
#             ExpressionAttributeValues=expression_attribute_values
#         )
#         send_notification("Survey Updated", f"The survey titled '{data['title']}' has been updated.")
#         return build_response(200, {'message': 'Survey updated'})
#     except Exception as e:
#         logger.error('Error in update_survey: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def delete_survey(event):
#     try:
#         survey_id = event['queryStringParameters'].get('survey_id')
#         logger.info('Deleting survey with ID: %s', survey_id)
#         survey_table.delete_item(Key={'survey_id': survey_id})
#         return build_response(200, {'message': 'Survey deleted'})
#     except Exception as e:
#         logger.error('Error in delete_survey: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def answer_survey(event):
#     try:
#         data = json.loads(event['body'])
#         logger.info('Submitting answers with data: %s', json.dumps(data))
#         answer_id = str(uuid.uuid4())
#         answer = {
#             'answer_id': answer_id,
#             'survey_id': data['survey_id'],
#             'answers': data['answers']
#         }
#         answers_table.put_item(Item=answer)
#         return build_response(201, {'answer_id': answer_id})
#     except Exception as e:
#         logger.error('Error in answer_survey: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def send_notification(subject, message):
#     try:
#         logger.info('Sending notification with subject: %s and message: %s', subject, message)
#         sns_client.publish(
#             TopicArn=os.environ['SNS_TOPIC_ARN'],
#             Subject=subject,
#             Message=message
#         )
#     except Exception as e:
#         logger.error('Error in send_notification: %s', str(e), exc_info=True)


# import json
# import boto3
# import os
# import uuid
# import logging
# import jwt
# from jwt.algorithms import RSAAlgorithm
# import requests
# from jwt.exceptions import InvalidTokenError
# from boto3.dynamodb.conditions import Key, Attr

# # Set up logging
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

# # Initialize AWS clients and resources
# dynamodb = boto3.resource('dynamodb')
# survey_table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])
# answers_table = dynamodb.Table(os.environ['ANSWERS_TABLE_NAME'])
# sns_client = boto3.client('sns')

# # Cognito Configuration
# cognito_region = os.environ.get('APP_AWS_REGION')
# user_pool_id = os.environ.get('COGNITO_USER_POOL_ID')
# app_client_id = os.environ.get('COGNITO_USER_POOL_CLIENT_ID')

# def handler(event, context):
#     logger.info('Event: %s', json.dumps(event))
#     method = event.get('httpMethod')
#     path = event.get('path')

#     try:
#         if method == 'OPTIONS':
#             return build_cors_response(200, '')

#         # Validate JWT token
#         decoded_token = get_decoded_token(event)
#         if not decoded_token:
#             return build_response(401, {'error': 'Unauthorized'})

#         # Extract username from the decoded token
#         username = decoded_token.get('cognito:username')

#         if path == '/survey' and method == 'POST':
#             return create_survey(event, username)
#         elif path == '/survey' and method == 'GET':
#             return get_surveys(event, username)
#         elif path == '/survey' and method == 'PUT':
#             return update_survey(event, username)
#         elif path == '/survey' and method == 'DELETE':
#             return delete_survey(event, username)
#         elif path == '/survey/answer' and method == 'POST':
#             return answer_survey(event)
#         else:
#             return build_response(405, {'error': 'Method Not Allowed'})
#     except Exception as e:
#         logger.error('Error: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def get_decoded_token(event):
#     token = get_jwt_token_from_event(event)
#     if not token:
#         logger.warning("No token provided.")
#         return None
#     decoded_token = validate_jwt_token(token)
#     if not decoded_token:
#         logger.warning("Invalid token provided.")
#         return None
#     return decoded_token

# def get_jwt_token_from_event(event):
#     auth_header = event['headers'].get('Authorization', '')
#     logger.info(f"Authorization header: {auth_header}")
#     if auth_header.startswith('Bearer '):
#         return auth_header.split(" ")[1]
#     return None

# def validate_jwt_token(token):
#     try:
#         # Fetch AWS Cognito's public keys
#         keys_url = f'https://cognito-idp.{cognito_region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
#         response = requests.get(keys_url)
#         keys = response.json()['keys']

#         # Get the key ID from the token header
#         headers = jwt.get_unverified_header(token)
#         kid = headers['kid']

#         # Find the corresponding public key
#         key = next((k for k in keys if k['kid'] == kid), None)
#         if not key:
#             logger.error('Public key not found in jwks.json')
#             return None

#         # Construct the public key
#         public_key = RSAAlgorithm.from_jwk(json.dumps(key))

#         # Decode and verify the token
#         decoded_token = jwt.decode(
#             token,
#             key=public_key,
#             algorithms=['RS256'],
#             audience=app_client_id,
#             issuer=f'https://cognito-idp.{cognito_region}.amazonaws.com/{user_pool_id}'
#         )
#         return decoded_token
#     except Exception as e:
#         logger.error(f"Token validation error: {e}", exc_info=True)
#         return None

# def build_response(status_code, body):
#     return {
#         'statusCode': status_code,
#         'headers': {
#             'Access-Control-Allow-Origin': '*',
#             'Access-Control-Allow-Headers': 'Content-Type,Authorization',
#             'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
#         },
#         'body': json.dumps(body)
#     }

# def build_cors_response(status_code, body):
#     return {
#         'statusCode': status_code,
#         'headers': {
#             'Access-Control-Allow-Origin': '*',
#             'Access-Control-Allow-Headers': 'Content-Type,Authorization',
#             'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
#         },
#         'body': body
#     }

# def create_survey(event, username):
#     try:
#         data = json.loads(event['body'])
#         logger.info('Creating survey with data: %s', json.dumps(data))
#         survey_id = str(uuid.uuid4())
#         survey = {
#             'survey_id': survey_id,
#             'username': username,  # Associate the survey with the user
#             'title': data['title'],
#             'description': data.get('description', ''),
#             'questions': data['questions']
#         }
#         survey_table.put_item(Item=survey)
#         send_notification("New Survey Created", f"A new survey titled '{data['title']}' has been created by {username}.")
#         return build_response(201, {'survey_id': survey_id})
#     except Exception as e:
#         logger.error('Error in create_survey: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def get_surveys(event, username):
#     try:
#         survey_id = event['queryStringParameters'].get('survey_id') if event.get('queryStringParameters') else None
#         if survey_id:
#             # Fetch a single survey by survey_id
#             logger.info('Fetching survey with ID: %s', survey_id)
#             response = survey_table.get_item(Key={'survey_id': survey_id})
#             item = response.get('Item')
#             if item:
#                 return build_response(200, item)
#             else:
#                 return build_response(404, {'error': 'Survey not found'})
#         else:
#             # Fetch all surveys for the user
#             logger.info('Fetching surveys for user: %s', username)
#             response = survey_table.scan(
#                 FilterExpression=Attr('username').eq(username)
#             )
#             surveys = response.get('Items', [])
#             return build_response(200, {'surveys': surveys})
#     except Exception as e:
#         logger.error('Error in get_surveys: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def update_survey(event, username):
#     try:
#         data = json.loads(event['body'])
#         logger.info('Updating survey with data: %s', json.dumps(data))
#         survey_id = data['survey_id']
#         # Check if the survey belongs to the user
#         existing_survey = survey_table.get_item(Key={'survey_id': survey_id}).get('Item')
#         if not existing_survey or existing_survey.get('username') != username:
#             return build_response(403, {'error': 'Forbidden'})
#         update_expression = "SET title = :title, description = :description, questions = :questions"
#         expression_attribute_values = {
#             ':title': data['title'],
#             ':description': data.get('description', ''),
#             ':questions': data['questions']
#         }
#         survey_table.update_item(
#             Key={'survey_id': survey_id},
#             UpdateExpression=update_expression,
#             ExpressionAttributeValues=expression_attribute_values
#         )
#         send_notification("Survey Updated", f"The survey titled '{data['title']}' has been updated by {username}.")
#         return build_response(200, {'message': 'Survey updated'})
#     except Exception as e:
#         logger.error('Error in update_survey: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def delete_survey(event, username):
#     try:
#         survey_id = event['queryStringParameters'].get('survey_id')
#         logger.info('Deleting survey with ID: %s', survey_id)
#         # Check if the survey belongs to the user
#         existing_survey = survey_table.get_item(Key={'survey_id': survey_id}).get('Item')
#         if not existing_survey or existing_survey.get('username') != username:
#             return build_response(403, {'error': 'Forbidden'})
#         survey_table.delete_item(Key={'survey_id': survey_id})
#         return build_response(200, {'message': 'Survey deleted'})
#     except Exception as e:
#         logger.error('Error in delete_survey: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def answer_survey(event):
#     try:
#         data = json.loads(event['body'])
#         logger.info('Submitting answers with data: %s', json.dumps(data))
#         answer_id = str(uuid.uuid4())
#         answer = {
#             'answer_id': answer_id,
#             'survey_id': data['survey_id'],
#             'answers': data['answers']
#         }
#         answers_table.put_item(Item=answer)
#         return build_response(201, {'answer_id': answer_id})
#     except Exception as e:
#         logger.error('Error in answer_survey: %s', str(e), exc_info=True)
#         return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

# def send_notification(subject, message):
#     try:
#         logger.info('Sending notification with subject: %s and message: %s', subject, message)
#         sns_client.publish(
#             TopicArn=os.environ['SNS_TOPIC_ARN'],
#             Subject=subject,
#             Message=message
#         )
#     except Exception as e:
#         logger.error('Error in send_notification: %s', str(e), exc_info=True)


# main.py

import json
import boto3
import os
import uuid
import logging
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from jwt.exceptions import InvalidTokenError
from boto3.dynamodb.conditions import Key, Attr

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients and resources
dynamodb = boto3.resource('dynamodb')
survey_table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])
answers_table = dynamodb.Table(os.environ['ANSWERS_TABLE_NAME'])
sns_client = boto3.client('sns')

# Cognito Configuration
cognito_region = os.environ.get('APP_AWS_REGION')
user_pool_id = os.environ.get('COGNITO_USER_POOL_ID')
app_client_id = os.environ.get('COGNITO_USER_POOL_CLIENT_ID')

def handler(event, context):
    logger.info('Event: %s', json.dumps(event))
    method = event.get('httpMethod')
    path = event.get('path')

    try:
        if method == 'OPTIONS':
            return build_cors_response(200, '')

        # Validate JWT token
        decoded_token = get_decoded_token(event)
        if not decoded_token:
            return build_response(401, {'error': 'Unauthorized'})

        # Extract username from the decoded token
        username = decoded_token.get('cognito:username') or decoded_token.get('username')

        if path == '/survey' and method == 'POST':
            return create_survey(event, username)
        elif path == '/survey' and method == 'GET':
            return get_survey(event, username)
        elif path == '/survey' and method == 'PUT':
            return update_survey(event, username)
        elif path == '/survey' and method == 'DELETE':
            return delete_survey(event, username)
        elif path == '/survey/answer' and method == 'POST':
            return answer_survey(event)
        else:
            return build_response(405, {'error': 'Method Not Allowed'})
    except Exception as e:
        logger.error('Error: %s', str(e), exc_info=True)
        return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

def get_decoded_token(event):
    token = get_jwt_token_from_event(event)
    if not token:
        logger.warning("No token provided.")
        return None
    decoded_token = validate_jwt_token(token)
    if not decoded_token:
        logger.warning("Invalid token provided.")
        return None
    return decoded_token

def get_jwt_token_from_event(event):
    auth_header = event['headers'].get('Authorization', '')
    logger.info(f"Authorization header: {auth_header}")
    if auth_header.startswith('Bearer '):
        return auth_header.split(" ")[1]
    return None

def validate_jwt_token(token):
    try:
        # Fetch AWS Cognito's public keys
        keys_url = f'https://cognito-idp.{cognito_region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
        response = requests.get(keys_url)
        keys = response.json()['keys']

        # Get the key ID from the token header
        headers = jwt.get_unverified_header(token)
        kid = headers['kid']

        # Find the corresponding public key
        key = next((k for k in keys if k['kid'] == kid), None)
        if not key:
            logger.error('Public key not found in jwks.json')
            return None

        # Construct the public key
        public_key = RSAAlgorithm.from_jwk(json.dumps(key))

        # Decode and verify the token
        decoded_token = jwt.decode(
            token,
            key=public_key,
            algorithms=['RS256'],
            audience=app_client_id,
            issuer=f'https://cognito-idp.{cognito_region}.amazonaws.com/{user_pool_id}'
        )
        return decoded_token
    except Exception as e:
        logger.error(f"Token validation error: {e}", exc_info=True)
        return None

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }

def build_cors_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': body
    }

def create_survey(event, username):
    try:
        data = json.loads(event['body'])
        logger.info('Creating survey with data: %s', json.dumps(data))
        survey_id = str(uuid.uuid4())
        survey = {
            'survey_id': survey_id,
            'username': username,
            'title': data['title'],
            'description': data.get('description', ''),
            'questions': data['questions']
        }
        survey_table.put_item(Item=survey)
        # Optionally send a notification
        return build_response(201, {'survey_id': survey_id})
    except Exception as e:
        logger.error('Error in create_survey: %s', str(e), exc_info=True)
        return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

def get_survey(event, username):

    logger.info('Using updated get_survey function with safe handling of queryStringParameters.')

    try:
        # Safely get 'queryStringParameters' or default to an empty dict
        query_params = event.get('queryStringParameters') or {}
        survey_id = query_params.get('survey_id')

        if survey_id:
            # Fetch a single survey by survey_id
            logger.info('Fetching survey with ID: %s', survey_id)
            response = survey_table.get_item(Key={'survey_id': survey_id})
            item = response.get('Item')
            if item:
                return build_response(200, item)
            else:
                return build_response(404, {'error': 'Survey not found'})
        else:
            # Fetch all surveys for the user
            logger.info('Fetching surveys for user: %s', username)
            response = survey_table.scan(
                FilterExpression=Attr('username').eq(username)
            )
            surveys = response.get('Items', [])
            return build_response(200, {'surveys': surveys})
    except Exception as e:
        logger.error('Error in get_survey fuck: %s', str(e), exc_info=True)
        return build_response(500, {'error': f'Internal Server Error: {str(e)}'})



def update_survey(event, username):
    try:
        data = json.loads(event['body'])
        logger.info('Updating survey with data: %s', json.dumps(data))
        survey_id = data['survey_id']
        # Check if the survey belongs to the user
        existing_survey = survey_table.get_item(Key={'survey_id': survey_id}).get('Item')
        if not existing_survey or existing_survey.get('username') != username:
            return build_response(403, {'error': 'Forbidden'})
        update_expression = "SET title = :title, description = :description, questions = :questions"
        expression_attribute_values = {
            ':title': data['title'],
            ':description': data.get('description', ''),
            ':questions': data['questions']
        }
        survey_table.update_item(
            Key={'survey_id': survey_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        # Optionally send a notification
        return build_response(200, {'message': 'Survey updated'})
    except Exception as e:
        logger.error('Error in update_survey: %s', str(e), exc_info=True)
        return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

def delete_survey(event, username):
    try:
        if 'queryStringParameters' in event and event['queryStringParameters']:
            survey_id = event['queryStringParameters'].get('survey_id')
        else:
            return build_response(400, {'error': 'survey_id is required'})

        logger.info('Deleting survey with ID: %s', survey_id)
        # Check if the survey belongs to the user
        existing_survey = survey_table.get_item(Key={'survey_id': survey_id}).get('Item')
        if not existing_survey or existing_survey.get('username') != username:
            return build_response(403, {'error': 'Forbidden'})
        survey_table.delete_item(Key={'survey_id': survey_id})
        return build_response(200, {'message': 'Survey deleted'})
    except Exception as e:
        logger.error('Error in delete_survey: %s', str(e), exc_info=True)
        return build_response(500, {'error': f'Internal Server Error: {str(e)}'})

def answer_survey(event):
    try:
        data = json.loads(event['body'])
        logger.info('Submitting answers with data: %s', json.dumps(data))
        answer_id = str(uuid.uuid4())
        answer = {
            'answer_id': answer_id,
            'survey_id': data['survey_id'],
            'answers': data['answers']
        }
        answers_table.put_item(Item=answer)
        return build_response(201, {'answer_id': answer_id})
    except Exception as e:
        logger.error('Error in answer_survey: %s', str(e), exc_info=True)
        return build_response(500, {'error': f'Internal Server Error: {str(e)}'})


def send_notification(subject, message):
    try:
        logger.info('Sending notification with subject: %s and message: %s', subject, message)
        sns_client.publish(
            TopicArn=os.environ['SNS_TOPIC_ARN'],
            Subject=subject,
            Message=message
        )
    except Exception as e:
        logger.error('Error in send_notification: %s', str(e), exc_info=True)
