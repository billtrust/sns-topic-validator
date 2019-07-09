variable "slack_webhook" {}
variable "max_items" {
  default = "10"
}

resource "aws_ssm_parameter" "SLACK_WEBHOOK_URL" {
  name = "/devops/sns-topic-validator/SLACK_WEBHOOK_URL"
  value = "${var.slack_webhook}"
  type = "SecureString"
  overwrite = true
  allowed_pattern = "^https:\\/\\/hooks.slack.com\\/services\\/[a-zA-Z0-9]*\\/[a-zA-Z0-9]*\\/[a-zA-Z0-9]*$"
}

resource "aws_ssm_parameter" "SLACK_MAX_ITEMS" {
  name = "/devops/sns-topic-validator/SLACK_MAX_ITEMS"
  value = "${var.max_items}"
  type = "String"
  overwrite = true
  allowed_pattern = "^[0-9]*$"
}
