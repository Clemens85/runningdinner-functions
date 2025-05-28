import { SQSEvent, SQSHandler } from 'aws-lambda';
import { Controller } from './Controller';

export const handler: SQSHandler = async (event: SQSEvent) => {
  await Controller.processSqsRecords(event.Records);
};
