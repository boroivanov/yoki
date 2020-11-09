[![Build Status](https://travis-ci.org/boroivanov/yoki.svg)](https://travis-ci.org/boroivanov/yoki)
[![Maintainability](https://api.codeclimate.com/v1/badges/ae723a0073e47a34bd9d/maintainability)](https://codeclimate.com/github/boroivanov/yoki/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/ae723a0073e47a34bd9d/test_coverage)](https://codeclimate.com/github/boroivanov/yoki/test_coverage)

# Yōki 容器 (ECS API)

Yoki is a supplementary ECS API. The main goal is to provide information and functionality which is either not easily accessible or not available via the AWS API and console.

Yoki also comes bundled with a slack app. The app provides commands for deploying and scaling with auto-updating post messages.

Main features:
- easy deployments and scaling.
- service groups - deploy and scale a group of services at once.
- deployment release history.
- rollback a release.
- slack commands and notifications.
- auth via cognito user pools


# Installation

### API Installation
Yoki is a serverless app. The installation will create API GW, DynamoDB tables, Lambda functions, Cognito User Pool and IAM role with permission to those resources.

**Deploy the API**

```bash
# For your initial installation you should run all the commands below in the parent app dir.

# Create the environment variables files. The defaults are safe to use but change SLACK_CHANNEL or create that channel in your slack org.
cp .env.yml.example .env.yml

# Install Serverless
npm install -g serverless
npm install serverless-python-requirements
npm install serverless-wsgi

# Python virtual env
virtualenv -p `which python3` venv
source venv/bin/activate

# Deploy the app
sls deploy --stage prod
```


### Slack App Installation

You will need to manually create the slack app in your org. PLease follow the steps below.

1. Go to https://api.slack.com/apps and `Create New App`
2. Record the `Verification Token` from the Basic Information page.
3. Go to Slack Commands and create a new command called `/ecs`
    - Use the API GW endpoint from the serverless output as `Request URL` for the slack command
    - Ex: `Request URL` https://asdf1234.execute-api.us-east-1.amazonaws.com/prod/slack

    ![slackapp_slash_command](images/slackapp-slash-command.png?raw=true)

4. Go to OAuth & Permissions and grant the following permissions to the slack app:
    - channels:read
    - chat:write:bot
    - chat:write:user
    - incoming-webhook
    - commands
    - groups:read

5. Install the app and record the `OAuth Access Token` from the OAuth & Permissions near the top.
6. Update the .env.yml file and add `Verification Token` and `OAuth Access Token`
    ```bash
    $ cat .env.yml
    lambda:
    environment:
        ....
        SLACK_VERIFICATION_TOKEN: asdf1234asdf1234 # Verification Token (step 3)
        SLACK_TOKEN: xoxp-11111111111-1111111111111-1111111111111-abcd3abcd3abcd3abcd3abcd3abcd3123 # OAuth Access Token (step 4)
    ```
7. Update your api
    ```bash
    sls deploy --stage prod
    ```

# Examples

### Slack command examples

```yaml
/ecs help

/ecs deploy <cluster> <service> <docker_tag>

# Manage service groups
/ecs groups
/ecs groups mygroup srv1 srv2
/ecs groups mygroup -d

# Deploy to a group of services
/ecs group-deploy <cluster> <group> <tags>

# scale
/ecs scale <cluster> <service> <count>
/ecs group-scale <cluster> <groups> <count>

# List deployment history and/or rollback
/ecs rollback <cluster> <service>
```

![slackapp_message](images/slackapp-message.png?raw=true)


### API examples

```bash
# Auth
curl -XPOST -H 'Content-type: application/json' -d '{"username": "username@example.com", "password": "pass123"}' localhost:5000/auth


# Create service group
curl -XPOST -H 'Content-type: application/json' -H "$AUTH" -d '{"services": "srv1 srv2"}' localhost:5000/groups/group1
# List service groups
curl -H "$AUTH" localhost:5000/groups
curl -H "$AUTH" localhost:5000/groups/group1


# List Deployments
curl -H "$AUTH" localhost:5000/deployments
curl -H "$AUTH" localhost:5000/deployments/${deployment_id}
curl -H "$AUTH" localhost:5000/clusters/${cluster}/deployments
curl -H "$AUTH" localhost:5000/clusters/${cluster}/services/${service}/deployments


# Create deployment - single service
curl -H 'Content-type: application/json' -H "$AUTH" -d '{"tags": {"container_name": "docker_tag"}}' localhost:5000/clusters/${cluster}/services/${service}/deploy
# Create deployment - service group
curl -H 'Content-type: application/json' -H "$AUTH" -d '{"tags": {"container_name": "docker_tag"}}' localhost:5000/clusters/${cluster}/groups/${group}/deploy


# Scale - single service
curl -H 'Content-type: application/json' -H "$AUTH" -d '{"count": 1}' localhost:5000/clusters/${cluster}/services/${service}/scale
# Scale - service group
curl -H 'Content-type: application/json' -H "$AUTH" -d '{"count": 1}' localhost:5000/clusters/${cluster}/groups/${group}/scale

```
