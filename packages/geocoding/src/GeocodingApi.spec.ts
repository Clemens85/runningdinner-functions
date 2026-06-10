import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';

import { Address } from './Address';
import { GeocodingApi } from './GeocodingApi';
import { AwsTestUtil } from './test/AwsTestUtil';

describe('GeocodingApi', { timeout: 60 * 1000 * 10 }, () => {
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

  test('GeocodingApi handles address variants with letters in streetNr correctly', async() => {
    const addressVariant1 = {
      streetNr: '2 a',
      street: 'Kästrich (Mainz)',
      zip: '55116',
      cityName: 'Mainz'
    }

    const addressVariant2 = {
      streetNr: '2a',
      street: 'Kästrich',
      zip: '55116',
      cityName: 'Mainz'
    }

    const expectedLat = 49.9948252;
    const expectedLng = 8.2667321;

    let response = await GeocodingApi.fetchGeocode(addressVariant1);
    expect(response).toBeDefined();
    expect(response?.lat).toBe(expectedLat)
    expect(response?.lng).toBe(expectedLng);
    expect(response?.resultType).toBe('EXACT');

    response = await GeocodingApi.fetchGeocode(addressVariant2);
    expect(response).toBeDefined();
    expect(response?.lat).toBe(expectedLat)
    expect(response?.lng).toBe(expectedLng);
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
