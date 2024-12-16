resource "aws_cognito_user_pool" "user_pool" {
  name = var.user_pool_name
  tags = var.common_tags
}

resource "aws_cognito_user_pool_client" "client" {
  name         = var.user_pool_client_name
  user_pool_id = aws_cognito_user_pool.user_pool.id

  # Enable USER_PASSWORD_AUTH flow
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
  
}

