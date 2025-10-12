import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { PythonLambda } from "./PythonLambda";
import { CommonUtils } from "./CommonUtils";
import { AttributeType, BillingMode } from "aws-cdk-lib/aws-dynamodb";
import { ENVIRONMENT } from "./Environment";

const PINECONE_API_KEY_PARAM_NAME = "/runningdinner/pinecone/apikey";
const OPENAI_API_KEY_PARAM_NAME = "/runningdinner/openai/apikey";
const LANGSMITH_API_KEY_PARAM_NAME = "/runningdinner/langsmith/apikey";

export class SupportBotStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const commonUtils = new CommonUtils(this);

    const supportBotFunc = new PythonLambda(this, "support-bot", {
      name: "support-bot",
      runtime: lambda.Runtime.PYTHON_3_13,
      packageFolderName: "support-bot",
      index: "LambdaHandler.py",
      handler: "lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.seconds(15),
      addFunctionUrl: true,
      cors: this.corsForHttpMethods([
        lambda.HttpMethod.HEAD,
        lambda.HttpMethod.GET,
        lambda.HttpMethod.POST,
      ]),
      environment: {
        LANGSMITH_TRACING: "true",
        LANGSMITH_ENDPOINT: "https://eu.api.smith.langchain.com",
        LANGSMITH_PROJECT: "pr-stupendous-spray-96",
        RUNNING_DINNER_API_HOST: "https://runyourdinner.eu",
        OPENAI_TEMPERATURE: "0.1",
        OPENAI_MODEL: "gpt-4.1-mini",
      },
      bundling: {
        assetExcludes: [
          "*.ipynb",
          "notebooks/",
          "__pycache__/",
          "*.pyc",
          "*.pyo",
          "test/",
          "local_db/",
          ".idea/",
          ".env",
          ".env.example",
          "main.py",
          "start-jupyter.sh",
          "local_adapter/",
          ".vscode/",
          "*.dist-info",
          "*.egg-info",
          "tests/",
          "local_web-adapter/",
          "run_local_server.py",
          ".pytest_cache/",
        ],
      },
    });

    const table = this.createDynamoDbTable("supportbot-v1");
    commonUtils.grantReadWriteDataToTable(
      [supportBotFunc.lambdaFunction],
      table
    );

    // Grant access to the SSM parameter store
    commonUtils.allowParameterStoreAccess(
      [supportBotFunc.lambdaFunction],
      PINECONE_API_KEY_PARAM_NAME
    );
    commonUtils.allowParameterStoreAccess(
      [supportBotFunc.lambdaFunction],
      OPENAI_API_KEY_PARAM_NAME
    );
    commonUtils.allowParameterStoreAccess(
      [supportBotFunc.lambdaFunction],
      LANGSMITH_API_KEY_PARAM_NAME
    );
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

  private createDynamoDbTable(tableName: string): cdk.aws_dynamodb.Table {
    return new cdk.aws_dynamodb.Table(this, tableName, {
      partitionKey: {
        name: "PK",
        type: AttributeType.STRING,
      },
      sortKey: {
        name: "SK",
        type: AttributeType.STRING,
      },
      tableName: tableName,
      timeToLiveAttribute: "expireAt",
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      billingMode: BillingMode.PROVISIONED,
      readCapacity: 4,
      writeCapacity: 4,
    });
  }
}
