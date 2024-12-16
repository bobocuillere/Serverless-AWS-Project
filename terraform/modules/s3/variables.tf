variable "s3_bucket_name" {
  description = "The name of the S3 bucket."
  type        = string
}

variable "flask_s3_bucket_name" {
  description = "The name of the S3 bucket."
  type        = string
  
}
variable "common_tags" {
  description = "Common tags for all resources in the module"
  type        = map(string)
}