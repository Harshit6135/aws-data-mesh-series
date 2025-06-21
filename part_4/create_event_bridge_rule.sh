#!/bin/bash
# This script sets up an EventBridge rule to capture GetDataAccess events from Lake Formation

# Event Pattern which captures GetDataAccess events from Lake Formation
cat > event_pattern.json << EOF
{
  "source": ["aws.lakeformation"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventSource": ["lakeformation.amazonaws.com"],
    "eventName": ["GetDataAccess"]
  }
}
EOF


# Create log group to store our GetDataAccess events
aws logs create-log-group --log-group-name /aws/events/datamesh_access_log_group

# Create EventBridge rule to capture GetDataAccess events
aws events put-rule \
  --name DataMeshAccessRule \
  --event-pattern file://event_pattern.json \
  --state ENABLED_WITH_ALL_CLOUDTRAIL_MANAGEMENT_EVENTS

# Create a CloudWatch Logs target for the EventBridge rule
aws events put-targets \
  --rule DataMeshAccessRule \
  --targets "Id"="DataMeshAccessLogGroup","Arn"="arn:aws:logs:us-east-1:781461006318:log-group:/aws/events/datamesh_access_log_group"
            # Replace <region> and <account-id> with your AWS region and account ID

# Wait for a few seconds to ensure the rule is created before adding permissions
sleep 5

# Add permissions to allow EventBridge to write to the CloudWatch Logs group
aws logs put-resource-policy \
  --policy-name "AllowEventBridgeWrite" \
  --policy-document '{
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
                "Resource": "arn:aws:logs:us-east-1:781461006318:log-group:/aws/events/datamesh_access_log_group:*"
            }
        ]
    }'

# Clean up the event pattern file
rm event_pattern.json

