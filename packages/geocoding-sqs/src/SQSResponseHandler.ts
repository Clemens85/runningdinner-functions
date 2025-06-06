import { SendMessageCommand } from '@aws-sdk/client-sqs';
import { sqsClient } from './aws/SQSClientFactory';
import { ADMIN_ID_FIELD, ENTITY_ID_FIELD, ENTITY_TYPE_FIELD, GeocodingResponse } from '@runningdinner/geocoding';
import { logger } from './aws/Logger';

export class SQSResponseHandler {
  public static async sendResponse(response: GeocodingResponse) {
    logger.info('Sending response to SQS...', {
      entityId: response.entityId,
      adminId: response.adminId,
      entityType: response.entityType,
      responseQueueUrl: response.responseQueueUrl,
    });
    const command = SQSResponseHandler.newSendMessageCommand(response);
    const sendResponse = await sqsClient.send(command);
    logger.info(`Sending finsihed with status code ${sendResponse.$metadata.httpStatusCode}`);
  }

  static newSendMessageCommand(response: GeocodingResponse): SendMessageCommand {
    return new SendMessageCommand({
      QueueUrl: response.responseQueueUrl,
      MessageBody: JSON.stringify(response),
      MessageAttributes: {
        [ENTITY_ID_FIELD]: {
          DataType: 'String',
          StringValue: response.entityId,
        },
        [ADMIN_ID_FIELD]: {
          DataType: 'String',
          StringValue: response.adminId,
        },
        [ENTITY_TYPE_FIELD]: {
          DataType: 'String',
          StringValue: response.entityType,
        },
      },
    });
  }
}
