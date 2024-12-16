from flask import Flask, render_template, jsonify, request, make_response
from botocore.exceptions import ClientError
import os
import boto3
import logging
import jwt
from jwt.algorithms import RSAAlgorithm
import json
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cognito Configuration
cognito_client = boto3.client('cognito-idp', region_name=os.environ.get('APP_AWS_REGION'))
user_pool_id = os.environ.get('COGNITO_USER_POOL_ID')
app_client_id = os.environ.get('COGNITO_USER_POOL_CLIENT_ID')

# Initialize AWS Lambda client for invoking backend Lambda
lambda_client = boto3.client('lambda', region_name=os.environ.get('APP_AWS_REGION'))

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    return response

def get_jwt_token_from_header():
    auth_header = request.headers.get('Authorization', None)
    logger.info(f"Authorization header: {auth_header}")
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(" ")[1]  # Assuming "Bearer <Token>"
    return None

def validate_jwt_token(token):
    try:
        # Fetch AWS Cognito's public keys
        keys_url = f'https://cognito-idp.{os.environ.get("APP_AWS_REGION")}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
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
            issuer=f'https://cognito-idp.{os.environ.get("APP_AWS_REGION")}.amazonaws.com/{user_pool_id}'
        )
        return decoded_token
    except Exception as e:
        logger.error(f"Token validation error: {e}", exc_info=True)
        return None

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

@app.template_filter('datetimeformat')
def datetimeformat(value):
    return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/flask/dashboard', methods=['GET', 'OPTIONS'])
def dashboard():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    else:
        logger.info("Accessing dashboard.")

        token = get_jwt_token_from_header()
        if not token:
            logger.warning("No token provided.")
            return jsonify({'error': 'Token is missing'}), 401

        decoded_token = validate_jwt_token(token)
        if not decoded_token:
            logger.warning("Invalid token provided.")
            return jsonify({'error': 'Invalid token'}), 401

        username = decoded_token.get('username') or decoded_token.get('cognito:username')

        # Render the dashboard template and return as HTML string
        return render_template('dashboard.html', username=username)

@app.route('/flask/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided.'}), 400
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'error': 'All fields are required.'}), 400

        try:
            response = cognito_client.sign_up(
                ClientId=app_client_id,
                Username=username,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email}
                ]
            )
            logger.info("User registered successfully.")
            return jsonify({'message': 'Registration successful. Please check your email to verify your account.'}), 200
        except ClientError as e:
            logger.error(f"Registration error: {e}")
            return jsonify({'error': 'Registration failed. Please try again.'}), 400

