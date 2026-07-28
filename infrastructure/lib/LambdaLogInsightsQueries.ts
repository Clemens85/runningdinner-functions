import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class LambdaLogInsightsQueries {
  /**
   * Creates a standard set of CloudWatch Logs Insights saved queries for the given log groups.
   *
   * Both TypeScript (@aws-lambda-powertools/logger) and Python (aws_lambda_powertools) lambdas are
   * supported. Note: TypeScript Powertools emits level "WARN", Python Powertools emits "WARNING",
   * so both are included in warning-level filters.
   *
   * @param scope        - CDK construct scope (e.g. the NodeJsLambda or PythonLambda construct)
   * @param queryPrefix  - Name prefix for all queries, e.g. "runningdinner/geocoding-http-dev"
   * @param logGroups    - Log groups to attach the queries to
   */
  static create(scope: Construct, queryPrefix: string, logGroups: cdk.aws_logs.ILogGroup[]) {
    // Derive a CDK-safe ID prefix (slashes are not valid in construct IDs)
    const idPrefix = queryPrefix.replace(/\//g, '-');

    new cdk.aws_logs.QueryDefinition(scope, `${idPrefix}-query-recent-logs`, {
      queryDefinitionName: `${queryPrefix}/recent-logs`,
      logGroups,
      queryString: new cdk.aws_logs.QueryString({
        fields: ['@timestamp', 'level', 'message', 'service', 'function_name', 'function_request_id', 'cold_start'],
        sort: '@timestamp desc',
        limit: 500,
      }),
    });

    new cdk.aws_logs.QueryDefinition(scope, `${idPrefix}-query-errors-and-warnings`, {
      queryDefinitionName: `${queryPrefix}/errors-and-warnings`,
      logGroups,
      queryString: new cdk.aws_logs.QueryString({
        fields: ['@timestamp', 'level', 'message', 'service', 'function_name', 'function_request_id', 'error.message', 'error.stack'],
        // TypeScript Powertools uses "WARN", Python Powertools uses "WARNING"
        filterStatements: ['level in ["ERROR", "WARN", "WARNING"]'],
        sort: '@timestamp desc',
        limit: 200,
      }),
    });

    new cdk.aws_logs.QueryDefinition(scope, `${idPrefix}-query-errors-only`, {
      queryDefinitionName: `${queryPrefix}/errors-only`,
      logGroups,
      queryString: new cdk.aws_logs.QueryString({
        fields: ['@timestamp', 'message', 'service', 'function_name', 'function_request_id', 'error.message', 'error.stack'],
        filterStatements: ['level = "ERROR"'],
        sort: '@timestamp desc',
        limit: 100,
      }),
    });

    new cdk.aws_logs.QueryDefinition(scope, `${idPrefix}-query-cold-starts`, {
      queryDefinitionName: `${queryPrefix}/cold-starts`,
      logGroups,
      queryString: new cdk.aws_logs.QueryString({
        fields: ['@timestamp', 'message', 'service', 'function_name', 'function_memory_size', 'function_request_id'],
        filterStatements: ['cold_start = 1'],
        sort: '@timestamp desc',
        limit: 100,
      }),
    });

    new cdk.aws_logs.QueryDefinition(scope, `${idPrefix}-query-error-rate`, {
      queryDefinitionName: `${queryPrefix}/error-rate-per-minute`,
      logGroups,
      queryString: new cdk.aws_logs.QueryString({
        filterStatements: ['level = "ERROR"'],
        stats: 'count(*) as errorCount by bin(1m)',
        sort: '@timestamp desc',
      }),
    });
  }
}
