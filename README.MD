# bedtime
A Chalice app to turn off AWS dev resources at night and on weekends

--------

## Deployment
- Create a Python 3.7 virtual environment somewhere (the `.gitignore` is already set up to ignore `/venv/` in the
  project directory, so you can put it there).
  - This project was developed with Python 3.7 - 3.6 might work, but if you want to be safe, use 3.7
- Activate the virtual environment, and then install Chalice with `pip install chalice`
- I think you also need to install the requirements, so run `pip install -r requirements.txt`
- After all that, you're ready to deploy, I think. You'll need to pass the credentials of your AWS account to Chalice,
  so if you use the fantastic [aws-vault](https://github.com/99designs/aws-vault) the command would look something
  like:

```
aws-vault exec AWS_ENV_NAME -- chalice deploy
```

That should all work, hopefully.

## Usage

It's a Lambda running on a schedule, so you don't do anything to use it. Sit back and relax!

However, if you want to trigger the shut down/start up of the resources manually (e.g. to check if you've tagged your
resources correctly), you can use the manual lambdas:
- `aws_bedtime-dev-ec2_start_manual`
- `aws_bedtime-dev-ec2_stop_manual`
- `aws_bedtime-dev-rds_start_manual`
- `aws_bedtime-dev-rds_stop_manual`

(Sorry about the mix of dashes and underscores - Chalice prefers dashes when it comes to automatically naming Lambdas.)

To run this, you will need to use `aws lambda invoke` with your AWS credentials supplied. Again, using `aws-vault`:
```
aws-vault exec AWS_ENV_NAME -- aws lambda invoke --function-name aws_bedtime-dev-ec2_start_manual /tmp/lambda.out
```
to start all the EC2 instances not tagged with the `KeepAwake` tag.

## TODO

- Change the config so that we don't have this "dev" environment name all around the lambdas...
- Add more resource types/services to the list of stuff being shut down
- Put the functions for different services in different files for readability
- (Far-off) find a way to let the user choose which services to enable Bedtime for, if they only want it active for EC2
  etc.
