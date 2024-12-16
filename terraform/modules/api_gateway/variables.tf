variable "api_name" {
  description = "The name of the API Gateway"
  type        = string
}

variable "api_description" {
  description = "The description of the API Gateway"
  type        = string
}

variable "flask_lambda_invoke_arn" {
  description = "The ARN to invoke the Flask Lambda function"
  type        = string
  
}

variable "lambda_function_name" {
  description = "The name of the Lambda function"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "The ARN to invoke the Lambda function"
  type        = string
}

variable "cloudwatch_log_group_arn" {
  description = "The ARN of the CloudWatch log group for API Gateway logs"
  type        = string
}

variable "common_tags" {
  description = "A map of tags to assign to the resources"
  type        = map(string)
}
