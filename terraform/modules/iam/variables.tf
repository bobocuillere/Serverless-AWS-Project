variable "lambda_execution_role_name" {
  description = "The name of the Lambda execution role"
  type        = string
}

variable "backend_lambda_function_name" {
  description = "The name of the backend Lambda function"
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

variable "region" {
  description = "The AWS region"
  type        = string
}

variable "topic_name" {
  description = "The name of the SNS topic"
  type        = string
  
}

variable "cognito_user_pool_id" {
  description = "The ID of the Cognito User Pool"
  type        = string
  
}

variable "private_bucket_name" {
  description = "The name of the private S3 bucket"
  type        = string
  
}

variable "common_tags" {
  description = "A map of tags to assign to the resources"
  type        = map(string)
}
