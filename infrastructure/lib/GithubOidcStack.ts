import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

const GITHUB_DOMAIN = 'token.actions.githubusercontent.com';
const CLIENT_ID = 'sts.amazonaws.com';

export interface GithubOidcStackProps extends cdk.StackProps {
  table?: cdk.aws_dynamodb.Table;
}

export class GithubOidcStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: GithubOidcStackProps) {
    super(scope, id, props);

    const oidcProviderName = 'runningdinner-functions-github-oidc-provider';
    const githubProvider = new iam.OpenIdConnectProvider(this, oidcProviderName, {
      url: `https://${GITHUB_DOMAIN}`,
      clientIds: [CLIENT_ID],
    });

    const allowedRepositories = ['repo:Clemens85/runningdinner-functions:*'];

    const conditions: iam.Conditions = {
      StringEquals: {
        [`${GITHUB_DOMAIN}:aud`]: CLIENT_ID,
      },
      StringLike: {
        [`${GITHUB_DOMAIN}:sub`]: allowedRepositories,
      },
    };

    const { table } = props || {};
    const region = this.region;
    const accountId = this.account;

    const roleName = 'runningdinner-functions-github-oidc-role';
    const githubActionsRole = new iam.Role(this, roleName, {
      roleName: roleName,
      description: 'This role is used via GitHub Actions to build and deploy runningdinner-functions',
      maxSessionDuration: cdk.Duration.minutes(60),
      assumedBy: new iam.WebIdentityPrincipal(githubProvider.openIdConnectProviderArn, conditions),
      inlinePolicies: {
        LocalDevDynamoDbPolicy: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              actions: ['dynamodb:PutItem', 'dynamodb:GetItem', 'dynamodb:UpdateItem', 'dynamodb:DeleteItem', 'dynamodb:Query', 'dynamodb:Scan'],
              resources: [table?.tableArn || ''],
              effect: iam.Effect.ALLOW,
            }),
          ],
        }),
        SsmPolicy: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              actions: ['ssm:GetParameter', 'ssm:GetParameters', 'ssm:GetParametersByPath'],
              resources: [`arn:aws:ssm:${region}:${accountId}:parameter/runningdinner/googlemaps/*`],
              effect: iam.Effect.ALLOW,
            }),
          ],
        }),
      },
    });

    new cdk.CfnOutput(this, `${roleName}-arn`, {
      value: githubActionsRole.roleArn,
    });
    new cdk.CfnOutput(this, `${oidcProviderName}-arn`, {
      value: githubProvider.openIdConnectProviderArn,
    });
  }
}
