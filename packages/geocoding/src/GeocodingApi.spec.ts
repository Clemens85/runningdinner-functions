import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';

import { Address } from './Address';
import { GeocodingApi } from './GeocodingApi';
import { AwsTestUtil } from './test/AwsTestUtil';

describe('GeocodingResultCacheRepository', () => {
  beforeEach(() => {
    AwsTestUtil.stubTestAwsEnv();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  test('GeocodingApi finds geocoding result', async () => {
    const addressWithoutStreetNr = newAddresss();
    addressWithoutStreetNr.streetNr = '';
    let response = await GeocodingApi.fetchGeocode(addressWithoutStreetNr);
    expect(response).toBeDefined();
    expect(response?.lat).toBeGreaterThan(47);
    expect(response?.lng).toBeGreaterThan(7.8);
    expect(response?.resultType).toBe('NOT_EXACT');

    const addressExact = newAddresss();
    response = await GeocodingApi.fetchGeocode(addressExact);
    expect(response).toBeDefined();
    expect(response?.lat).toBeGreaterThan(47);
    expect(response?.lng).toBeGreaterThan(7.8);
    expect(response?.resultType).toBe('EXACT');
  });

  function newAddresss(): Address {
    return {
      street: 'Hauptstrasse',
      streetNr: '1',
      zip: '79104',
      cityName: 'Freiburg',
    };
  }
});
