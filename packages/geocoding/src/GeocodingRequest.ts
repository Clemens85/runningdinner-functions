import { Address } from './Address';

export type GeocodingEntityType = 'PARTICIPANT' | 'AFTER_PARTY_LOCATION';

export const ENTITY_TYPE_FIELD = 'entityType';
export const ENTITY_ID_FIELD = 'entityId';
export const ADMIN_ID_FIELD = 'adminId';
export const RESPONSE_QUEUE_URL_FIELD = 'responseQueueUrl';

export type GeocodingRequest = {
  address: Address;
  [ENTITY_TYPE_FIELD]: GeocodingEntityType;
  [ENTITY_ID_FIELD]: string;
  [ADMIN_ID_FIELD]: string;
  [RESPONSE_QUEUE_URL_FIELD]: string;
};
