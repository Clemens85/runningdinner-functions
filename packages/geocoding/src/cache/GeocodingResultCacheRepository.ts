import { PutCommand, QueryCommand } from '@aws-sdk/lib-dynamodb';
import { addMonths } from 'date-fns';

import { docClient, TABLE_NAME } from '../aws/DocClientFactory';
import { formatDateToUTC, toUnixTimestamp } from '../DateUtil';
import { GeocodingResult } from '../GeocodingResult';
import { GeocodingCacheItemDb } from './GeocodingCacheItemDb';

const GEOCODING_CACHE_PK = 'GEOCODING#CACHE';

const EXPIRES_IN_MONTHS = 12;

export class GeocodingResultCacheRepository {
  static async findGeocodingResultByAddressCacheKey(addressCacheKey: string): Promise<GeocodingResult | null> {
    const command = new QueryCommand({
      TableName: TABLE_NAME,
      KeyConditionExpression: 'pk = :pk and sk = :sk',
      ExpressionAttributeValues: {
        ':pk': GEOCODING_CACHE_PK,
        ':sk': `ADDRESS#${addressCacheKey}`,
      },
    });
    const response = await docClient.send(command);
    if (!response.Items || response.Items.length === 0) {
      return null;
    }
    return (response.Items[0] as GeocodingCacheItemDb).attributes;
  }

  static async saveGeocodingResult(addressCacheKey: string, geocodingResult: GeocodingResult, customTtl?: number): Promise<void> {
    const item: GeocodingCacheItemDb = {
      pk: GEOCODING_CACHE_PK,
      sk: `ADDRESS#${addressCacheKey}`,
      attributes: { ...geocodingResult },
      createdAt: formatDateToUTC(new Date()),
      ttl: customTtl ? customTtl : GeocodingResultCacheRepository.calculateTTL(),
    };
    const command = new PutCommand({
      TableName: TABLE_NAME,
      Item: item,
    });
    await docClient.send(command);
  }

  static calculateTTL(): number {
    const now = new Date();
    const expireDate = addMonths(now, EXPIRES_IN_MONTHS);
    return toUnixTimestamp(expireDate);
  }
}
