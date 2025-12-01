import * as cdk from 'aws-cdk-lib';
import { Table } from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';

export class CommonUtils {
  private readonly parentStack: cdk.Stack;

  constructor(parentStack: cdk.Stack) {
    this.parentStack = parentStack;
  }

  public allowParameterStoreAccess(lambdaFunctions: Array<lambda.Function>, paramStorePathPrefix: string): iam.PolicyStatement[] {
    const region = this.parentStack.region;
    const accountId = this.parentStack.account;

    const actions = ['ssm:GetParameter', 'ssm:GetParameters', 'ssm:GetParametersByPath'];
    const ssmPolicy = new iam.PolicyStatement({
      actions,
      resources: [`arn:aws:ssm:${region}:${accountId}:parameter${paramStorePathPrefix}`],
    });

    const kmsPolicy = new iam.PolicyStatement({
      actions: ['kms:Decrypt', 'kms:Encrypt'],
      resources: [`arn:aws:kms:${region}:${accountId}:key/*`],
    });

    for (const lambdaFunc of lambdaFunctions) {
      lambdaFunc.addToRolePolicy(ssmPolicy);
      lambdaFunc.addToRolePolicy(kmsPolicy);
    }

    return [ssmPolicy, kmsPolicy];
  }

  public grantReadWriteDataToTable(lambdaFunctions: Array<lambda.Function>, table: Table) {
    for (const lambdaFunc of lambdaFunctions) {
      table.grantReadWriteData(lambdaFunc);
    }
  }
}
