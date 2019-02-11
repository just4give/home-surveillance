variable route53_zone_id {
    default="Z1FF1VZ7X78KL4"
}

variable domain {
    default="hss.crazykoder.com"
}

variable "certificate" {
  default="arn:aws:acm:us-east-1:027378352884:certificate/246f67fe-7e17-4e12-a64a-68c7def75575"
}

variable "dynamo_ngrok" {
  default="PiNgRok"
}

variable "dynamo_faces" {
  default="PiFaces"
}

variable "s3slack" {
  default="home-surveillance-hss-slack"
}

variable "s3faces" {
  default="home-surveillance-hss-faces"
}