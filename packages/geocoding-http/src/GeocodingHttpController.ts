import { ENTITY_ID_FIELD, ENTITY_TYPE_FIELD, GeocodingApiServiceCached, GeocodingResponse, RESPONSE_QUEUE_URL_FIELD, Util, Validator } from '@runningdinner/geocoding';
import { LambdaFunctionURLEvent } from 'aws-lambda';

import { logger } from './aws/Logger';
import { HttpGeocodeBatchRequest, HttpGeocodeRequestLine } from './HttpGeocodeBatchRequest';
import { HttpResponse } from './HttpResponse';

export class GeocodingHttpController {
  public static async processHttpRequest(event: LambdaFunctionURLEvent): Promise<HttpResponse> {
    const batchRequest = JSON.parse(event.body || '{}') as HttpGeocodeBatchRequest;

    const singleRequests = batchRequest?.requests || [];
    if (singleRequests.length === 0) {
      logger.warn(`Request body was empty: ${event.body}`);
      return {
        statusCode: 204,
        body: JSON.stringify({}),
      };
    }

    const { adminId } = batchRequest;
    try {
      Validator.assertStringNotEmpty(adminId, 'Missing adminId in batch request');
    } catch (error) {
      return GeocodingHttpController.httpErrorResponse(400, JSON.stringify(error));
    }

    for (let i = 0; i < singleRequests.length; i++) {
      const singleRequest = singleRequests[i];
      try {
        Validator.validateAddress(singleRequest);
        Validator.assertStringNotEmpty(singleRequest[ENTITY_ID_FIELD], 'Missing entityId');
        Validator.assertStringNotEmpty(singleRequest[ENTITY_TYPE_FIELD], 'Missing entityType');
      } catch (error) {
        return GeocodingHttpController.httpErrorResponse(400, `Request with index ${i} was not valid: ${JSON.stringify(error)}`);
      }
    }

    const requestChunks = Util.splitIntoChunks(singleRequests, 3);
    logger.info(`Processing ${singleRequests.length} geocoding requests in ${requestChunks.length} chunks`);

    const result = await Promise.all(requestChunks.map((requestChunk) => GeocodingHttpController.fetchRequestLineChunks(adminId, requestChunk)));
    const resultList: GeocodingResponse[] = result.flat();

    const responseBody = JSON.stringify(resultList);
    logger.info(`Sending response body: ${responseBody}`);

    return {
      statusCode: 200,
      body: JSON.stringify(resultList),
    };
  }

  private static async fetchRequestLineChunks(adminId: string, requestLines: HttpGeocodeRequestLine[]): Promise<GeocodingResponse[]> {
    const geocodingResponses: GeocodingResponse[] = [];
    for (const requestLine of requestLines) {
      try {
        const response = await GeocodingHttpController.fetchRequestLine(adminId, requestLine);
        geocodingResponses.push(response);
      } catch (error) {
        logger.error(`Error processing request line ${JSON.stringify(requestLine)}: ${error}`);
      }
    }
    return geocodingResponses;
  }

  private static async fetchRequestLine(adminId: string, requestLine: HttpGeocodeRequestLine): Promise<GeocodingResponse> {
    const geocodingResult = await GeocodingApiServiceCached.fetchGeocode(requestLine);
    return {
      ...requestLine,
      geocodingResult,
      adminId,
      [RESPONSE_QUEUE_URL_FIELD]: 'Not used for HTTP requests',
    };
  }

  private static httpErrorResponse(statusCode: number, errorMsg: string): HttpResponse {
    logger.error(errorMsg);
    return {
      statusCode,
      body: errorMsg,
    };
  }
}
