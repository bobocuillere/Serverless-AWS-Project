output "flask_function_name" {
  value = aws_lambda_function.flask_function.function_name
}

output "flask_function_invoke_arn" {
  value = aws_lambda_function.flask_function.invoke_arn
}
