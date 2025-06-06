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

  public static splitIntoChunks<T>(requests: T[], desiredChunkCount: number): T[][] {
    const chunkCount = Math.min(desiredChunkCount, requests.length);
    const chunks: T[][] = [];
    for (let i = 0; i < requests.length; i += chunkCount) {
      chunks.push(requests.slice(i, i + chunkCount));
    }
    return chunks;
  }
}
