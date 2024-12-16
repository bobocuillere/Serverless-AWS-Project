variable "table_name" {
  description = "The name of the DynamoDB table"
  type        = string
}

variable "answers_table_name" {
  description = "The name of the DynamoDB answers table"
  type        = string
}

variable "hash_key" {
  description = "The name of the hash key"
  type        = string
}

variable "hash_key_type" {
  description = "The type of the hash key (S = string, N = number, B = binary)"
  type        = string
}

variable "read_capacity" {
  description = "The read capacity units for the DynamoDB table"
  type        = number
}

variable "write_capacity" {
  description = "The write capacity units for the DynamoDB table"
  type        = number
}

variable "gsi_read_capacity" {
  description = "Read capacity units for the GSI"
  default     = 5
}

variable "gsi_write_capacity" {
  description = "Write capacity units for the GSI"
  default     = 5
}

variable "common_tags" {
  description = "A map of tags to assign to the resources"
  type        = map(string)
}
