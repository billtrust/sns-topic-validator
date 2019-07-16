import os
import sns_topic_validator
from slack_webhook_post import post_to_slack


def generate_slack_message(validation_results, max_items):
    aws_env = os.environ.get('AWS_ENV', '(AWS_ENV not present)')
    fail_count = 0
    skipped = False
    slack_blocks = []
    for result in validation_results:
        if not result['Valid']:
            fail_count += 1
            for failed_assertion in result['FailedAssertions']:
                if len(slack_blocks) >= max_items:
                    skipped = True
                else:
                    missing_sub = failed_assertion["MissingSubscription"]
                    text = (f"*Topic Name:* "
                            f"{result['TopicArn'].split(':')[-1]}\n"
                            f"*Assertion Name:* "
                            f"{failed_assertion['AssertionName']}\n"
                            f"*Missing Subscription:* "
                            f"Protocol: {missing_sub['Protocol']}, "
                            f"Endpoint: {missing_sub['Endpoint']}"
                            )
                    slack_blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": text
                            }
                        }
                    )

    if skipped:
        slack_blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"And {fail_count - max_items} more..."
                }
            }
        )

    if fail_count == 0:
        return 0

    topic_noun = 'topics' if fail_count > 1 else 'topic'
    slack_headline = (
            f"*{fail_count} SNS {topic_noun} failed validation "
            f"in AWS_ENV: {aws_env}*"
            )
    slack_data = {
        "username": "SLA Topic Validator",
        "icon_emoji": ":space_invader:",
        "text": slack_headline,
        "attachments": [
            {
                "blocks": slack_blocks
            }
        ]
    }
    return slack_data


def main(event, context):
    print("SNS Topic Validator Starting ...")
    validation_results = (sns_topic_validator.
                          process_sns_assertions('sns-assertions.json'))
    slack_data = generate_slack_message(validation_results,
                                        int(os.environ['SLACK_MAX_ITEMS']))
    webhook_url = os.environ['SLACK_WEBHOOK_URL']
    if slack_data != 0:
        post_to_slack(webhook_url, slack_data)
    return "You're welcome"


if __name__ == '__main__':
    main(None, None)
