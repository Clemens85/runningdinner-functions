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
  location: {
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

    const response = await axios.get(url, {
      headers: { 'X-Goog-Api-Key': apiKey },
    });
    if (response.status !== 200) {
      Util.logAndThrowError(`Error fetching geocode: ${response.statusText}`);
    }

    const data = response.data;
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

/**
 *
 *
 * curl -H "X-Goog-Api-Key: <KEY>" \
 * "https://geocode.googleapis.com/v4/geocode/address/2a+K%C3%A4strich,+55116,+Mainz"
 *
 * => Response:
 *
 * {
 *   "results": [
 *     {
 *       "place": "places/ChIJm_kYUR6XvUcRNbEvf2WIj1U",
 *       "placeId": "ChIJm_kYUR6XvUcRNbEvf2WIj1U",
 *       "location": {
 *         "latitude": 49.9948252,
 *         "longitude": 8.2667321
 *       },
 *       "granularity": "ROOFTOP",
 *       "viewport": {
 *         "low": {
 *           "latitude": 49.9934590697085,
 *           "longitude": 8.265384919708497
 *         },
 *         "high": {
 *           "latitude": 49.9961570302915,
 *           "longitude": 8.2680828802915016
 *         }
 *       },
 *       "bounds": {
 *         "low": {
 *           "latitude": 49.9947601,
 *           "longitude": 8.2666425999999991
 *         },
 *         "high": {
 *           "latitude": 49.994880599999995,
 *           "longitude": 8.2668252
 *         }
 *       },
 *       "formattedAddress": "Kästrich 2A, 55116 Mainz, Deutschland",
 *       "postalAddress": {
 *         "regionCode": "DE",
 *         "languageCode": "en",
 *         "postalCode": "55116",
 *         "locality": "Mainz",
 *         "addressLines": [
 *           "Kästrich 2A"
 *         ]
 *       },
 *       "addressComponents": [
 *         {
 *           "longText": "2A",
 *           "shortText": "2A",
 *           "types": [
 *             "street_number"
 *           ]
 *         },
 *         {
 *           "longText": "Kästrich",
 *           "shortText": "Kästrich",
 *           "types": [
 *             "route"
 *           ],
 *           "languageCode": "de"
 *         },
 *         {
 *           "longText": "Mainz",
 *           "shortText": "MZ",
 *           "types": [
 *             "locality",
 *             "political"
 *           ],
 *           "languageCode": "de"
 *         },
 *         {
 *           "longText": "Mainz",
 *           "shortText": "Mainz",
 *           "types": [
 *             "administrative_area_level_3",
 *             "political"
 *           ],
 *           "languageCode": "de"
 *         },
 *         {
 *           "longText": "Rheinland-Pfalz",
 *           "shortText": "RP",
 *           "types": [
 *             "administrative_area_level_1",
 *             "political"
 *           ],
 *           "languageCode": "de"
 *         },
 *         {
 *           "longText": "Deutschland",
 *           "shortText": "DE",
 *           "types": [
 *             "country",
 *             "political"
 *           ],
 *           "languageCode": "de"
 *         },
 *         {
 *           "longText": "55116",
 *           "shortText": "55116",
 *           "types": [
 *             "postal_code"
 *           ]
 *         }
 *       ],
 *       "types": [
 *         "premise",
 *         "street_address"
 *       ]
 *     }
 *   ]
 * }
 *
 */
