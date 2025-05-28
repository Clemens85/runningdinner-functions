import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';

export const docClient = DynamoDBDocumentClient.from(
  new DynamoDBClient({
    region: 'eu-central-1',
  }),
);

export const TABLE_NAME = 'runningdinner-v1';
