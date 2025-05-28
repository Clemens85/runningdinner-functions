import { GeocodingResult } from '../GeocodingResult';

export type GeocodingCacheItemDbAttributes = {} & GeocodingResult;

export type GeocodingCacheItemDb = {
  pk: string;
  sk: string;
  createdAt: string;
  attributes: GeocodingCacheItemDbAttributes;
  ttl?: number;
};
