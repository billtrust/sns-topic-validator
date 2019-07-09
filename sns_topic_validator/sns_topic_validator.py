import os
import json
import boto3
import logging


logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def get_all_sns_topic_arns(token=None):
    '''Returns a list of all SNS topic ARN strings'''
    topics = []
    client = boto3.client('sns')
    kwargs = {}
    if token:
        kwargs['NextToken'] = token
    response = client.list_topics(**kwargs)
    for item in response['Topics']:
        topics.append(item['TopicArn'])
    if 'NextToken' in response:
        topics.extend(get_all_sns_topic_arns(response['NextToken']))
    return topics


def get_sns_topic_subscriptions(topic_arn, token=None):
    subscriptions = []
    client = boto3.client('sns')
    kwargs = {'TopicArn': topic_arn}
    if token:
        kwargs['NextToken'] = token
    try:
        response = client.list_subscriptions_by_topic(**kwargs)
        for subscription in response['Subscriptions']:
            subscriptions.append(subscription)
        if 'NextToken' in response:
            subscriptions.extend(
                    get_sns_topic_subscriptions(topic_arn,
                                                response['NextToken']
                                                ))
    except client.exceptions.NotFoundException:
        logger.info(f"{topic_arn} does not exist.")

    return subscriptions


def validate_sns_topic(topic_arn, topic_subscriptions, assertions):
    failed_assertions = []
    num_applicable_assertions = 0
    for assertion in assertions:
        process_assertion = True
        if 'TopicNameIncludes' in assertion:
            topic_name = topic_arn.split(':')[-1]
            if not assertion['TopicNameIncludes'] in topic_name:
                process_assertion = False
                logger.debug(
                        f"Topic {topic_name} does not match topic name "
                        "criteria for assertion {assertion['AssertionName']}"
                    )

        if process_assertion:
            num_applicable_assertions += 1
            assertion_satisfied = False
            for topic_sub in topic_subscriptions:
                # see if at least one subscription meets the assertion criteria
                sub_exists = assertion['SubscriptionExists']
                if topic_sub['Protocol'] == sub_exists['Protocol'] and \
                   topic_sub['Endpoint'] == sub_exists['Endpoint']:
                    assertion_satisfied = True
            if assertion_satisfied:
                logger.debug(
                        f"Topic {topic_name} passes assertion for "
                        "protocol {sub_exists['Protocol']}"
                        )
            else:
                failed_assertions.append(
                    {
                        'AssertionName': assertion['AssertionName'],
                        'MissingSubscription': assertion['SubscriptionExists']
                    }
                )

    return {
        'TopicArn': topic_arn,
        'Valid': len(failed_assertions) == 0,
        'NumApplicableAssertions': num_applicable_assertions,
        'FailedAssertions': failed_assertions
    }


def load_sns_assertions(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


def process_sns_assertions(assertions_filename):
    topic_arns = get_all_sns_topic_arns()
    logger.info("Loaded {} SNS topics".format(len(topic_arns)))

    assertions = load_sns_assertions(assertions_filename)
    logger.info("Loaded {} assertions".format(len(assertions)))

    all_validation_results = []
    for topic_arn in topic_arns:
        logger.debug(f"Entering topic {topic_arn}")
        subscriptions = get_sns_topic_subscriptions(topic_arn)
        topic_validation_result = validate_sns_topic(topic_arn, subscriptions,
                                                     assertions)
        logger.info("{} ({} matching assertions) - {}".format(
            'VALID' if topic_validation_result['Valid'] else '***INVALID***',
            topic_validation_result['NumApplicableAssertions'],
            topic_arn))
        # if not topic_validation_result['Valid']:
        #     logger.info(f"Failed assertions:\n"
        #                 "{topic_validation_result['FailedAssertions']}")
        all_validation_results.append(topic_validation_result)

    return all_validation_results
