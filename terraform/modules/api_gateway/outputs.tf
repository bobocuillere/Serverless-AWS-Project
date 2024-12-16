output "api_id" {
  value = aws_api_gateway_rest_api.api.id
}

output "api_gateway_endpoint" {
  value = aws_api_gateway_rest_api.api.execution_arn
}
