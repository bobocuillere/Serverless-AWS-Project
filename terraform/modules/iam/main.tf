data "aws_caller_identity" "current" {}

resource "random_string" "suffix" {
  length  = 8
  special = false
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.lambda_execution_role_name}-${random_string.suffix.result}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "lambda_execution_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "frontend_lambda_policy" {
  name   = "frontend_lambda_policy"
  role   = aws_iam_role.lambda_execution_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      # Add permission to invoke backend Lambda
      {
        Effect = "Allow",
        Action = "lambda:InvokeFunction",
        Resource = "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.backend_lambda_function_name}"
      }
    ]
  })
}

resource "aws_iam_policy" "dynamodb_policy" {
  name        = "dynamodb-access-policy"
  path        = "/"
  description = "Policy to allow Lambda functions to access DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem",
        ],
        Resource = [
          "arn:aws:dynamodb:${var.region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_table_name}",
          "arn:aws:dynamodb:${var.region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_table_name}/index/*",
          "arn:aws:dynamodb:${var.region}:${data.aws_caller_identity.current.account_id}:table/${var.answers_table_name}",
          "arn:aws:dynamodb:${var.region}:${data.aws_caller_identity.current.account_id}:table/${var.answers_table_name}/index/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "dynamodb_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.dynamodb_policy.arn
}

resource "aws_iam_role" "api_gateway_cloudwatch_role" {
  name = "api-gateway-cloudwatch-role-${random_string.suffix.result}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement: [
      {
        Effect    = "Allow",
        Principal = {
          Service = "apigateway.amazonaws.com"
        },
        Action    = "sts:AssumeRole"
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_role_policy" "api_gateway_cloudwatch_policy" {
  name = "api-gateway-cloudwatch-policy-${random_string.suffix.result}"
  role = aws_iam_role.api_gateway_cloudwatch_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement: [
      {
        Effect   = "Allow",
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "api_gateway_role" {
  name = "api-gateway-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "apigateway.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "api_gateway_policy" {
  role       = aws_iam_role.api_gateway_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

resource "aws_iam_role_policy_attachment" "invoke_lambda_policy" {
  role       = aws_iam_role.api_gateway_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaExecute"
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution_policy" {
  role       = aws_iam_role.api_gateway_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "sns_publish_policy" {
  name        = "sns-publish-policy"
  description = "Policy to allow publishing to SNS topics"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "sns:Publish",
        Resource = "arn:aws:sns:${var.region}:${data.aws_caller_identity.current.account_id}:${var.topic_name}"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sns_publish_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name 
  policy_arn = aws_iam_policy.sns_publish_policy.arn
}

# New Cognito Admin Policy
resource "aws_iam_policy" "cognito_admin_policy" {
  name        = "cognito-admin-policy"
  path        = "/"
  description = "Policy to allow Lambda functions to perform admin actions on Cognito"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "cognito-idp:AdminConfirmSignUp",
          "cognito-idp:AdminGetUser",
          "cognito-idp:AdminInitiateAuth",
          "cognito-idp:AdminRespondToAuthChallenge",
          "cognito-idp:AdminUpdateUserAttributes"
        ],
        Resource = "arn:aws:cognito-idp:${var.region}:${data.aws_caller_identity.current.account_id}:userpool/${var.cognito_user_pool_id}"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "cognito_admin_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.cognito_admin_policy.arn
}

resource "aws_iam_policy" "s3_read_policy" {
  name        = "s3-read-policy"
  description = "Policy to allow Lambda functions to read from the S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject"

        ],
        Resource = [
          "arn:aws:s3:::${var.private_bucket_name}/*",
          "arn:aws:s3:::flask-survey-ui/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_read_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.s3_read_policy.arn
}
