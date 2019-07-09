# SNS Topic Validator

Validates that your SNS topics adhere to certain rules you may have, such as making sure all topics used for alerting operations staff have appropriate subscriptions.  Posts the results to a slack channel.  This is implemented as a Lambda function using the serverless framework.

## How It Works

Below is an example of `sns-assertions.json`, which defines the assertions that should be made on SNS topics found in the account. Only a single subscription can be checked per assertion, so break up multiple SubscriptionExists checks into different assertions. These assertion names will be included in failure messages.

*Ensure that you create a sns-assertions.json file like this and place it in the root of this repo before invoking or deploying, with whatever rules you want to validate for.*

```json
[
    {
        "AssertionName": "EnsureOpsAlertSubscribedToByOpsTeam",
        "TopicNameIncludes": "ops-alerts",
        "SubscriptionExists":
            {
            "Protocol": "email",
            "Endpoint": "opsteam@mycompany.com"
            }
    },
    {
        "AssertionName": "EnsureOpsSevereAlertSubscribedToByOpsTeam",
        "TopicNameIncludes": "ops-severe-alerts",
        "SubscriptionExists":
            {
            "Protocol": "email",
            "Endpoint": "opsteam@mycompany.com"
            }
    }
]
```

## Terraform

```bash
# pip install iam-starter
cd terraform
export AWS_ENV="dev"
export AWS_REGION="us-east-1"
export TF_STATE_REGION="us-east-1"
export TF_STATE_BUCKET="mycompany-tfstate-$AWS_ENV"
export TF_STATE_TABLE="tfstate_$AWS_ENV"

TF_DATA_DIR="./.$AWS_ENV-terraform/" iam-starter \
    --profile $AWS_ENV \
    --command \
        "terraform init \
        -backend-config=\"region=$TF_STATE_REGION\" \
        -backend-config=\"bucket=$TF_STATE_BUCKET\" \
        -backend-config=\"dynamodb_table=$TF_STATE_TABLE\" && \
        terraform apply \
        -var \"aws_env=$AWS_ENV\" \
        -var \"aws_region=$AWS_REGION\""
```

## Build

```bash
docker build -t sns-topic-validator .

# pip install iam-docker-run
iam-docker-run \
    --image sns-topic-validator \
    --host-source-path . \
    --container-source-path /src \
    -e AWS_DEFAULT_REGION=us-east-1 \
    -e LOG_LEVEL=info \
    --profile dev
```

## Invoke through Serverless Framework

```bash
# pip install iam-starter
LOG_LEVEL=INFO iam-starter \
    --role bt-role-ops-devops \
    --profile btdev \
    --command sls invoke local \
    -f sns-topic-validator
```

## Deploy

```bash
export DEPLOY_BUCKET="mycompany-deploy"

iam-docker-run \
    --image sns-topic-validator \
    --profile $AWS_ENV \
    --region $AWS_REGION \
    --full-entrypoint "sls deploy --deployBucket $DEPLOY_BUCKET"
```

