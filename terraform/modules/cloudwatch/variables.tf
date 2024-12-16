variable "lambda_function_name" {
  description = "The name of the Lambda function."
  type        = string
}

variable "api_gateway_id" {
  description = "The API gateway ID."
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources in the module"
  type        = map(string)
}