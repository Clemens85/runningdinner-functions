export type HttpResponse = {
  statusCode?: number | undefined;
  headers?:
    | {
    [header: string]: boolean | number | string;
  }
    | undefined;
  body?: string | undefined;
  isBase64Encoded?: boolean | undefined;
  cookies?: string[] | undefined;
};