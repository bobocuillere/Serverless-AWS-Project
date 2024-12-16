variable "user_pool_name" {
  description = "The name of the Cognito user pool"
  type        = string
}

variable "user_pool_client_name" {
  description = "The name of the Cognito user pool client"
  type        = string
}

variable "common_tags" {
  description = "A map of tags to assign to the resources"
  type        = map(string)
}
