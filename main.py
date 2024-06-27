import boto3, os, json, requests

ssm = boto3.client('ssm')
cloudwatch = boto3.client('logs')


def queryLogGroup(log_group_to_scan_):
    log_group_to_scan_ = str(log_group_to_scan_).replace("(", "")
    log_group_to_scan_ = str(log_group_to_scan_).replace(")", "")
    log_group_to_scan_ = str(log_group_to_scan_).replace("(", "")
    log_group_to_scan_ = str(log_group_to_scan_).replace("'", "")
    log_group_to_scan_ = str(log_group_to_scan_).strip()
    log_group_to_scan_list = log_group_to_scan_.split(',')
    log_events_arr = list()

    try:
        print('Size of log_group_to_scan_list=', len(log_group_to_scan_list))
        for log_group_to_scan in log_group_to_scan_list:
            if log_group_to_scan:
                logstream_name_arr = list()
                logstream_name_ = ''
                response = cloudwatch.describe_log_streams(logGroupName=log_group_to_scan.strip(),
                                                           descending=False)

                print('Size of len(response[logStreams])={} in Log Group {}'.format(len(response['logStreams']),
                                                                                    log_group_to_scan))
                for logstream in response['logStreams']:
                    if logstream:
                        logstream_name = logstream["logStreamName"]
                        logstream_name_arr.append(logstream_name.strip())

                for logstream_name in logstream_name_arr:
                    if logstream_name:
                        logstream_name_ = logstream_name
                        try:
                            log_events = cloudwatch.get_log_events(
                                logGroupName=log_group_to_scan,
                                logStreamName=logstream_name,
                                limit=1
                            )
                            if log_events:
                                print('logstream_name={} log_events={}'.format(logstream_name, log_events))
                                log_events_arr.append(log_events)
                        except Exception as e:
                            print('Exception: {} , logstream_name = {}'.format(e, logstream_name_))

                print('log_events_arr length=', len(log_events_arr))

    except Exception as e:
        print(e)

    print('len(log_events_arr) before return statement=', len(log_events_arr))
    return json.dumps(log_events_arr)


def lambda_handler(event, context):
    # To be retrieved from Parameter Store
    HEC_TOKEN = ssm.get_parameter(Name=os.environ['HEC_TOKEN'])['Parameter']['Value']
    print('HEC_TOKEN=', HEC_TOKEN)
    headers = {"Authorization": "Splunk %s" % HEC_TOKEN}

    HEC_URL = ssm.get_parameter(Name=os.environ['HEC_URL'])['Parameter']['Value']
    print('HEC_URL=', HEC_URL)
    LOG_GROUP_TO_SCAN = ssm.get_parameter(Name=os.environ['LOG_GROUP_TO_SCAN'])['Parameter']['Value']
    print('LOG_GROUP_TO_SCAN=', LOG_GROUP_TO_SCAN)

    try:
        print('About to print found events:')
        cw_events = queryLogGroup(str(LOG_GROUP_TO_SCAN))
        print(cw_events)

    except Exception as e:
        print(e)

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