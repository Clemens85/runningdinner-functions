import * as iam from "aws-cdk-lib/aws-iam";
import * as sqs from "aws-cdk-lib/aws-sqs";
import * as cdk from "aws-cdk-lib";

export class LocalDevUser {
  private readonly stack: cdk.Stack;

  private readonly user: iam.User;

  constructor(scope: cdk.Stack, userName: string) {
    this.stack = scope;
    this.user = new iam.User(this.stack, userName, {
      userName,
      // No password set, so no console access
    });

    // Create access key for programmatic access (outputs secret in CloudFormation, so use only for dev!)
    const accessKey = new iam.CfnAccessKey(
      this.stack,
      `${userName}-access-key`,
      {
        userName: this.user.userName,
      }
    );

    // Optional: Output credentials (for dev only, never for prod!)
    new cdk.CfnOutput(this.stack, `${userName}-access-key-id`, {
      value: accessKey.ref,
    });
    new cdk.CfnOutput(this.stack, `${userName}-access-key-secret`, {
      value: accessKey.attrSecretAccessKey,
    });
  }

  public grantSqsAccess(queues: sqs.IQueue[]) {
    const queueArns = queues.map((queue) => queue.queueArn);

    // Policy: Allow full access to the specific SQS queues
    const sqsAccessPolicy = new iam.Policy(this.stack, "LocalDevSqsPolicy", {
      statements: [
        new iam.PolicyStatement({
          actions: [
            "sqs:SendMessage",
            "sqs:SendMessageBatch",
            "sqs:ReceiveMessage",
            "sqs:DeleteMessage",
            "sqs:GetQueueAttributes",
            "sqs:GetQueueUrl",
          ],
          resources: queueArns,
        }),
      ],
      policyName: "LocalDevSqsPolicy",
    });

    // Attach policy to user
    this.user.attachInlinePolicy(sqsAccessPolicy);
  }

  public grantDynamoDbReadWriteData(table: cdk.aws_dynamodb.Table) {
    const policyName = `LocalDevDynamoDbPolicy-${table.tableName}`;
    // Policy: Allow read/write access to the DynamoDB table
    const dynamoDbPolicy = new iam.Policy(
      this.stack,
      "LocalDevDynamoDbPolicy",
      {
        statements: [
          new iam.PolicyStatement({
            actions: [
              "dynamodb:PutItem",
              "dynamodb:GetItem",
              "dynamodb:UpdateItem",
              "dynamodb:DeleteItem",
              "dynamodb:Query",
              "dynamodb:Scan",
            ],
            resources: [table.tableArn],
          }),
        ],
        policyName,
      }
    );
    // Attach policy to user
    this.user.attachInlinePolicy(dynamoDbPolicy);
  }

  public addPolicyStatements(
    policyStatements: iam.PolicyStatement[],
    policyName: string
  ) {
    // Create a new policy with the provided statements
    const customPolicy = new iam.Policy(this.stack, policyName, {
      statements: policyStatements,
      policyName,
    });
    // Attach the custom policy to the user
    this.user.attachInlinePolicy(customPolicy);
  }

  public grantBucketReadWrite(bucket: cdk.aws_s3.Bucket) {
    const s3AccessPolicy = new iam.Policy(this.stack, "LocalDevS3Policy", {
      statements: [
        new iam.PolicyStatement({
          actions: ["s3:ListBucket", "s3:GetObject", "s3:PutObject"],
          resources: [bucket.bucketArn, `${bucket.bucketArn}/*`],
        }),
      ],
      policyName: "LocalDevS3Policy",
    });
    this.user.attachInlinePolicy(s3AccessPolicy);
    // bucket.grantReadWrite(this.user);
    // bucket.
  }
}
