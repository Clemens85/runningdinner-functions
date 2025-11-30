import { Address, ENTITY_ID_FIELD, ENTITY_TYPE_FIELD, GeocodingEntityType } from '@runningdinner/geocoding';

export type HttpGeocodeBatchRequest = {
  adminId: string;
  requests: HttpGeocodeRequestLine[];
};

export type HttpGeocodeRequestLine = {
  [ENTITY_ID_FIELD]: string;
  [ENTITY_TYPE_FIELD]: GeocodingEntityType;
} & Address;
