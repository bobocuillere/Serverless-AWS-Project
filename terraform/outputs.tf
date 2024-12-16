output "api_gateway_url" {
  value = "https://${module.api_gateway.api_id}.execute-api.${var.region}.amazonaws.com/prod"
}

output "cloudwatch_log_group_name" {
  value = module.cloudwatch.cloudwatch_log_group_name
}

output "cognito_user_pool_client_id" {
  value = module.cognito.user_pool_client_id
}

output "cognito_user_pool_id" {
  value = module.cognito.user_pool_id
}

output "dynamodb_table_name" {
  value = module.dynamodb.table_name
}

output "answers_table_name" {
  value = module.dynamodb.answers_table_name
}

output "lambda_execution_role_arn" {
  value = module.iam.lambda_execution_role_arn
}

output "lambda_function_name" {
  value = module.lambda.lambda_function_name
}

output "s3_bucket_name" {
  value = module.s3.s3_bucket_name
}

output "sns_topic_arn" {
  value = module.sns.sns_topic_arn
}

output "api_gateway_cloudwatch_role_arn" {
  value = module.iam.api_gateway_cloudwatch_role_arn

}

output "flask_s3_bucket_url" {
  value = module.s3.flask_s3_bucket_url
  
}
