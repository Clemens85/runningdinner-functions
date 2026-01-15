import * as path from 'node:path';

import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as sns from 'aws-cdk-lib/aws-sns';
import { Construct } from 'constructs';

import { CommonUtils } from './CommonUtils';
import { ENVIRONMENT } from './Environment';
import { LocalDevUser } from './LocalDevUser';
import { PythonLambda } from './PythonLambda';

export interface RouteOptimizationStackProps extends cdk.StackProps {
  localDevUser?: LocalDevUser;
}

export class RouteOptimizationStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: RouteOptimizationStackProps) {
    super(scope, id, props);

    const commonUtils = new CommonUtils(this);

    const bucketName = `route-optimization-${ENVIRONMENT.stage.toLowerCase()}`;
    const bucket = commonUtils.createBucket(bucketName, [
      {
        id: 'ExpireAfter14Days',
        expiration: cdk.Duration.days(14),
        enabled: true,
      },
    ]);

    const topicName = 'route-optimization-notifications';
    const topic = new sns.Topic(this, topicName, {
      topicName: topicName,
      displayName: topicName,
    });

    const optimizationLayer = new lambda.LayerVersion(this, 'route_optimization_layer', {
      layerVersionName: 'route_optimization_layer',
      code: lambda.Code.fromAsset(path.join(__dirname, 'layers/route_optimization')),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
      description: 'AWS Lambda Layer containing scikit-learn, numpy and pydantic',
    });

    const optimizationFunc = new PythonLambda(this, 'route-optimization', {
      name: 'route-optimization',
      runtime: lambda.Runtime.PYTHON_3_12,
      packageFolderName: 'optimization',
      index: 'LambdaHandler.py',
      handler: 'lambda_handler',
      allowAccessToBucket: bucket,
      memorySize: 1024, // 1 GB
      timeout: cdk.Duration.minutes(3), // Increased timeout for route optimization
      deadLetterQueueEnabled: true,
      environment: {
        SNS_TOPIC_ARN: topic.topicArn,
      },
      bundling: {
        assetExcludes: [
          '*.ipynb',
          'notebooks/',
          '__pycache__/',
          '*.pyc',
          '*.pyo',
          'test/',
          'test-data/',
          'main.py',
          'main_watcher.py',
          'start-jupyter.sh',
          'Visualizer.py',
          'local_adapter/',
          '.vscode/',
          '*.dist-info',
          '*.egg-info',
          'tests/',
          '.pytest_cache/',
        ],
      },
      layers: [optimizationLayer],
    });

    topic.grantPublish(optimizationFunc.lambdaFunction);

    bucket.addEventNotification(
      s3.EventType.OBJECT_CREATED, // Trigger on object creation
      new s3n.LambdaDestination(optimizationFunc.lambdaFunction),
      {
        prefix: 'optimization/',
        suffix: '-request.json',
      },
    );

    const localDevUser = props?.localDevUser;
    if (localDevUser) {
      localDevUser.grantBucketReadWrite(bucket);
    }
  }
}
