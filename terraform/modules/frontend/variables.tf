variable "APP_AWS_REGION" {
  description = "The AWS region to deploy resources."
  type        = string
}

variable "cognito_user_pool_id" {
  description = "The Cognito User Pool ID."
  type        = string
  
}

variable "cognito_user_pool_client_id" {
  description = "The Cognito User Pool Client ID."
  type        = string
  
}

variable "api_gateway_id" {
  description = "The API gateway ID."
  type        = string
}

variable "lambda_execution_role_arn" {
  description = "The ARN of the Lambda execution role"
  type        = string
}

variable "s3_bucket_name" {
  description = "The S3 bucket to store Flask Lambda function code"
  type        = string
}

variable "flask_s3_bucket_name" {
  description = "The S3 bucket to store the public index html and static files"
  type        = string
  
}
variable "flask_lambda_s3_key" {
  description = "The S3 key for the Flask Lambda function code"
  type        = string
}

variable "flask_lambda_s3_bucket_id" {
  description = "The S3 ID for the Flask Lambda function code"
  type        = string
  
}

variable "api_gateway_url" {
  description = "The URL of the API Gateway"
  type        = string
}

variable "sns_topic_arn" {
  description = "The ARN of the SNS topic"
  type        = string
}

variable "common_tags" {
  description = "A map of tags to assign to the resources"
  type        = map(string)
}


