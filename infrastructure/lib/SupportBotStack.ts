import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { PythonLambda } from "./PythonLambda";
import { CommonUtils } from "./CommonUtils";

const PINECONE_API_KEY_PARAM_NAME = "/runningdinner/pinecone/apikey";
const OPENAI_API_KEY_PARAM_NAME = "/runningdinner/openai/apikey";

export class SupportBotStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const commonUtils = new CommonUtils(this);

    const supportBotFunc = new PythonLambda(this, "support-bot", {
      name: "support-bot",
      runtime: lambda.Runtime.PYTHON_3_12,
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
      environment: {},
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

    // Grant access to the SSM parameter store
    commonUtils.allowParameterStoreAccess(
      [supportBotFunc.lambdaFunction],
      PINECONE_API_KEY_PARAM_NAME
    );
    commonUtils.allowParameterStoreAccess(
      [supportBotFunc.lambdaFunction],
      OPENAI_API_KEY_PARAM_NAME
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
}
