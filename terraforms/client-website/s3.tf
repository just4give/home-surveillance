resource "aws_s3_bucket" "bucket_faces" {
  bucket = "${var.s3faces}"
  acl    = "private"
  
  tags {
    Name = "${var.s3faces}"
  }

  versioning {
    enabled = false
  }
}

resource "aws_s3_bucket" "bucket_slack" {
  bucket = "${var.s3slack}"
  acl    = "private"
  
  tags {
    Name = "${var.s3slack}"
  }

  versioning {
    enabled = false
  }
}