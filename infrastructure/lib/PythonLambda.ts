import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as cdk from "aws-cdk-lib";
import * as path from "node:path";
import { Bucket } from "aws-cdk-lib/aws-s3";
import {
  PythonFunction,
  PythonFunctionProps,
} from "@aws-cdk/aws-lambda-python-alpha";

export type PythonLambdaProps = {
  name: string;
  packageFolderName: string;
  allowAccessToBucket?: Bucket;
  index: string;
  handler: string;
} & Omit<PythonFunctionProps, "handler" | "code" | "entry">;

export class PythonLambda extends Construct {
  public lambdaFunction: lambda.Function;

  public logGroup: cdk.aws_logs.LogGroup;

  constructor(scope: Construct, id: string, props: PythonLambdaProps) {
    super(scope, id);

    const {
      name,
      packageFolderName,
      index,
      handler,
      environment,
      timeout,
      deadLetterQueueEnabled,
      allowAccessToBucket,
      ...remainder
    } = props;

    let environmentToSet = environment || {};
    environmentToSet = {
      ...environmentToSet,
      JOBLIB_MULTIPROCESSING: "0",
    };
    const timeoutToSet = timeout || cdk.Duration.seconds(30);

    this.logGroup = new cdk.aws_logs.LogGroup(this, `loggroup-${name}`, {
      logGroupName: `/aws/lambda/${name}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      retention: cdk.aws_logs.RetentionDays.FIVE_DAYS,
    });

    let deadLetterQueue = undefined;
    if (deadLetterQueueEnabled) {
      deadLetterQueue = new cdk.aws_sqs.Queue(this, `dlq-${name}`, {
        queueName: `dlq-${name}`,
        retentionPeriod: cdk.Duration.days(14),
        removalPolicy: cdk.RemovalPolicy.DESTROY,
      });
    }

    this.lambdaFunction = new PythonFunction(this, name, {
      ...remainder,
      functionName: name,
      environment: environmentToSet,
      timeout: timeoutToSet,
      logGroup: this.logGroup,
      entry: path.join(__dirname, `../../packages/${packageFolderName}`),
      index,
      handler,
      deadLetterQueueEnabled: deadLetterQueueEnabled,
      deadLetterQueue: deadLetterQueue,
    });

    if (allowAccessToBucket) {
      // Grant the Lambda function permissions to access the S3 bucket
      allowAccessToBucket.grantReadWrite(this.lambdaFunction);
      allowAccessToBucket.grantPut(this.lambdaFunction);
    }
  }
}
