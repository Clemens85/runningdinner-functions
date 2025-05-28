import * as cdk from "aws-cdk-lib";
import * as sqs from "aws-cdk-lib/aws-sqs";
import { Construct } from "constructs";
import { NodeJsLambda } from "./NodeJsLambda";
import * as lambdaEventSources from "aws-cdk-lib/aws-lambda-event-sources";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { ENVIRONMENT } from "./Environment";
import { LocalDevUser } from "./LocalDevUser";
import { AttributeType } from "aws-cdk-lib/aws-dynamodb";

export class GeocodingStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const geocodingRequestQueue = this.createSqsWithDLQ("geocoding-request")[0];

    const geocodingResponseQueue =
      this.createSqsWithDLQ("geocoding-response")[0];

    // Create lambda and give access to the queues
    const geocodingFunc = new NodeJsLambda(this, "geocoding", {
      name: "geocoding",
      packageFolderName: "geocoding",
    });
    geocodingFunc.lambdaFunction.addEventSource(
      new lambdaEventSources.SqsEventSource(geocodingRequestQueue, {
        batchSize: 3,
      })
    );
    geocodingRequestQueue.grantConsumeMessages(geocodingFunc.lambdaFunction);
    geocodingResponseQueue.grantSendMessages(geocodingFunc.lambdaFunction);

    // Grant access to the SSM parameter store
    const policyStatementsSsm = this.allowParameterStoreAccess(
      geocodingFunc.lambdaFunction,
      "/runningdinner/googlemaps/*"
    );

    const table = this.createDynamoDbTable("runningdinner-v1");
    table.grantReadWriteData(geocodingFunc.lambdaFunction);

    // Create local dev response SQS queue if in dev stage
    if (ENVIRONMENT.createDevSqsResponseQueue) {
      const geocodingResponseQueueLocalDev = this.createSqsWithDLQ(
        "geocoding-response-local_dev"
      )[0];

      geocodingResponseQueueLocalDev.grantSendMessages(
        geocodingFunc.lambdaFunction
      );

      const localDevUser = new LocalDevUser(this, "geocoding-local-dev");
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

  private allowParameterStoreAccess(
    lambdaFunc: lambda.Function,
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

    lambdaFunc.addToRolePolicy(ssmPolicy);
    lambdaFunc.addToRolePolicy(kmsPolicy);

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
}
