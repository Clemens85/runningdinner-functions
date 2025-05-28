import { GeocodingRequest } from './GeocodingRequest';
import { GeocodingResult } from './GeocodingResult';

export type GeocodingResponse = {
  geocodingResult: GeocodingResult | null;
} & Pick<GeocodingRequest, 'entityId' | 'adminId' | 'entityType' | 'responseQueueUrl'>;
