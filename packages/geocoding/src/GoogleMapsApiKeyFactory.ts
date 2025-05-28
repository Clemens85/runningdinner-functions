import { GetParameterCommand, GetParameterCommandOutput } from '@aws-sdk/client-ssm';
import { ssmClient } from './aws/SSMClientFactory';
import { logger } from './aws/Logger';

const SSM_PARAMETER = '/runningdinner/googlemaps/apikey';

export class GoogleMapsApiKeyFactory {
  private static instance: GoogleMapsApiKeyFactory;

  private ssmPromise: Promise<GetParameterCommandOutput>;

  private constructor() {
    this.ssmPromise = this.fetchSsmParameter(SSM_PARAMETER);
  }

  public static getInstance(): GoogleMapsApiKeyFactory {
    if (!GoogleMapsApiKeyFactory.instance) {
      GoogleMapsApiKeyFactory.instance = new GoogleMapsApiKeyFactory();
    }
    return GoogleMapsApiKeyFactory.instance;
  }

  public async getApiKey(): Promise<string> {
    let response: GetParameterCommandOutput;
    try {
      response = await this.ssmPromise;
    } catch (error) {
      this.ssmPromise = this.fetchSsmParameter(SSM_PARAMETER);
      try {
        response = await this.ssmPromise;
      } catch (innerError) {
        const errorMessage = `Failed to fetch SSM parameter (${SSM_PARAMETER}): ${innerError}`;
        logger.error(errorMessage);
        throw new Error(errorMessage);
      }
    }
    const result = response?.Parameter?.Value;
    if (!result) {
      logger.error(`Google Maps API key not found in ${SSM_PARAMETER}`);
      throw new Error(`Google Maps API key not found in ${SSM_PARAMETER}`);
    }
    return result;
  }

  private async fetchSsmParameter(parameterName: string): Promise<GetParameterCommandOutput> {
    return ssmClient.send(
      new GetParameterCommand({
        Name: parameterName,
        WithDecryption: true,
      }),
    );
  }
}
