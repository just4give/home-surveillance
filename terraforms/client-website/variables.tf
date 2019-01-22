variable route53_zone_id {
    default="xxxx"
}

variable domain {
    default="xxx.example.com"
}

variable "certificate" {
  default="arn:aws:acm:us-east-1:xxx:certificate/xxx"
}

variable "dynamo_ngrok" {
  default="PiNgRok"
}

variable "dynamo_faces" {
  default="PiFaces"
}

variable "s3slack" {
  default="xxxx-surveillance-hss-slack"
}

variable "s3faces" {
  default="xxxx-surveillance-hss-faces"
}