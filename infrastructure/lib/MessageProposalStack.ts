import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

import { CommonUtils } from './CommonUtils';
import { ENVIRONMENT } from './Environment';
import { LocalDevUser } from './LocalDevUser';
import { PythonLambda } from './PythonLambda';

const PINECONE_API_KEY_PARAM_NAME = '/runningdinner/pinecone/apikey';
const OPENAI_API_KEY_PARAM_NAME = '/runningdinner/openai/apikey';
const LANGSMITH_API_KEY_PARAM_NAME = '/runningdinner/langsmith/apikey';

export interface MessageProposalStackProps extends cdk.StackProps {
  localDevUser?: LocalDevUser;
}

export class MessageProposalStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: MessageProposalStackProps) {
    super(scope, id, props);

    const commonUtils = new CommonUtils(this);

    const bucketName = `message-proposal-${ENVIRONMENT.stage.toLowerCase()}`;
    const bucket = commonUtils.createBucket(bucketName, []);

    const messageProposalFunc = new PythonLambda(this, 'message-proposal', {
      name: 'message-proposal',
      runtime: lambda.Runtime.PYTHON_3_13,
      packageFolderName: 'message-proposal',
      index: 'LambdaHandler.py',
      handler: 'lambda_handler',
      memorySize: 256,
      timeout: cdk.Duration.seconds(60),
      allowAccessToBucket: bucket,
      addFunctionUrl: false,
      environment: {
        LANGSMITH_TRACING: 'true',
        LANGSMITH_ENDPOINT: 'https://eu.api.smith.langchain.com',
        LANGSMITH_PROJECT: 'pr-stupendous-spray-96',
      },
      bundling: {
        assetExcludes: [
          '*.ipynb',
          'notebooks/',
          '__pycache__/',
          '*.pyc',
          '*.pyo',
          'tests/',
          'local_db/',
          '.idea/',
          '.env',
          '.env.example',
          'local_adapter/',
          '.vscode/',
          '*.dist-info',
          '*.egg-info',
          'tests/',
          'local_adapter/',
          '.pytest_cache/',
          'extensions/',
        ],
      },
    });

    // Grant access to the SSM parameter store
    commonUtils.allowParameterStoreAccess([messageProposalFunc.lambdaFunction], PINECONE_API_KEY_PARAM_NAME);
    commonUtils.allowParameterStoreAccess([messageProposalFunc.lambdaFunction], OPENAI_API_KEY_PARAM_NAME);
    commonUtils.allowParameterStoreAccess([messageProposalFunc.lambdaFunction], LANGSMITH_API_KEY_PARAM_NAME);

    const localDevUser = props?.localDevUser;
    if (localDevUser) {
      localDevUser.grantBucketReadWrite(bucket, 'MessageProposalLocalDevS3Policy');
    }
  }
}
