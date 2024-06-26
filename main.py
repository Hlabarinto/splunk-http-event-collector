import boto3, os, json, requests

ssm = boto3.client('ssm')
cloudwatch = boto3.client('logs')

def queryLogGroup():

    log_group_to_scan = "/aws/containerinsights/Reach-uat-eks-cluster/performance"
    logstream_name_arr = list()
    log_events_arr = list()

    try:

        response = cloudwatch.describe_log_streams(logGroupName=log_group_to_scan,
                                                   descending=False)

        for logstream in response['logStreams']:
            logstream_name = logstream["logStreamName"]
            logstream_name_arr.append(logstream_name)

        for logstream_name in logstream_name_arr:
            log_events = cloudwatch.get_log_events(
                logGroupName=log_group_to_scan,
                logStreamName=logstream_name,
                limit=1
            )
            print("logstream_name= ", log_group_to_scan + '/' + logstream_name)
            log_events_arr.append(log_events)

    except Exception as e:
        print(e)

    return json.dumps(log_events_arr)

def lambda_handler(event, context):

    #To be retrieved from Parameter Store
    HEC_TOKEN = ssm.get_parameter(Name=os.environ['HEC_TOKEN'])['Parameter']['Value'],
    print('HEC_TOKEN', HEC_TOKEN)
    HEC_URL = ssm.get_parameter(Name=os.environ['HEC_URL'])['Parameter']['Value']
    print('HEC_URL', HEC_URL)

    cw_events = queryLogGroup()
    print('About to print found events:')
    print(cw_events)

    headers = {"Authorization": "Splunk %s" % HEC_TOKEN}

    print('One')
    try:
        print('two')
        r = requests.post(HEC_URL, headers=headers, data=cw_events)
    except Exception as f:
        print('three')
        print('Exception: ', f)
        print(
            'Error code {} , Error message {}'.format(
                r.status_code, r.content))