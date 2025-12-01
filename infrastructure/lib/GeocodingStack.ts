import * as cdk from 'aws-cdk-lib';
import { AttributeType } from 'aws-cdk-lib/aws-dynamodb';
import { HttpMethod } from 'aws-cdk-lib/aws-lambda';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';

import { CommonUtils } from './CommonUtils';
import { ENVIRONMENT } from './Environment';
import { LocalDevUser } from './LocalDevUser';
import { NodeJsLambda } from './NodeJsLambda';

export interface GeocodingStackProps extends cdk.StackProps {
  localDevUser?: LocalDevUser;
}

export class GeocodingStack extends cdk.Stack {
  public readonly table: cdk.aws_dynamodb.Table;

  constructor(scope: Construct, id: string, props?: GeocodingStackProps) {
    super(scope, id, props);

    const geocodingRequestQueue = this.createSqsWithDLQ('geocoding-request')[0];

    const commonUtils = new CommonUtils(this);

    const geocodingResponseQueue = this.createSqsWithDLQ('geocoding-response')[0];

    // Create SQS-lambda and give access to the queues
    const geocodingFuncSqs = new NodeJsLambda(this, 'geocoding-sqs', {
      name: 'geocoding-sqs',
      packageFolderName: 'geocoding-sqs',
    });
    // Create HTTP-Lambda
    const geocodingFuncHttp = new NodeJsLambda(this, 'geocoding-http', {
      name: 'geocoding-http',
      packageFolderName: 'geocoding-http',
      addFunctionUrl: true,
      cors: this.corsForHttpMethods([HttpMethod.HEAD, HttpMethod.PUT]),
    });

    geocodingFuncSqs.lambdaFunction.addEventSource(
      new lambdaEventSources.SqsEventSource(geocodingRequestQueue, {
        batchSize: 3,
      }),
    );
    geocodingRequestQueue.grantConsumeMessages(geocodingFuncSqs.lambdaFunction);
    geocodingResponseQueue.grantSendMessages(geocodingFuncSqs.lambdaFunction);

    // Grant access to the SSM parameter store
    const policyStatementsSsm = commonUtils.allowParameterStoreAccess([geocodingFuncSqs.lambdaFunction, geocodingFuncHttp.lambdaFunction], '/runningdinner/googlemaps/*');

    this.table = this.createDynamoDbTable('runningdinner-v1');
    commonUtils.grantReadWriteDataToTable([geocodingFuncSqs.lambdaFunction, geocodingFuncHttp.lambdaFunction], this.table);

    // Create local dev response SQS queue if in dev stage
    if (ENVIRONMENT.isDevStage) {
      const geocodingResponseQueueLocalDev = this.createSqsWithDLQ('geocoding-response-local_dev')[0];

      geocodingResponseQueueLocalDev.grantSendMessages(geocodingFuncSqs.lambdaFunction);

      const localDevUser = props?.localDevUser;
      if (localDevUser) {
        localDevUser.grantSqsAccess([geocodingRequestQueue, geocodingResponseQueueLocalDev]);
        localDevUser.grantDynamoDbReadWriteData(this.table);
        localDevUser.addPolicyStatements(policyStatementsSsm, `local-dev-geocoding-ssm-policy`);
      }
    }
  }

  private createDynamoDbTable(tableName: string): cdk.aws_dynamodb.Table {
    return new cdk.aws_dynamodb.Table(this, tableName, {
      partitionKey: {
        name: 'pk',
        type: AttributeType.STRING,
      },
      sortKey: {
        name: 'sk',
        type: AttributeType.STRING,
      },
      tableName: tableName,
      timeToLiveAttribute: 'ttl',
      ...ENVIRONMENT.dynamodb,
    });
  }

  private createSqsWithDLQ(queueName: string): sqs.IQueue[] {
    const queueNameDLQ = `${queueName}-dlq`;
    const queueDLQ = new sqs.Queue(this, queueNameDLQ, {
      queueName: queueNameDLQ,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });
    const queue = new sqs.Queue(this, queueName, {
      queueName,
      visibilityTimeout: cdk.Duration.seconds(30),
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      deadLetterQueue: {
        maxReceiveCount: 2,
        queue: queueDLQ,
      },
    });
    return [queue, queueDLQ];
  }

  private corsForHttpMethods(allowedMethods: cdk.aws_lambda.HttpMethod[]): cdk.aws_lambda.FunctionUrlCorsOptions {
    return {
      allowedOrigins: ['*'],
      allowedMethods,
      allowedHeaders: ['*'],
      exposedHeaders: ['*'],
    };
  }
}
