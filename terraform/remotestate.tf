terraform {
  backend "s3" {
    key = "sns-topic-validator/terraform.tfstate"
  }
}

