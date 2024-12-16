resource "aws_s3_bucket" "bucket" {
  bucket = var.s3_bucket_name
  tags   = var.common_tags
}

resource "aws_s3_bucket" "flask_bucket" {
  bucket = var.flask_s3_bucket_name

  tags = var.common_tags
}

resource "aws_s3_bucket_public_access_block" "flask_bucket_public_access" {
  bucket = aws_s3_bucket.flask_bucket.id

  block_public_acls   = false
  block_public_policy = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "flask_bucket_website" {
  bucket = aws_s3_bucket.flask_bucket.id

  index_document {
    suffix = "index.html"
  }

}

resource "aws_s3_bucket_ownership_controls" "flask_bucket_ownership" {
  bucket = aws_s3_bucket.flask_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "flash_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.flask_bucket_ownership,
    aws_s3_bucket_public_access_block.flask_bucket_public_access, 
  ]

  bucket = aws_s3_bucket.flask_bucket.id
  acl    = "public-read"
}

resource "aws_s3_bucket_policy" "flask_bucket_policy" {
  bucket = aws_s3_bucket.flask_bucket.id

  depends_on = [
    aws_s3_bucket_public_access_block.flask_bucket_public_access,
    aws_s3_bucket_acl.flash_bucket_acl
  ]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "arn:aws:s3:::${aws_s3_bucket.flask_bucket.bucket}/*"
      },
    ]
  })
}