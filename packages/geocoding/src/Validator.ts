import { Address } from './Address';
import { logger } from './aws/Logger';
import { ADMIN_ID_FIELD, ENTITY_ID_FIELD, ENTITY_TYPE_FIELD, GeocodingRequest } from './GeocodingRequest';
import { Util } from './Util';

export class Validator {
  public static validateAddress(address: Address): void {
    const { street, cityName, zip } = address;
    if (!street || (!zip && !cityName)) {
      throw new Error('Missing street or zip/cityName');
    }
  }

  public static validateGeocodingRequest(request: GeocodingRequest): void {
    logger.info('Validating geocoding request', {
      request,
    });
    if (!request) {
      Util.logAndThrowError('Missing geocoding request');
    }
    Validator.assertStringNotEmpty(request.responseQueueUrl, 'Missing responseQueueUrl');
    Validator.assertStringNotEmpty(request[ADMIN_ID_FIELD], 'Missing adminId');
    Validator.assertStringNotEmpty(request[ENTITY_ID_FIELD], 'Missing entityId');
    Validator.assertStringNotEmpty(request[ENTITY_TYPE_FIELD], 'Missing entityType');
    Validator.validateAddress(request.address);
  }

  public static assertStringNotEmpty(str: string | null | undefined, errorMessage: string) {
    if (!str || str.trim().length === 0) {
      Util.logAndThrowError(errorMessage);
    }
  }
}
