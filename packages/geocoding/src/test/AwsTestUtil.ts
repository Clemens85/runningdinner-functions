import { vi } from 'vitest';

export class AwsTestUtil {
  static stubTestAwsEnv() {
    // In CI (GitHub Actions), AWS credentials are provided via OIDC
    // Only set AWS_PROFILE for local development
    if (!process.env.CI) {
      vi.stubEnv('AWS_PROFILE', 'runningdinner-local-dev-test');
    }
    vi.stubEnv('AWS_REGION', 'eu-central-1');
  }
}
