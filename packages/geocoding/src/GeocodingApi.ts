import axios from 'axios';
import { Address } from './Address';
import { EXACTNESS_TYPE, GeocodingResult } from './GeocodingResult';
import { GoogleMapsApiKeyFactory } from './GoogleMapsApiKeyFactory';
import { logger } from './aws/Logger';
import { Validator } from './Validator';
import { Util } from './Util';

const googleMapsApiKeyFactory = GoogleMapsApiKeyFactory.getInstance();

type GeocodingApiSingleResult = {
  formatted_address: string;
  geometry: {
    location_type: string;
    location: {
      lat: number;
      lng: number;
    };
  };
};

export class GeocodingApi {
  public static async fetchGeocode(address: Address): Promise<GeocodingResult | null> {
    logger.info(`Fetching API key for Google Maps...`);
    const apiKey = await googleMapsApiKeyFactory.getApiKey();

    const addressQueryParam = GeocodingApi.getAddressQueryParam(address);
    logger.info(`Fetching geocode for address: ${addressQueryParam}`);
    const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${addressQueryParam}&key=${apiKey}`;

    const response = await axios.get(url);
    if (response.status !== 200) {
      Util.logAndThrowError(`Error fetching geocode: ${response.statusText}`);
    }

    const data = response.data;
    if (!data) {
      Util.logAndThrowError('No data received from geocode API');
    }

    if (data.status === 'ZERO_RESULTS') {
      logger.warn(`No results found for address: ${addressQueryParam}`);
      return null;
    }
    if (data.status !== 'OK') {
      Util.logAndThrowError(`Error in geocode response: ${data.status}`);
    }

    const results = (data.results || []) as GeocodingApiSingleResult[];
    if (results.length === 0) {
      logger.error(`Results array was empty for address: ${addressQueryParam}`);
      return null;
    }

    const result = GeocodingApi.findBestResult(results);

    return GeocodingApi.mapApiResultToGeocodingResult(result);
  }

  public static getAddressQueryParam(address: Address): string {
    const { street, streetNr, cityName, zip, country } = address;
    Validator.validateAddress(address);
    const addressString = `${street} ${streetNr}, ${cityName}, ${zip}${country ? `, ${country}` : ''}`;
    return encodeURIComponent(addressString);
  }

  static findBestResult(results: GeocodingApiSingleResult[]): GeocodingApiSingleResult {
    let bestResult = results.find((result) => result.geometry?.location_type === 'ROOFTOP');
    if (!bestResult) {
      bestResult = results.find((result) => result.geometry?.location_type === 'APPROXIMATE');
    }
    if (!bestResult) {
      bestResult = results[0];
    }
    return bestResult;
  }

  static mapApiResultToGeocodingResult(result: GeocodingApiSingleResult): GeocodingResult {
    const formattedAddress = result.formatted_address;

    let exactness: EXACTNESS_TYPE = 'NONE';
    if (result.geometry?.location_type === 'ROOFTOP') {
      exactness = 'EXACT';
    } else if (result.geometry?.location_type === 'APPROXIMATE' ||
               result.geometry?.location_type === 'GEOMETRIC_CENTER' ||
               result.geometry?.location_type === 'RANGE_INTERPOLATED') {
      exactness = 'NOT_EXACT';
    }

    logger.info(`GOT LOCATION TYPE ${result.geometry?.location_type} for address: ${formattedAddress}, exactness: ${exactness}`);

    const location = result.geometry?.location;
    const lat = location?.lat || -1;
    const lng = location?.lng || -1;
    return {
      lat,
      lng,
      formattedAddress,
      resultType: exactness,
    };
  }
}
