output "lambda_execution_role_arn" {
  value = aws_iam_role.lambda_execution_role.arn
}

output "lambda_execution_role_name" {
  value = aws_iam_role.lambda_execution_role.name
}

output "iam_policy_attachment_arn" {
  value = aws_iam_role_policy_attachment.lambda_execution_policy.id
}

output "api_gateway_cloudwatch_role_arn" {
  value = aws_iam_role.api_gateway_cloudwatch_role.arn
}
