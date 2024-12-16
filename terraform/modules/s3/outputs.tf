output "s3_bucket_name" {
  value = aws_s3_bucket.bucket.bucket
}

output "flask_s3_bucket_name" {
  value = aws_s3_bucket.flask_bucket.bucket
  
}

output "flash_s3_bucket_id" {
  value = aws_s3_bucket.flask_bucket.id
  
}

output "flask_s3_bucket_url" {
  value = "http://${aws_s3_bucket.flask_bucket.bucket_regional_domain_name}"
}