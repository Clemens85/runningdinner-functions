import { RemovalPolicy } from 'aws-cdk-lib';
import * as cdk from 'aws-cdk-lib';
import { BillingMode } from 'aws-cdk-lib/aws-dynamodb';

export type EnvironmentType = {
  stage: string;
  isDevStage?: boolean;
  dynamodb: {
    removalPolicy: RemovalPolicy;
    readCapacity?: number;
    writeCapacity?: number;
    billingMode: BillingMode;
  };
  s3: {
    removalPolicy: cdk.RemovalPolicy;
    autoDeleteObjects: boolean;
  };
};

function getEnvironment(): EnvironmentType {
  const stage = process.env.RUNNINGDINNER_FUNCTIONS_STAGE || '';
  if (stage === 'dev') {
    return {
      stage: 'dev',
      s3: {
        autoDeleteObjects: true,
        removalPolicy: RemovalPolicy.DESTROY,
      },
      isDevStage: true,
      dynamodb: {
        removalPolicy: RemovalPolicy.DESTROY,
        billingMode: BillingMode.PROVISIONED,
        readCapacity: 8,
        writeCapacity: 8,
      },
    };
  } else if (stage === 'prod') {
    return {
      stage: 'prod',
      s3: {
        autoDeleteObjects: false,
        removalPolicy: RemovalPolicy.RETAIN,
      },
      dynamodb: {
        removalPolicy: RemovalPolicy.RETAIN,
        billingMode: BillingMode.PROVISIONED,
        readCapacity: 12,
        writeCapacity: 12,
      },
    };
  }
  throw new Error(`Passed invalid stage, only dev or prod is allowed, but was: ${stage}`);
}

export const ENVIRONMENT = getEnvironment();
