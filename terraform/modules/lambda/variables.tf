variable "region" {
  description = "The AWS region to deploy resources."
  type        = string
}

variable "api_gateway_id" {
  description = "The API gateway ID."
  type        = string
}

variable "lambda_function_name" {
  description = "The name of the Lambda function"
  type        = string
}

variable "lambda_execution_role_arn" {
  description = "The ARN of the Lambda execution role"
  type        = string
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  type        = string
}

variable "answers_table_name" {
  description = "The name of the DynamoDB answers table"
  type        = string
}

variable "lambda_s3_bucket" {
  description = "The S3 bucket to store Lambda function code"
  type        = string
}

variable "lambda_s3_key" {
  description = "The S3 key for the Lambda function code"
  type        = string
}

variable "sns_topic_arn" {
  description = "The ARN of the SNS topic"
  type        = string
}

variable "cognito_user_pool_id" {
  description = "The ID of the Cognito User Pool"
  type        = string
  
}

variable "cognito_user_pool_client_id" {
  description = "The ID of the Cognito User Pool Client"
  type        = string  
  
}

variable "common_tags" {
  description = "A map of tags to assign to the resources"
  type        = map(string)
}


