resource "aws_api_gateway_rest_api" "api" {
  name        = var.api_name
  description = var.api_description

  tags = var.common_tags
}

resource "aws_api_gateway_resource" "flask_proxy" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "flask"
}

resource "aws_api_gateway_resource" "flask_proxy_child" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.flask_proxy.id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "flask_proxy_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.flask_proxy_child.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "flask_lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.flask_proxy_child.id
  http_method = aws_api_gateway_method.flask_proxy_method.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.flask_lambda_invoke_arn
}

resource "aws_api_gateway_method" "flask_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.flask_proxy_child.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "flask_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.flask_proxy_child.id
  http_method = aws_api_gateway_method.flask_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "flask_options_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.flask_proxy_child.id
  http_method = aws_api_gateway_method.flask_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "flask_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.flask_proxy_child.id
  http_method = aws_api_gateway_method.flask_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,HEAD,OPTIONS,PATCH,POST,PUT,DELETE'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  response_templates = {
    "application/json" = ""
  }
  depends_on = [aws_api_gateway_integration.flask_options_integration]

}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeployment = timestamp()
  }

  depends_on = [
    aws_api_gateway_integration.flask_lambda_integration,
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.flask_options_integration,
    aws_api_gateway_integration_response.flask_options_integration_response,
    aws_api_gateway_integration_response.integration_response_200,
    aws_api_gateway_method.proxy,
    aws_api_gateway_method.flask_proxy_method,
    aws_api_gateway_method.flask_options,
    aws_api_gateway_method_response.method_response_200,
    aws_api_gateway_method_response.flask_options_200,
    aws_api_gateway_resource.proxy,
    aws_api_gateway_resource.flask_proxy,
    aws_api_gateway_resource.flask_proxy_child,

  ]
}

resource "null_resource" "update_html_files" {
  provisioner "local-exec" {
    environment = {
      API_URL = aws_api_gateway_stage.prod.invoke_url
    }
    command = "../scripts/update_html_api_url.sh"
  }
  
  depends_on = [
    aws_api_gateway_deployment.deployment,
    aws_api_gateway_stage.prod,
    aws_api_gateway_rest_api.api
  ]
}


resource "aws_api_gateway_stage" "prod" {
  stage_name    = "prod"
  rest_api_id   = aws_api_gateway_rest_api.api.id
  deployment_id = aws_api_gateway_deployment.deployment.id

  access_log_settings {
    destination_arn = var.cloudwatch_log_group_arn
    format = jsonencode({
      requestId : "$context.requestId",
      ip : "$context.identity.sourceIp",
      caller : "$context.identity.caller",
      user : "$context.identity.user",
    })
  }

  lifecycle {
    # Ensure the stage is replaced when the deployment changes
    replace_triggered_by = [
      aws_api_gateway_deployment.deployment,
    ]
  }
}

resource "aws_api_gateway_method_response" "method_response_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "integration_response_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy.http_method
  status_code = aws_api_gateway_method_response.method_response_200.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }

  depends_on = [
    aws_api_gateway_method_response.method_response_200,
    aws_api_gateway_integration.lambda
  ]
}

resource "aws_api_gateway_gateway_response" "default_4xx" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  response_type = "DEFAULT_4XX"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
  }
}

resource "aws_api_gateway_gateway_response" "default_5xx" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  response_type = "DEFAULT_5XX"

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
  }
}
