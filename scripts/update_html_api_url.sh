#!/bin/bash

# Retrieve the API Gateway URL from the environment variable provided by Terraform
api_url="$API_URL"
echo "Retrieved API URL from environment variable: $api_url"

# Check if the API URL is empty
if [[ -z "$api_url" ]]; then
    echo "Error: API URL is empty. Ensure API_URL is correctly set."
    exit 1
fi

# Escape special characters in the API URL for use in sed
escaped_api_url=$(printf '%s\n' "$api_url" | sed -e 's/[\/&]/\\&/g')

# Define HTML files and their corresponding S3 buckets
html_path="../terraform/modules/frontend/flask_function/package/templates"
index_file="../terraform/modules/frontend/flask_function/templates/index.html"
other_files=("$html_path/dashboard.html" "$html_path/create_survey.html" "$html_path/register.html" "$html_path/survey.html")

# Define S3 bucket names
index_bucket="flask-survey-ui"
other_bucket="serveless-survey" # Or use Terraform output if needed

# Update the apiBaseUrl in index.html
if [[ -f $index_file ]]; then
    sed -i "s|const apiBaseUrl = '.*';|const apiBaseUrl = '$escaped_api_url';|g" "$index_file"
    echo "Updated API URL in $index_file"
else
    echo "File $index_file does not exist."
fi

# Update the apiBaseUrl in other HTML files
for file in "${other_files[@]}"; do
    if [[ -f $file ]]; then
        sed -i "s|const apiBaseUrl = '.*';|const apiBaseUrl = '$escaped_api_url';|g" "$file"
        echo "Updated API URL in $file"
    else
        echo "File $file does not exist."
    fi
done

# Upload the updated files to S3
aws s3 cp "$index_file" "s3://$index_bucket/$(basename $index_file)"
for file in "${other_files[@]}"; do
    if [[ -f $file ]]; then
        aws s3 cp "$file" "s3://$other_bucket/$(basename $file)"
    fi
done
