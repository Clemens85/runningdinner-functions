import { RemovalPolicy } from "aws-cdk-lib";
import { BillingMode } from "aws-cdk-lib/aws-dynamodb";

export type EnvironmentType = {
  stage: string;
  createDevSqsResponseQueue?: boolean;
  dynamodb: {
    removalPolicy: RemovalPolicy;
    readCapacity?: number;
    writeCapacity?: number;
    billingMode: BillingMode;
  };
};

function getEnvironment(): EnvironmentType {
  const stage = process.env.GEOCODING_STAGE || "";
  if (stage === "dev") {
    return {
      stage: "dev",
      createDevSqsResponseQueue: true,
      dynamodb: {
        removalPolicy: RemovalPolicy.DESTROY,
        billingMode: BillingMode.PROVISIONED,
        readCapacity: 12,
        writeCapacity: 12,
      },
    };
  } else if (stage === "prod") {
    return {
      stage: "prod",
      dynamodb: {
        removalPolicy: RemovalPolicy.RETAIN,
        billingMode: BillingMode.PROVISIONED,
        readCapacity: 12,
        writeCapacity: 12,
      },
    };
  }
  throw new Error(
    `Passed invalid stage, only dev or prod is allowed, but was: ${stage}`
  );
}

export const ENVIRONMENT = getEnvironment();
