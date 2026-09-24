import type { ScheduledHandler } from 'aws-lambda';
import axios from 'axios';

import { logger } from './aws/Logger';

const DEFAULT_TIMEOUT_MS = 10_000;

export async function checkEndpoint(endpointUrl: string, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<void> {
  const response = await axios.get(endpointUrl, {
    timeout: timeoutMs,
    headers: {
      'user-agent': 'runningdinner-uptime-monitor/1.0',
    },
  });

  logger.info('Health check succeeded', {
    endpointUrl,
    statusCode: response.status,
  });
}

export const handler: ScheduledHandler = async () => {
  const endpointUrl = process.env.ENDPOINT_URL;
  if (!endpointUrl) {
    throw new Error('ENDPOINT_URL environment variable is required');
  }

  const timeoutMs = Number(process.env.REQUEST_TIMEOUT_MS ?? DEFAULT_TIMEOUT_MS);
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new Error('REQUEST_TIMEOUT_MS must be a positive number');
  }

  await checkEndpoint(endpointUrl, timeoutMs);
};
