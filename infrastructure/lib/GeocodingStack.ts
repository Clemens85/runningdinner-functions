import * as cdk from "aws-cdk-lib";
import * as sqs from "aws-cdk-lib/aws-sqs";
import { Construct } from "constructs";
import { NodeJsLambda } from "./NodeJsLambda";
import * as lambdaEventSources from "aws-cdk-lib/aws-lambda-event-sources";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { ENVIRONMENT } from "./Environment";
import { LocalDevUser } from "./LocalDevUser";
import { AttributeType, Table } from "aws-cdk-lib/aws-dynamodb";
import { HttpMethod } from "aws-cdk-lib/aws-lambda";

export interface GeocodingStackProps extends cdk.StackProps {
  localDevUser?: LocalDevUser;
}

export class GeocodingStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: GeocodingStackProps) {
    super(scope, id, props);

    const geocodingRequestQueue = this.createSqsWithDLQ("geocoding-request")[0];

    const geocodingResponseQueue =
      this.createSqsWithDLQ("geocoding-response")[0];

    // Create SQS-lambda and give access to the queues
    const geocodingFuncSqs = new NodeJsLambda(this, "geocoding-sqs", {
      name: "geocoding-sqs",
      packageFolderName: "geocoding-sqs",
    });
    // Create HTTP-Lambda
    const geocodingFuncHttp = new NodeJsLambda(this, "geocoding-http", {
      name: "geocoding-http",
      packageFolderName: "geocoding-http",
      addFunctionUrl: true,
      cors: this.corsForHttpMethods([HttpMethod.HEAD, HttpMethod.PUT]),
    });

    geocodingFuncSqs.lambdaFunction.addEventSource(
      new lambdaEventSources.SqsEventSource(geocodingRequestQueue, {
        batchSize: 3,
      })
    );
    geocodingRequestQueue.grantConsumeMessages(geocodingFuncSqs.lambdaFunction);
    geocodingResponseQueue.grantSendMessages(geocodingFuncSqs.lambdaFunction);

    // Grant access to the SSM parameter store
    const policyStatementsSsm = this.allowParameterStoreAccess(
      [geocodingFuncSqs.lambdaFunction, geocodingFuncHttp.lambdaFunction],
      "/runningdinner/googlemaps/*"
    );

    const table = this.createDynamoDbTable("runningdinner-v1");
    this.grantReadWriteDataToTable(
      [geocodingFuncSqs.lambdaFunction, geocodingFuncHttp.lambdaFunction],
      table
    );

    // Create local dev response SQS queue if in dev stage
    if (ENVIRONMENT.isDevStage) {
      const geocodingResponseQueueLocalDev = this.createSqsWithDLQ(
        "geocoding-response-local_dev"
      )[0];

      geocodingResponseQueueLocalDev.grantSendMessages(
        geocodingFuncSqs.lambdaFunction
      );

      const localDevUser = props?.localDevUser;
      if (localDevUser) {
        localDevUser.grantSqsAccess([
          geocodingRequestQueue,
          geocodingResponseQueueLocalDev,
        ]);
        localDevUser.grantDynamoDbReadWriteData(table);
        localDevUser.addPolicyStatements(
          policyStatementsSsm,
          `local-dev-geocoding-ssm-policy`
        );
      }
    }
  }

  private grantReadWriteDataToTable(
    lambdaFunctions: Array<lambda.Function>,
    table: Table
  ) {
    for (let lambdaFunc of lambdaFunctions) {
      table.grantReadWriteData(lambdaFunc);
    }
  }

  private allowParameterStoreAccess(
    lambdaFunctions: Array<lambda.Function>,
    paramStorePathPrefix: string
  ): iam.PolicyStatement[] {
    const region = this.region;
    const accountId = this.account;

    const actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath",
    ];
    const ssmPolicy = new iam.PolicyStatement({
      actions,
      resources: [
        `arn:aws:ssm:${region}:${accountId}:parameter${paramStorePathPrefix}`,
      ],
    });

    const kmsPolicy = new iam.PolicyStatement({
      actions: ["kms:Decrypt", "kms:Encrypt"],
      resources: [`arn:aws:kms:${region}:${accountId}:key/*`],
    });

    for (let lambdaFunc of lambdaFunctions) {
      lambdaFunc.addToRolePolicy(ssmPolicy);
      lambdaFunc.addToRolePolicy(kmsPolicy);
    }

    return [ssmPolicy, kmsPolicy];
  }

  private createDynamoDbTable(tableName: string): cdk.aws_dynamodb.Table {
    return new cdk.aws_dynamodb.Table(this, tableName, {
      partitionKey: {
        name: "pk",
        type: AttributeType.STRING,
      },
      sortKey: {
        name: "sk",
        type: AttributeType.STRING,
      },
      tableName: tableName,
      timeToLiveAttribute: "ttl",
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

  private corsForHttpMethods(
    allowedMethods: cdk.aws_lambda.HttpMethod[]
  ): cdk.aws_lambda.FunctionUrlCorsOptions {
    return {
      allowedOrigins: ["*"],
      allowedMethods,
      allowedHeaders: ["*"],
      exposedHeaders: ["*"],
    };
  }
}