@app.route('/flask/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided.'}), 400
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({'error': 'Username and password are required.'}), 400
        try:
            response = cognito_client.initiate_auth(
                ClientId=app_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            logger.info("Authentication successful. Cognito response received.")

            id_token = response['AuthenticationResult']['IdToken']

            logger.info(f"User logged in successfully. JWT Token: {id_token}")

            # Return the token as JSON
            return jsonify({'access_token': id_token})

        except ClientError as e:
            logger.error(f"Login error: {e}")
            return jsonify({'error': 'Login failed. Please check your credentials.'}), 400

@app.route('/flask/create_survey', methods=['POST', 'OPTIONS'])
def create_survey():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    else:
        logger.info("Accessing create_survey.")

        token = get_jwt_token_from_header()
        if not token:
            logger.warning("No token provided.")
            return jsonify({'error': 'Token is missing'}), 401

        decoded_token = validate_jwt_token(token)
        if not decoded_token:
            logger.warning("Invalid token provided.")
            return jsonify({'error': 'Invalid token'}), 401

        data = request.get_json()
        if not data:
            logger.warning("No data provided in the request body.")
            return jsonify({'error': 'No data provided'}), 400

        # Prepare the payload for the backend Lambda
        payload = {
            'body': json.dumps(data),
            'headers': {
                'Authorization': request.headers.get('Authorization')
            },
            'httpMethod': 'POST',
            'path': '/survey'
        }

        try:
            # Invoke the backend Lambda function
            response = lambda_client.invoke(
                FunctionName=os.environ.get('BACKEND_LAMBDA_FUNCTION_NAME'),
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )

            # Read and parse the response from the backend Lambda
            response_payload = json.loads(response['Payload'].read().decode('utf-8'))

            # Return the response to the client
            return (
                response_payload.get('body', ''),
                response_payload.get('statusCode', 200),
                {'Content-Type': 'application/json'}
            )
        except Exception as e:
            logger.error(f"Error invoking backend Lambda: {e}", exc_info=True)
            return jsonify({'error': 'Failed to create survey'}), 500

@app.route('/flask/get_all_surveys', methods=['GET', 'OPTIONS'])
def get_all_surveys():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    else:
        logger.info("Fetching all surveys.")

        token = get_jwt_token_from_header()
        if not token:
            logger.warning("No token provided.")
            return jsonify({'error': 'Token is missing'}), 401

        decoded_token = validate_jwt_token(token)
        if not decoded_token:
            logger.warning("Invalid token provided.")
            return jsonify({'error': 'Invalid token'}), 401

        # Prepare the payload for the backend Lambda to fetch all surveys
        payload = {
            'headers': {
                'Authorization': request.headers.get('Authorization')
            },
            'httpMethod': 'GET',
            'path': '/survey',
            'queryStringParameters': None
        }

        try:
            # Invoke the backend Lambda function
            response = lambda_client.invoke(
                FunctionName=os.environ.get('BACKEND_LAMBDA_FUNCTION_NAME'),
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )

            # Read and parse the response from the backend Lambda
            response_payload = json.loads(response['Payload'].read().decode('utf-8'))

            # Return the response to the client
            return (
                response_payload.get('body', ''),
                response_payload.get('statusCode', 200),
                {'Content-Type': 'application/json'}
            )
        except Exception as e:
            logger.error(f"Error invoking backend Lambda: {e}", exc_info=True)
            return jsonify({'error': 'Failed to fetch surveys'}), 500

@app.route('/flask/survey/<survey_id>', methods=['GET', 'DELETE', 'OPTIONS'])
def survey_handler(survey_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    elif request.method == 'GET':
        return survey_details(survey_id)
    elif request.method == 'DELETE':
        return delete_survey(survey_id)

def survey_details(survey_id):
    logger.info(f"Fetching survey details for survey_id: {survey_id}")

    token = get_jwt_token_from_header()
    if not token:
        logger.warning("No token provided.")
        return jsonify({'error': 'Token is missing'}), 401

    decoded_token = validate_jwt_token(token)
    if not decoded_token:
        logger.warning("Invalid token provided.")
        return jsonify({'error': 'Invalid token'}), 401

    # Prepare the payload to fetch survey details
    payload = {
        'headers': {
            'Authorization': request.headers.get('Authorization')
        },
        'httpMethod': 'GET',
        'path': '/survey',
        'queryStringParameters': {
            'survey_id': survey_id
        }
    }

    try:
        # Invoke the backend Lambda function
        response = lambda_client.invoke(
            FunctionName=os.environ.get('BACKEND_LAMBDA_FUNCTION_NAME'),
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        # Read and parse the response from the backend Lambda
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))

        status_code = response_payload.get('statusCode', 200)
        body = response_payload.get('body', '')

        # Parse the body if it's a JSON string
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass

        # Return the response to the client
        return jsonify(body), status_code

    except Exception as e:
        logger.error(f"Error invoking backend Lambda: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch survey details'}), 500
    
def delete_survey(survey_id):
    logger.info(f"Deleting survey with ID: {survey_id}")

    token = get_jwt_token_from_header()
    if not token:
        logger.warning("No token provided.")
        return jsonify({'error': 'Token is missing'}), 401

    decoded_token = validate_jwt_token(token)
    if not decoded_token:
        logger.warning("Invalid token provided.")
        return jsonify({'error': 'Invalid token'}), 401

    # Prepare the payload to delete the survey
    payload = {
        'headers': {
            'Authorization': request.headers.get('Authorization')
        },
        'httpMethod': 'DELETE',
        'path': '/survey',
        'queryStringParameters': {
            'survey_id': survey_id
        }
    }

    try:
        # Invoke the backend Lambda function
        response = lambda_client.invoke(
            FunctionName=os.environ.get('BACKEND_LAMBDA_FUNCTION_NAME'),
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        # Read and parse the response from the backend Lambda
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))

        status_code = response_payload.get('statusCode', 200)
        body = response_payload.get('body', '')

        # Parse the body if it's a JSON string
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass

        # Return the response to the client
        return jsonify(body), status_code

    except Exception as e:
        logger.error(f"Error invoking backend Lambda: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete survey'}), 500

@app.route('/flask/survey/<survey_id>/responses', methods=['GET', 'OPTIONS'])
def survey_responses(survey_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    else:
        logger.info(f"Fetching survey responses for survey_id: {survey_id}")

        token = get_jwt_token_from_header()
        if not token:
            logger.warning("No token provided.")
            return jsonify({'error': 'Token is missing'}), 401

        decoded_token = validate_jwt_token(token)
        if not decoded_token:
            logger.warning("Invalid token provided.")
            return jsonify({'error': 'Invalid token'}), 401

        # Prepare the payload to fetch survey responses
        payload = {
            'headers': {
                'Authorization': request.headers.get('Authorization')
            },
            'httpMethod': 'GET',
            'path': '/survey/responses',
            'queryStringParameters': {
                'survey_id': survey_id
            }
        }

        try:
            # Invoke the backend Lambda function
            response = lambda_client.invoke(
                FunctionName=os.environ.get('BACKEND_LAMBDA_FUNCTION_NAME'),
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )

            # Read and parse the response from the backend Lambda
            response_payload = json.loads(response['Payload'].read().decode('utf-8'))

            status_code = response_payload.get('statusCode', 200)
            body = response_payload.get('body', '')

            # Parse the body if it's a JSON string
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                pass

            # Return the response to the client
            return jsonify(body), status_code

        except Exception as e:
            logger.error(f"Error invoking backend Lambda: {e}", exc_info=True)
            return jsonify({'error': 'Failed to fetch survey responses'}), 500

@app.route('/flask/submit_survey', methods=['POST', 'OPTIONS'])
def submit_survey():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    else:
        logger.info("Submitting survey answers.")

        token = get_jwt_token_from_header()
        if not token:
            logger.warning("No token provided.")
            return jsonify({'error': 'Token is missing'}), 401

        decoded_token = validate_jwt_token(token)
        if not decoded_token:
            logger.warning("Invalid token provided.")
            return jsonify({'error': 'Invalid token'}), 401

        data = request.get_json()
        if not data:
            logger.warning("No data provided in the request body.")
            return jsonify({'error': 'No data provided'}), 400

        # Prepare the payload for the backend Lambda
        payload = {
            'body': json.dumps(data),
            'headers': {
                'Authorization': request.headers.get('Authorization')
            },
            'httpMethod': 'POST',
            'path': '/survey/answer'
        }

        try:
            # Invoke the backend Lambda function
            response = lambda_client.invoke(
                FunctionName=os.environ.get('BACKEND_LAMBDA_FUNCTION_NAME'),
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )

            # Read and parse the response from the backend Lambda
            response_payload = json.loads(response['Payload'].read().decode('utf-8'))

            # Return the response to the client
            return (
                response_payload.get('body', ''),
                response_payload.get('statusCode', 200),
                {'Content-Type': 'application/json'}
            )
        except Exception as e:
            logger.error(f"Error invoking backend Lambda: {e}", exc_info=True)
            return jsonify({'error': 'Failed to submit answers'}), 500

if __name__ == '__main__':
    app.run(debug=True)
