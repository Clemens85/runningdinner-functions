import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as cdk from "aws-cdk-lib";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import * as path from "node:path";

export type LambdaFunctionUrlProps = {
  name: string;
  packageFolderName: string;
  addFunctionUrl?: boolean;
  cors?: cdk.aws_lambda.FunctionUrlCorsOptions;
  runtime?: lambda.Runtime;
} & Omit<lambda.FunctionProps, "runtime" | "handler" | "code">;

export class NodeJsLambda extends Construct {
  public lambdaFunction: lambda.Function;

  public logGroup: cdk.aws_logs.LogGroup;

  constructor(scope: Construct, id: string, props: LambdaFunctionUrlProps) {
    super(scope, id);

    const {
      name,
      packageFolderName,
      addFunctionUrl,
      cors,
      environment,
      timeout,
      deadLetterQueueEnabled,
      runtime,
      ...remainder
    } = props;

    let environmentToSet = environment || {};
    environmentToSet = {
      ...environmentToSet,
      NODE_OPTIONS: "--enable-source-maps",
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

    this.lambdaFunction = new NodejsFunction(this, name, {
      ...remainder,
      runtime: runtime ? runtime : lambda.Runtime.NODEJS_22_X,
      functionName: name,
      environment: environmentToSet,
      timeout: timeoutToSet,
      logGroup: this.logGroup,
      handler: "handler",
      entry: path.join(
        __dirname,
        `../../packages/${packageFolderName}/src/index.ts`
      ),
      bundling: {
        sourceMap: true,
        minify: true,
        // esbuildVersion: "0.21.5",
      },
      deadLetterQueueEnabled: deadLetterQueueEnabled,
      deadLetterQueue: deadLetterQueue,
    });

    if (addFunctionUrl) {
      const functionUrl = this.lambdaFunction.addFunctionUrl({
        authType: lambda.FunctionUrlAuthType.NONE,
        cors,
      });
      // Remove all non-alphanumeric chars from packageFolderName
      const normalizedPackageFolderName = packageFolderName.replace(
        /[^a-zA-Z0-9]/g,
        ""
      );
      new cdk.CfnOutput(this, `${normalizedPackageFolderName}FunctionUrl`, {
        value: functionUrl.url,
        key: `${normalizedPackageFolderName}FunctionUrl`,
      });
    }
  }
}
