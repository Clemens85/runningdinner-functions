import { format, getUnixTime } from 'date-fns';

export function formatDateToUTC(date: Date) {
  return format(date, "yyyy-MM-dd'T'HH:mm:ss.SSSX");
}

export function toUnixTimestamp(date: Date) {
  return getUnixTime(date);
}
