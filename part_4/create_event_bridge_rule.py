#!/usr/bin/env python3
"""
This script sets up an EventBridge rule to capture GetDataAccess events from Lake Formation
using the AWS boto3 SDK.
"""

import json
import boto3


# Event Pattern which captures GetDataAccess events from Lake Formation
event_pattern = {
        "source": ["aws.lakeformation"],
        "detail-type": ["AWS API Call via CloudTrail"],
        "detail": {
            "eventSource": ["lakeformation.amazonaws.com"],
            "eventName": ["GetDataAccess"]
        }
    }


# Create EventBridge rule to capture GetDataAccess events
events_client = boto3.client('events')
response = events_client.put_rule(
    Name="DataMeshAccessRule",
    EventPattern=json.dumps(event_pattern),
    State='ENABLED_WITH_ALL_CLOUDTRAIL_MANAGEMENT_EVENTS', #This state can only be used with CloudTrail management events
    Description='Captures GetDataAccess events from Lake Formation'
)


# Create log group to store our GetDataAccess events
logs_client = boto3.client('logs')
logs_client.create_log_group(logGroupName="/aws/events/datamesh_access_log_group")


# Create a CloudWatch Logs target for the EventBridge rule
events_client.put_targets(
    Rule="DataMeshAccessRule",
    Targets=[
        {
            'Id': 'DataMeshAccessLogGroup',
            'Arn': "arn:aws:logs:<region>:<account_id>:log-group:/aws/events/datamesh_access_log_group"
        }
    ]
)


# Add permissions to allow EventBridge to write to the CloudWatch Logs group
logs_client.put_resource_policy(
    policyName=policy_name,
    policyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "TrustEventsToStoreLogEvent",
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "events.amazonaws.com",
                        "delivery.logs.amazonaws.com"
                    ]
                },
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": f"arn:aws:logs:<region>:<account_id>:log-group:/aws/events/datamesh_access_log_group:*"
            }
        ]
    })
)