import { describe, expect, test } from 'vitest';

import { checkEndpoint } from './index';

describe('uptime monitor', () => {
  test('RunningDinner API is publicly available', async () => {
    const endpointUrl = 'https://runyourdinner.eu/rest/frontend/v1/runningdinner';

    await expect(checkEndpoint(endpointUrl)).resolves.toBeUndefined();
  });
});
