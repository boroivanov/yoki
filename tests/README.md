# Testing setup

At the moment moto doesn't have the functionality required to support all the tests. I found it easier to just build a simple infra and test against that. The Cloudformation tests/infra-setup/ecs-cloudformation.yml will create bare minimum setup with a separate VPC, subnets, and ECS services.

## Running the tests.

1. Create a Cloudformation stack `test-yoki-infra` with the template from tests/infra-setup/ecs-cloudformation.yml
2. Switch to your python venv and deploy the app for testing with `sls deploy --stage test`.
3. Update the environment variables in tox.ini for:
    - DYNAMODB_TABLE_PREFIX
    - COGNITO_APP_CLIENT_ID
    - COGNITO_USERPOOL_ID
4. Upload two small docker images to the ECR repo created by the Cloudformation stack.
   - Images:
        - ${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/test-yoki:srv1
        - ${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/test-yoki:srv2
5. Run the tests from parent dir by executing `tox`