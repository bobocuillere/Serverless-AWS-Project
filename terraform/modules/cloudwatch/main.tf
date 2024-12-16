resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14
  tags              = var.common_tags
}

resource "aws_cloudwatch_log_group" "api_gateway_log_group" {
  name = "/aws/apigateway/${var.api_gateway_id}"
  retention_in_days = 7

  tags = var.common_tags
}
