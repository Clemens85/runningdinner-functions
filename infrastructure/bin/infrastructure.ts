#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { GeocodingStack } from "../lib/GeocodingStack";
import { ENVIRONMENT } from "../lib/Environment";
import { LocalDevUserStack } from "../lib/LocalDevUserStack";
import { RouteOptimizationStack } from "../lib/RouteOptimizationStack";

const app = new cdk.App();

// Create the dev user stack first (if needed)
const devUserStack = new LocalDevUserStack(app, "LocalDevUserStack", {});

new GeocodingStack(app, "GeocodingStack", {
  localDevUser: devUserStack.localDevUser,
});

new RouteOptimizationStack(app, "RouteOptimizationStack", {
  localDevUser: devUserStack.localDevUser,
});

cdk.Tags.of(app).add("stage", ENVIRONMENT.stage);

/* If you don't specify 'env', this stack will be environment-agnostic.
 * Account/Region-dependent features and context lookups will not work,
 * but a single synthesized template can be deployed anywhere. */
/* Uncomment the next line to specialize this stack for the AWS Account
 * and Region that are implied by the current CLI configuration. */
// env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
/* Uncomment the next line if you know exactly what Account and Region you
 * want to deploy the stack to. */
// env: { account: '123456789012', region: 'us-east-1' },
/* For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html */
