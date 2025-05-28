import { Address } from '../Address';
import { logger } from '../aws/Logger';
import { GeocodingApi } from '../GeocodingApi';
import { GeocodingResult } from '../GeocodingResult';
import { GeocodingResultCacheRepository } from './GeocodingResultCacheRepository';

export class GeocodingApiServiceCached {
  public static async fetchGeocode(address: Address): Promise<GeocodingResult | null> {
    const addressCacheKey = GeocodingApiServiceCached.buildAddressCacheKey(address);
    const result = await GeocodingApiServiceCached.findGeocodingResultByAddressCacheKeySafe(addressCacheKey);
    if (result) {
      logger.info(`Cache hit for address: ${addressCacheKey}`);
      return result;
    }
    logger.info(`Address ${addressCacheKey} not found, querying Google MAPS API...`);
    const geocodingResult = await GeocodingApi.fetchGeocode(address);
    if (!geocodingResult) {
      return null;
    }
    await GeocodingApiServiceCached.saveGeocodingResultSafe(addressCacheKey, geocodingResult);
    return geocodingResult;
  }

  private static async findGeocodingResultByAddressCacheKeySafe(addressCacheKey: string) {
    try {
      logger.info(`Trying to fetch geocoding result from cache for address: ${addressCacheKey}`);
      return await GeocodingResultCacheRepository.findGeocodingResultByAddressCacheKey(addressCacheKey);
    } catch (error) {
      logger.error(`Error fetching geocoding result from cache`, { error });
      return null;
    }
  }
  private static async saveGeocodingResultSafe(addressCacheKey: string, geocodingResult: GeocodingResult) {
    try {
      await GeocodingResultCacheRepository.saveGeocodingResult(addressCacheKey, geocodingResult);
    } catch (error) {
      logger.error(`Error saving geocoding result ${geocodingResult} for ${addressCacheKey}`, { error });
      return null;
    }
  }

  static buildAddressCacheKey(address: Address): string {
    return GeocodingApi.getAddressQueryParam(address);
  }
}
