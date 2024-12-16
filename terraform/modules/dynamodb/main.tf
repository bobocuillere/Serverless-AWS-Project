resource "aws_dynamodb_table" "table" {
  name           = var.table_name
  billing_mode   = "PROVISIONED"
  read_capacity  = var.read_capacity
  write_capacity = var.write_capacity
  hash_key       = var.hash_key

  attribute {
    name = var.hash_key
    type = var.hash_key_type
  }

  tags = var.common_tags
}

resource "aws_dynamodb_table" "answers_table" {
  name           = var.answers_table_name
  billing_mode   = "PROVISIONED" # or "PAY_PER_REQUEST" if you prefer on-demand billing
  read_capacity  = var.read_capacity
  write_capacity = var.write_capacity
  hash_key       = var.hash_key

  # Attribute definitions
  attribute {
    name = var.hash_key          
    type = var.hash_key_type  
  }

  attribute {
    name = "survey_id"
    type = "S"                  
  }

  # Global Secondary Indexes
  global_secondary_index {
    name            = "survey_id-index"
    hash_key        = "survey_id"
    projection_type = "ALL"      # Projects all attributes to the index

    read_capacity  = var.gsi_read_capacity
    write_capacity = var.gsi_write_capacity
  }

  tags = var.common_tags
}


