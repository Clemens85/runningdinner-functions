import axios from 'axios';

import { Address } from './Address';
import { logger } from './aws/Logger';
import { EXACTNESS_TYPE, GeocodingResult } from './GeocodingResult';
import { GoogleMapsApiKeyFactory } from './GoogleMapsApiKeyFactory';
import { Util } from './Util';
import { Validator } from './Validator';

const googleMapsApiKeyFactory = GoogleMapsApiKeyFactory.getInstance();

type GeocodingApiSingleResult = {
  formattedAddress: string;
  granularity: string;
  location?: {
    latitude: number;
    longitude: number;
  };
};

export class GeocodingApi {
  public static async fetchGeocode(address: Address): Promise<GeocodingResult | null> {
    logger.info(`Fetching API key for Google Maps...`);
    const apiKey = await googleMapsApiKeyFactory.getApiKey();

    const addressQueryParam = GeocodingApi.getAddressQueryParam(address);
    logger.info(`Fetching geocode for address: ${addressQueryParam}`);
    const url = `https://geocode.googleapis.com/v4/geocode/address/${addressQueryParam}`;

    let data: Record<string, unknown>;
    try {
      const response = await axios.get(url, {
        headers: { 'X-Goog-Api-Key': apiKey },
      });
      data = response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (error.response?.status === 401 || error.response?.status === 403)) {
        // Try to refetch API key (in case lambda is warmed), but don't wait here. This may help on next request
        googleMapsApiKeyFactory.triggerRefetchApiKey();
      }
      Util.logAndThrowError(`Error fetching geocode: ${error}`);
    }
    if (!data) {
      Util.logAndThrowError('No data received from geocode API');
    }

    const results = (data.results || []) as GeocodingApiSingleResult[];
    if (results.length === 0) {
      logger.warn(`No results found for address: ${addressQueryParam}`);
      return null;
    }

    const result = GeocodingApi.findBestResult(results);

    return GeocodingApi.mapApiResultToGeocodingResult(result);
  }

  public static getAddressQueryParam(address: Address): string {
    const { street, streetNr, cityName, zip } = address;
    Validator.validateAddress(address);
    const streetWithNr = streetNr ? `${street} ${streetNr}` : street;
    const addressString = `${streetWithNr}, ${zip}, ${cityName}`;
    return encodeURIComponent(addressString).replace(/%20/g, '+').replace(/%2C/gi, ',');
  }

  static findBestResult(results: GeocodingApiSingleResult[]): GeocodingApiSingleResult {
    let bestResult = results.find((result) => result.granularity === 'ROOFTOP');
    if (!bestResult) {
      bestResult = results.find((result) => result.granularity === 'RANGE_INTERPOLATED');
    }
    if (!bestResult) {
      bestResult = results.find((result) => result.granularity === 'GEOMETRIC_CENTER');
    }
    if (!bestResult) {
      bestResult = results.find((result) => result.granularity === 'APPROXIMATE');
    }
    if (!bestResult) {
      bestResult = results[0];
    }
    return bestResult;
  }

  static mapApiResultToGeocodingResult(result: GeocodingApiSingleResult): GeocodingResult {
    const formattedAddress = result.formattedAddress;

    let exactness: EXACTNESS_TYPE = 'NONE';
    if (result.granularity === 'ROOFTOP') {
      exactness = 'EXACT';
    } else if (result.granularity === 'APPROXIMATE' || result.granularity === 'GEOMETRIC_CENTER' || result.granularity === 'RANGE_INTERPOLATED') {
      exactness = 'NOT_EXACT';
    }

    logger.info(`GOT LOCATION TYPE ${result.granularity} for address: ${formattedAddress}, exactness: ${exactness}`);

    const lat = result.location?.latitude || -1;
    const lng = result.location?.longitude || -1;
    return {
      lat,
      lng,
      formattedAddress,
      resultType: exactness,
    };
  }
}
