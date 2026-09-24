import * as cdk from 'aws-cdk-lib';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as cloudwatchActions from 'aws-cdk-lib/aws-cloudwatch-actions';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import { Construct } from 'constructs';

import { ENVIRONMENT } from './Environment';
import { NodeJsLambda } from './NodeJsLambda';

const ENDPOINT_URL = 'https://runyourdinner.eu/rest/frontend/v1/runningdinner';

export class UptimeMonitorStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const monitor = new NodeJsLambda(this, 'uptime-monitor', {
      name: `uptime-monitor-${ENVIRONMENT.stage}`,
      packageFolderName: 'uptime-monitor',
      memorySize: 128,
      timeout: cdk.Duration.seconds(40),
      environment: {
        ENDPOINT_URL,
        REQUEST_TIMEOUT_MS: '20000',
      },
    });

    const schedule = new events.Rule(this, 'uptime-monitor-schedule', {
      ruleName: `uptime-monitor-${ENVIRONMENT.stage}`,
      description: 'Checks the public API endpoint every two hours',
      schedule: events.Schedule.rate(cdk.Duration.hours(2)),
    });
    schedule.addTarget(new targets.LambdaFunction(monitor.lambdaFunction));

    const alarmTopic = new sns.Topic(this, 'uptime-monitor-alerts', {
      topicName: `uptime-monitor-alerts-${ENVIRONMENT.stage}`,
      displayName: `Uptime monitor ${ENVIRONMENT.stage}`,
    });
    const notificationEmail = ENVIRONMENT.sns.notificationEmail;
    if (notificationEmail) {
      alarmTopic.addSubscription(new subscriptions.EmailSubscription(notificationEmail));
    }

    const alarm = new cloudwatch.Alarm(this, 'uptime-monitor-alarm', {
      alarmName: `uptime-monitor-failed-${ENVIRONMENT.stage}`,
      alarmDescription: `The public endpoint ${ENDPOINT_URL} returned a non-2xx response or could not be reached`,
      metric: monitor.lambdaFunction.metricErrors({
        period: cdk.Duration.minutes(5),
        statistic: 'Sum',
      }),
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
    });
    alarm.addAlarmAction(new cloudwatchActions.SnsAction(alarmTopic));
  }
}
