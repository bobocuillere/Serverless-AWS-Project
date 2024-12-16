provider "aws" {
  region = var.region
}

terraform {
  backend "s3" {
    region         = "eu-central-1"
    bucket         = "terraform-state-bucket-sophnel"
    key            = "serverless-survey/"
    dynamodb_table = "serverless-survey-terraform-lock"
  }
}

locals {
  common_tags = {
    Project     = "Serverless Survey Cloud Project"
    ManagedBy   = "Terraform"
    Department  = "IT Department"
    Application = "Serverless Survey App"
    Owner       = "Sophnel"
  }
}
data "aws_caller_identity" "current" {}

module "lambda" {
  source                    = "./modules/lambda"
  lambda_function_name      = "survey-lambda-function"
  lambda_execution_role_arn = module.iam.lambda_execution_role_arn

  dynamodb_table_name       = module.dynamodb.table_name
  answers_table_name        = module.dynamodb.answers_table_name

  lambda_s3_bucket          = module.s3.s3_bucket_name
  lambda_s3_key             = "lambda_function.zip"

  sns_topic_arn             = module.sns.sns_topic_arn
  region                    = var.region
  api_gateway_id            = module.api_gateway.api_id

  cognito_user_pool_client_id = module.cognito.user_pool_client_id
  cognito_user_pool_id = module.cognito.user_pool_id
  # user_pool_arn = module.cognito.user_pool_arn
  common_tags               = local.common_tags
}

module "frontend" {
  source          = "./modules/frontend"
  APP_AWS_REGION  = var.region
  api_gateway_id  = module.api_gateway.api_id
  api_gateway_url = "https://${module.api_gateway.api_id}.execute-api.${var.region}.amazonaws.com/prod/flask"

  cognito_user_pool_id        = module.cognito.user_pool_id
  cognito_user_pool_client_id = module.cognito.user_pool_client_id

  lambda_execution_role_arn = module.iam.lambda_execution_role_arn
  s3_bucket_name            = module.s3.s3_bucket_name
  flask_lambda_s3_key       = "flask_function.zip"
  flask_s3_bucket_name      = module.s3.flask_s3_bucket_name
  flask_lambda_s3_bucket_id = module.s3.flash_s3_bucket_id

  sns_topic_arn = module.sns.sns_topic_arn
  common_tags   = local.common_tags
}

module "api_gateway" {
  source          = "./modules/api_gateway"
  api_name        = "survey-api-gateway"
  api_description = "API Gateway for Survey Application"

  flask_lambda_invoke_arn = module.frontend.flask_function_invoke_arn

  lambda_function_name     = module.lambda.lambda_function_name
  lambda_invoke_arn        = module.lambda.lambda_function_invoke_arn
  cloudwatch_log_group_arn = module.cloudwatch.api_gateway_log_group_arn

  common_tags = local.common_tags
}


module "dynamodb" {
  source             = "./modules/dynamodb"
  table_name         = "survey-table"
  answers_table_name = "answers-table"
  hash_key           = "survey_id"
  hash_key_type      = "S"
  read_capacity      = 1
  write_capacity     = 1
  common_tags        = local.common_tags
}

module "sns" {
  source      = "./modules/sns"
  topic_name  = "survey-sns-topic"
  backend_lambda_function_arn = module.lambda.lambda_function_arn
  lambda_function_name = module.lambda.lambda_function_name
  common_tags = local.common_tags
}

module "cognito" {
  source                = "./modules/cognito"
  user_pool_name        = "survey-user-pool"
  user_pool_client_name = "survey-user-pool-client"
  # backend_lambda_function_arn = module.lambda.lambda_function_arn
  common_tags           = local.common_tags
}

module "s3" {
  source               = "./modules/s3"
  s3_bucket_name       = "serveless-survey"
  flask_s3_bucket_name = "flask-survey-ui"
  common_tags          = local.common_tags
}

module "iam" {
  source                     = "./modules/iam"
  lambda_execution_role_name = "survey-lambda-role"
  backend_lambda_function_name = module.lambda.lambda_function_name
  dynamodb_table_name        = module.dynamodb.table_name
  answers_table_name         = module.dynamodb.answers_table_name
  topic_name                 = module.sns.sns_topic_name
  region                     = var.region

  cognito_user_pool_id = module.cognito.user_pool_id

  private_bucket_name = module.s3.s3_bucket_name
  common_tags         = local.common_tags
}

module "cloudwatch" {
  source               = "./modules/cloudwatch"
  lambda_function_name = module.lambda.lambda_function_name
  api_gateway_id       = module.api_gateway.api_id
  common_tags          = local.common_tags
}
