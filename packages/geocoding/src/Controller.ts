import { SQSRecord } from 'aws-lambda';
import { Address } from './Address';
import { ADMIN_ID_FIELD, ENTITY_ID_FIELD, ENTITY_TYPE_FIELD, GeocodingEntityType, GeocodingRequest, RESPONSE_QUEUE_URL_FIELD } from './GeocodingRequest';
import { GeocodingResponse } from './GeocodingResponse';
import { SQSResponseHandler } from './SQSResponseHandler';
import { logger } from './aws/Logger';
import { GeocodingApiServiceCached } from './cache/GeocodingApiServiceCached';
import { Validator } from './Validator';

export class Controller {
  public static async processSqsRecords(sqsRecords: SQSRecord[]): Promise<any> {
    if (!sqsRecords || sqsRecords.length === 0) {
      throw new Error('No SQS records to process');
    }
    for (const record of sqsRecords) {
      await Controller.processSqsRecord(record);
    }
    logger.info(`${sqsRecords.length} records processed successfully`);
  }

  private static async processSqsRecord(record: SQSRecord): Promise<void> {
    const geocodingRequest: GeocodingRequest = Controller.mapSqsRecordToGeocodingRequest(record);
    logger.info('Processing SQS record', {
      request: geocodingRequest,
    });

    Validator.validateGeocodingRequest(geocodingRequest);

    const result = await GeocodingApiServiceCached.fetchGeocode(geocodingRequest.address);

    const geocodingResponse: GeocodingResponse = {
      ...geocodingRequest,
      geocodingResult: result,
    };

    await SQSResponseHandler.sendResponse(geocodingResponse);
  }

  private static mapSqsRecordToGeocodingRequest(record: SQSRecord): GeocodingRequest {
    const address = JSON.parse(record.body) as Address;
    const entityId = (record.messageAttributes || {})[ENTITY_ID_FIELD]?.stringValue || '';
    const entityType = (record.messageAttributes || {})[ENTITY_TYPE_FIELD]?.stringValue as GeocodingEntityType;
    const adminId = (record.messageAttributes || {})[ADMIN_ID_FIELD]?.stringValue || '';
    const responseQueueUrl = (record.messageAttributes || {})[RESPONSE_QUEUE_URL_FIELD]?.stringValue || '';

    return {
      address,
      entityId,
      entityType,
      adminId,
      responseQueueUrl,
    };
  }
}
