export type EXACTNESS_TYPE = 'EXACT' | 'NOT_EXACT' | 'NONE';

export type GeocodingResult = {
  lat: number;
  lng: number;
  formattedAddress: string;
  resultType: EXACTNESS_TYPE;
};
