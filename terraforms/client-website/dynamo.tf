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

resource "aws_dynamodb_table" "msg-dynamodb-table" {
  name           = "PiMessages"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "id"
  range_key      = "createdOn"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "createdOn"
    type = "S"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  }

  tags = {
    Name        = "PiMessages"
    Environment = "home-surveillance"
  }
}

resource "aws_dynamodb_table" "notification-dynamodb-table" {
  name           = "PiNotification"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "id"
  range_key      = "createdOn"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "createdOn"
    type = "S"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  }

  tags = {
    Name        = "PiNotification"
    Environment = "home-surveillance"
  }
}