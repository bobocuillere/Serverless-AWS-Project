output "table_name" {
  value = aws_dynamodb_table.table.name
}

output "answers_table_name" {
  value = aws_dynamodb_table.answers_table.name
}
