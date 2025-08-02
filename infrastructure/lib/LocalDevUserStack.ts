import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import { LocalDevUser } from "./LocalDevUser";
import { ENVIRONMENT } from "./Environment";

export class LocalDevUserStack extends cdk.Stack {
  public readonly localDevUser: LocalDevUser;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Only create the dev user in dev stage
    if (ENVIRONMENT.isDevStage) {
      this.localDevUser = new LocalDevUser(this, "geocoding-local-dev");
    }
  }
}
