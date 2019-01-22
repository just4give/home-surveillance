terraform {
  backend "s3" {
    bucket = "tf-backend-state-md"
    key    = "homesurveillance/cloudfront/cosumerwebsite.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "application_name" {
  description = "Name of your application"
  default     = "homesurveillance-client-website"
}

variable "application_description" {
  description = "Description of your application"
  default     = "homesurveillance client website"
}

variable "application_env" {
  description = "Environment of your application"
  default     = "prod"
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["arn:aws:s3:::${var.application_name}.${var.application_env}/*"]

    principals {
      type        = "AWS"
      identifiers = ["${aws_cloudfront_origin_access_identity.origin_access_identity.iam_arn}"]
    }
  }
}

resource "aws_s3_bucket" "bucket" {
  bucket = "${var.application_name}.${var.application_env}"
  acl    = "private"
  policy = "${data.aws_iam_policy_document.s3_policy.json}"

  tags {
    Name = "${var.application_name} ${var.application_env} bucket"
  }

  versioning {
    enabled = false
  }
}

resource "aws_s3_bucket" "logbucket" {
  bucket = "logs.${var.application_name}.${var.application_env}"
  acl    = "private"

  tags {
    Name = "${var.application_name} ${var.application_env} log bucket"
  }

  versioning {
    enabled = false
  }
}

resource "aws_cloudfront_origin_access_identity" "origin_access_identity" {
  comment = "Cloudfront access origin identity for ${var.application_name}.${var.application_env}"
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  depends_on = [
    "aws_s3_bucket.bucket",
    "aws_s3_bucket.logbucket",
  ]

  origin {
    domain_name = "${aws_s3_bucket.bucket.bucket_domain_name}"
    origin_id   = "myS3Origin"

    s3_origin_config {
      origin_access_identity = "${aws_cloudfront_origin_access_identity.origin_access_identity.cloudfront_access_identity_path}"
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Terraformed Cloudfront for ${var.application_name} ${var.application_env}"
  default_root_object = "index.html"

  logging_config {
    include_cookies = false
    bucket          = "${aws_s3_bucket.logbucket.bucket_domain_name}"
    prefix          = "logs/"
  }

  aliases = ["${var.domain}"]

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "myS3Origin"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "https-only"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  # Cache behavior with precedence 0
  ordered_cache_behavior {
    path_pattern     = "/content/immutable/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "myS3Origin"

    forwarded_values {
      query_string = false
      headers      = ["Origin"]

      cookies {
        forward = "none"
      }
    }

    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    compress               = true
    viewer_protocol_policy = "https-only"
  }

  # Cache behavior with precedence 1
  ordered_cache_behavior {
    path_pattern     = "/content/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "myS3Origin"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
    viewer_protocol_policy = "https-only"
  }

  price_class = "PriceClass_All"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  custom_error_response {
    error_code            = "404"
    error_caching_min_ttl = "300"
    response_code         = "200"
    response_page_path    = "/index.html"
  }

  custom_error_response {
    error_code            = "403"
    error_caching_min_ttl = "300"
    response_code         = "200"
    response_page_path    = "/index.html"
  }

  tags {
    Environment = "${var.application_env}"
  }

  viewer_certificate {
    cloudfront_default_certificate = false
    acm_certificate_arn            = "${var.certificate}"
    ssl_support_method             = "sni-only"
  }
}

################################################################################################################
## Create a Route53 ALIAS record to the Cloudfront website distribution
################################################################################################################
resource "aws_route53_record" "web" {
  zone_id = "${var.route53_zone_id}"
  name    = "${var.domain}"
  type    = "A"

  alias {
    name                   = "${aws_cloudfront_distribution.s3_distribution.domain_name}"
    zone_id                = "${aws_cloudfront_distribution.s3_distribution.hosted_zone_id}"
    evaluate_target_health = false
  }
}


output "domain_name" {
  value = "${aws_cloudfront_distribution.s3_distribution.domain_name}"
}

output "hosted_zone_id" {
  value = "${aws_cloudfront_distribution.s3_distribution.hosted_zone_id}"
}

output "cloudfront_id" {
  value = "${aws_cloudfront_distribution.s3_distribution.id}"
}
