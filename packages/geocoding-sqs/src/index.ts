import { SQSEvent, SQSHandler } from 'aws-lambda';
import { GeocodingSqsController } from './GeocodingSqsController';

export const handler: SQSHandler = async (event: SQSEvent) => {
  await GeocodingSqsController.processSqsRecords(event.Records);
};
