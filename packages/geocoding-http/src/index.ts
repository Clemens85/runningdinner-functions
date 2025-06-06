import { LambdaFunctionURLEvent, LambdaFunctionURLHandler } from 'aws-lambda';
import { GeocodingHttpController } from './GeocodingHttpController';

export const handler: LambdaFunctionURLHandler = async (event: LambdaFunctionURLEvent) => {
  return await GeocodingHttpController.processHttpRequest(event);
}