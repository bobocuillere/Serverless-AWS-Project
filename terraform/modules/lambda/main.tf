data "aws_caller_identity" "current" {}

resource "aws_s3_object" "lambda_zip" {
  bucket = var.lambda_s3_bucket
  key    = var.lambda_s3_key
  source = "${path.module}/lambda_function/lambda_function.zip"
}


resource "aws_lambda_function" "lambda" {
  function_name = var.lambda_function_name
  role          = var.lambda_execution_role_arn
  handler       = "main.handler"
  runtime       = "python3.10"

  filename         = "${path.module}/lambda_function/lambda_function.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_function/lambda_function.zip")

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
      ANSWERS_TABLE_NAME  = var.answers_table_name
      SNS_TOPIC_ARN       = var.sns_topic_arn
      APP_AWS_REGION      = var.region
      COGNITO_USER_POOL_ID = var.cognito_user_pool_id
      COGNITO_USER_POOL_CLIENT_ID = var.cognito_user_pool_client_id
    }
  }

  tags = var.common_tags
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${data.aws_caller_identity.current.account_id}:${var.api_gateway_id}/*"
}
