resource "aws_dynamodb_table" "ngrok-dynamodb-table" {
  name           = "${var.dynamo_ngrok}"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "deviceId"

  attribute {
    name = "deviceId"
    type = "S"
  }

  

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  }

 

  tags = {
    Name        = "${var.dynamo_ngrok}"
    Environment = "home-surveillance"
  }
}


resource "aws_dynamodb_table" "faces-dynamodb-table" {
  name           = "${var.dynamo_faces}"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "faceId"

  attribute {
    name = "faceId"
    type = "S"
  }

  

  

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  }

 

  tags = {
    Name        = "${var.dynamo_faces}"
    Environment = "home-surveillance"
  }
}