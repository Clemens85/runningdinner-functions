import { logger } from './aws/Logger';
import { v4 as uuidv4 } from 'uuid';

export class Util {
  public static logAndThrowError(message: string): never {
    logger.error(message);
    throw new Error(message);
  }

  public static newUuid() {
    return uuidv4();
  }
}
