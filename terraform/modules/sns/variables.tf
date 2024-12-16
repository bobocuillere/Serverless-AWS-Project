variable "topic_name" {
  description = "The name of the SNS topic."
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources in the module"
  type        = map(string)
}

variable "backend_lambda_function_arn" {
  description = "The ARN of the backend Lambda function"
  type        = string
  
}

variable "lambda_function_name" {
  description = "The name of the Lambda function"
  type        = string
  
}