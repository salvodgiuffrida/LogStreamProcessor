# LogStreamProcessor
An AWS Lambda application, written in Python, that notifies by e-mail when a specified pattern (e.g. ERROR) is found in one of the log stream of the 2 specified log groups.
Addresses the limitations of CloudWatch alerts notifications, that don't contain any detail about what triggered the alert.

To avoid spamming with e-mails for the same pattern, the application used a DynamoDB table to deduplicate the notifications and avoid duplicate e-mails for the same pattern over a certain period of time.
The dedup behavior can be configured through some parameters specified at stack creation:
- DedupWindowSeconds: The number of seconds for which the deduplication should be active. After this time, the same pattern will trigger a new notification.

The application is deployed using AWS SAM (Serverless Application Model) and uses the following AWS services:
- Lambda
- DynamoDB
- CloudWatch Logs
- SNS

## Structure
- logstreamprocessor - Code for the application's Lambda function, written in Python.
- events - Invocation events that you can use to invoke the function locally.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources and can be used with SAM to deploy a self-contained stack in an AWS account.

## Deploy the application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

You may need the following for local testing.
* [Python 3 installed](https://www.python.org/downloads/)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

The first command will build a directory containing the code of the Lambda and the required dependencies, under ```.aws-sam.```
The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Parameter Email**: The e-mail address to which you want to receive the notifications.
* **Parameter LogGroupName1**: The name of the first log group to monitor.
* **Parameter LogGroupName2**: The name of the second log group to monitor.
* **Parameter Pattern**: The pattern to look for in the log streams of the 2 log groups.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

After the ```sam deploy``` command will finish, you will receive an email to the email address you specified at command execution, asking you to confirm the SNS subscription.
Remember to open the email and click the link, otherwise you won't be notified!

## Use the SAM CLI to build and test locally

Build your application with the `sam build` command.

```bash
LogStreamProcessor$ sam build
```

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
LogStreamProcessor$ sam local invoke LogStreamProcessorFunction --event events/event.json
```

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
LogStreamProcessor$ sam logs -n LogStreamProcessor --stack-name LogStreamProcessor --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests from your local machine.

```bash
LogStreamProcessor$ pip install pytest pytest-mock --user
LogStreamProcessor$ python -m pytest tests/ -v
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name LogStreamProcessor
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)

## License Summary
The project is released with the GPL-3.0 license. See the LICENSE file for the full license text.

## Buy me a coffee
If you like this project, please consider buying me a coffee. Thanks!
https://www.buymeacoffee.com/sgiuffrida