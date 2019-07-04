# Arbot

Sign up for workouts automatically.

## Usage
1. deply
    1. clone repository: `git clone https://github.com/orrshilon/arbot.git`
    1. download requirements: `pip install -r requirements.txt` 
    1. [package requirements](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#python-package-dependencies)
    1. [deploy to AWS Labmda] (https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#python-package-codeonly)
1. schedule
    1. create a new schedule on [CloudWatch Event Scheduling](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/RunLambdaSchedule.html)
    1. choose your lambda function
    1. for the input choose JSON text and enter something like: `{"target_workouts": ["יוגה"], "delta": 24, "max_delta": 1}`
    1. for the cron enter something like: `0,1,30,31 9,10,11 ? * FRI *`. * the cron expression is in UTC
 
