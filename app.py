from chalice import Chalice
import boto3
import logging

app = Chalice(app_name='aws_bedtime')
app.debug = True
app.log.setLevel(logging.DEBUG)

ec2 = boto3.client('ec2')
rds = boto3.client('rds')

ACCOUNT_ID = boto3.client('sts').get_caller_identity().get('Account')
REGION = boto3.session.Session().region_name


def get_ec2_instances():
    """Return a list of EC2 instance ids which aren't tagged with KeepAwake"""
    instances = [i for instance_list in
                 [x['Instances'] for x in ec2.describe_instances()['Reservations']]
                 for i in instance_list]
    app.log.debug('Got some instances')
    return [x['InstanceId'] for x in instances
            if sum([(i['Key'] == 'KeepAwake') for i in x['Tags']]) == 0]


def get_rds_instances():
    """Return a list of RDS instance ids which aren't tagged with KeepAwake"""
    instances = rds.describe_db_instances()['DBInstances']
    app.log.debug('Got some instances')
    app.log.debug(instances)
    untagged = [x['DBInstanceIdentifier'] for x in instances
                if sum([(i['Key'] == 'KeepAwake') for i in
                        rds.list_tags_for_resource(
                            ResourceName=f'arn:aws:rds:{REGION}:{ACCOUNT_ID}:db:{x["DBInstanceIdentifier"]}'
                         )['TagList']]) == 0]
    return untagged


def ec2_stop(event, context):
    """Stop the instances, return/log the name of each instance shut down"""
    instances = get_ec2_instances()
    app.log.debug('Attempting to stop the instances...')
    ec2.stop_instances(InstanceIds=instances)
    text = 'Stopped instances with the following IDs:' + '\t'.join(instances)
    app.log.debug(text)
    return text


def ec2_start(event, context):
    """Start the instances, return/log the name of each instance shut down"""
    instances = get_ec2_instances()
    app.log.debug('Attempting to start the instances...')
    ec2.start_instances(InstanceIds=instances)
    text = 'Started instances with the following IDs:' + '\t'.join(instances)
    app.log.debug(text)
    return text


def rds_stop(event, context):
    """Stop the RDS instances, log the name of each instance shut down"""
    instances = get_rds_instances()
    app.log.debug('Untagged instances are: ' + " ".join(instances))
    app.log.debug('Attempting to stop the instances...')
    for instance_id in instances:
        rds.stop_db_instance(DBInstanceIdentifier=instance_id)
        app.log.debug(f'Stopped instance with the ID: {instance_id}')
    return


def rds_start(event, context):
    """Start the RDS instances, log the name of each instance shut down"""
    instances = get_rds_instances()
    app.log.debug('Untagged instances are: ' + " ".join(instances))
    app.log.debug('Attempting to start the instances...')
    for instance_id in instances:
        rds.start_db_instance(DBInstanceIdentifier=instance_id)
        app.log.debug(f'Started instance with the ID: {instance_id}')
    return


@app.schedule('cron(0 22 ? * MON-FRI *)')
def ec2_stop_scheduled(event, context=None):
    """Stop instances at 10 p.m. Monday through Friday"""
    return ec2_stop(event, context)


@app.schedule('cron(0 6 ? * MON-FRI *)')
def ec2_start_scheduled(event, context=None):
    """Start the instances at 6 a.m. Monday through Friday"""
    return ec2_start(event, context)


@app.lambda_function()
def ec2_stop_manual(event, context):
    """
    Use this when running the lambda from the command line using `aws lambda invoke`.
    Mostly for debugging.
    The reason we need to split off the scheduled version from the actual stoppping of the ec2 resources is because
    of the `context` parameter - a different context is provided when running from the command line compared to being
    triggered by a CloudWatch event.
    """
    app.log.debug('Executing a manual stop')
    return ec2_stop(event, context)


@app.lambda_function()
def ec2_start_manual(event, context):
    """
    Use this when running the lambda from the command line using `aws lambda invoke`.
    Mostly for debugging.
    The reason we need to split off the scheduled version from the actual stoppping of the ec2 resources is because
    of the `context` parameter - a different context is provided when running from the command line compared to being
    triggered by a CloudWatch event.
    """
    app.log.debug('Executing a manual start')
    return ec2_start(event, context)


@app.schedule('cron(0 22 ? * MON-FRI *)')
def rds_stop_scheduled(event, context=None):
    """Stop instances at 10 p.m. Monday through Friday"""
    return rds_stop(event, context)


@app.schedule('cron(0 6 ? * MON-FRI *)')
def rds_start_scheduled(event, context=None):
    """Start the instances at 6 a.m. Monday through Friday"""
    return rds_start(event, context)


@app.lambda_function()
def rds_stop_manual(event, context):
    """
    Use this when running the lambda from the command line using `aws lambda invoke`.
    Mostly for debugging.
    """
    app.log.debug('Executing a manual stop')
    return rds_stop(event, context)


@app.lambda_function()
def rds_start_manual(event, context):
    """
    Use this when running the lambda from the command line using `aws lambda invoke`.
    Mostly for debugging.
    """
    app.log.debug('Executing a manual start')
    return rds_start(event, context)
