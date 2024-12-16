data "aws_caller_identity" "current" {}

resource "aws_s3_object" "flask_lambda_zip" {
  bucket = var.s3_bucket_name
  key    = var.flask_lambda_s3_key
  source = "${path.module}/flask_function/flask_function.zip"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_s3_object" "upload_public_index" {
  bucket       = var.flask_lambda_s3_bucket_id
  key          = "index.html"
  source       = "${path.module}/flask_function/templates/index.html"
  content_type = "text/html"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_s3_object" "upload_templates_private_bucket" {
  for_each = { for f in fileset("${path.module}/flask_function/templates", "**/*") : f => f if f != "index.html" }
  bucket   = var.s3_bucket_name
  key      = each.value
  source   = "${path.module}/flask_function/templates/${each.value}"
  content_type = "text/html"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_s3_object" "upload_static_public_bucket" {
  for_each = fileset("${path.module}/flask_function/static", "**/*")
  bucket   = var.flask_lambda_s3_bucket_id
  key      = each.value
  source   = "${path.module}/flask_function/static/${each.value}"
  content_type = each.value == "css/styles.css" ? "text/css" : "application/octet-stream"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_s3_object" "upload_static_private_bucket" {
  for_each = fileset("${path.module}/flask_function/static", "**/*")
  bucket   = var.s3_bucket_name
  key      = each.value
  source   = "${path.module}/flask_function/static/${each.value}"
  content_type = each.value == "css/styles.css" ? "text/css" : "application/octet-stream"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lambda_function" "flask_function" {
  function_name = "flask-application"
  role          = var.lambda_execution_role_arn
  handler       = "wsgi.lambda_handler"
  runtime       = "python3.10"

  filename         = "${path.module}/flask_function/flask_function.zip"
  source_code_hash = filebase64sha256("${path.module}/flask_function/flask_function.zip")

  environment {
    variables = {
      API_GATEWAY_URL     = var.api_gateway_url
      APP_AWS_REGION          = var.APP_AWS_REGION
      COGNITO_USER_POOL_ID = var.cognito_user_pool_id
      COGNITO_USER_POOL_CLIENT_ID = var.cognito_user_pool_client_id
      REQUEST_METHOD = "GET"
      SURVEY_LAMBDA_FUNCTION_NAME = "flask-application"
      BACKEND_LAMBDA_FUNCTION_NAME = "survey-lambda-function"
      PRIVATE_S3_BUCKET_NAME = var.s3_bucket_name
    }
  }

  tags = var.common_tags

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lambda_permission" "api_gateway_flask" {
  statement_id  = "AllowAPIGatewayInvokeFlask"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.flask_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.APP_AWS_REGION}:${data.aws_caller_identity.current.account_id}:${var.api_gateway_id}/*"
}