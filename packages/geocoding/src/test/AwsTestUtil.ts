import { vi } from 'vitest';

export class AwsTestUtil {
  static stubTestAwsEnv() {
    vi.stubEnv('AWS_PROFILE', 'runningdinner-local-dev-test');
    vi.stubEnv('AWS_REGION', 'eu-central-1');
  }
}
