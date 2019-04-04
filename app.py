from chalice import Chalice
import boto3

app = Chalice(app_name='aws_bedtime')
app.debug = True

ec2 = boto3.client('ec2')


def get_ec2_instances():
    """Return a list of instances which aren't tagged with KeepAlive and are active"""
    instances = ec2.describe_instances(InstanceIds=[])['Reservations'][0]['Instances']
    app.log.debug('Got some instances')
    return [x for x in instances
            if sum([(i['Key'] == 'KeepAlive') for i in x['Tags']]) == 0]


@app.schedule('cron(0 22 ? * MON-FRI)')
def ec2_stop(event):
    """Stop the instances, return/log the name of each instance shut down"""
    instances = get_ec2_instances()
    ids = [i['InstanceId'] for i in instances]
    ec2.stop_instances(InstanceIds=ids)
    text = 'Stopped instances with the following IDs:\n' + '\t\n'.join(ids)
    app.log.debug(text)
    return text


@app.schedule('cron(0 6 ? * MON-FRI)')
def ec2_start(event):
    """Start the instances, return/log the name of each instance shut down"""
    instances = get_ec2_instances()
    ids = [i['InstanceId'] for i in instances]
    ec2.stop_instances(InstanceIds=ids)
    text = 'Started instances with the following IDs:\n' + '\t\n'.join(ids)
    app.log.debug(text)
    return text


@app.schedule('cron(* * * * ?)')
def ec2_test(event):
    """Scheduled to run every minute, so you can test whether things are actually working"""
    ec2_stop(None)  # Comment out as necessary
    #ec2_start(None)  # Comment out as necessary
