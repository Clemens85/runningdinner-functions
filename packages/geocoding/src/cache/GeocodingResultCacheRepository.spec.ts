import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import { AwsTestUtil } from '../test/AwsTestUtil';
import { GeocodingResultCacheRepository } from './GeocodingResultCacheRepository';
import { Util } from '../Util';
import { addMinutes } from 'date-fns';
import { toUnixTimestamp } from '../DateUtil';

describe('GeocodingResultCacheRepository', () => {
  beforeEach(() => {
    AwsTestUtil.stubTestAwsEnv();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  test('GeocodingResultCacheRepository finds and stores geocoding results', async () => {
    const addressCacheKey = 'testaddress_' + Util.newUuid().split('-')[0];

    let cachedResult = await GeocodingResultCacheRepository.findGeocodingResultByAddressCacheKey(addressCacheKey);

    expect(cachedResult).toBeNull();

    await GeocodingResultCacheRepository.saveGeocodingResult(
      addressCacheKey,
      {
        lat: 2.5,
        lng: 1.7575,
        formattedAddress: 'Test Address',
        resultType: 'EXACT',
      },
      customTtl(),
    );

    cachedResult = await GeocodingResultCacheRepository.findGeocodingResultByAddressCacheKey(addressCacheKey);
    expect(cachedResult).toBeDefined();
    expect(cachedResult?.lat).toBe(2.5);
    expect(cachedResult?.lng).toBe(1.7575);
    expect(cachedResult?.formattedAddress).toBe('Test Address');
    expect(cachedResult?.resultType).toBe('EXACT');
  });
});

function customTtl(): number {
  const now = new Date();
  const expireDate = addMinutes(now, 2);
  return toUnixTimestamp(expireDate);
}
