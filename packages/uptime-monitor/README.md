# Uptime monitor

This Lambda performs a `GET` request against a public HTTPS endpoint. Network errors, timeouts, and non-2xx responses fail the invocation so the CloudWatch alarm in `UptimeMonitorStack` can notify the configured SNS email subscriber.

Deploy the stack with:

```bash
cd infrastructure
./deploy-uptime-monitor.sh prod
```

AWS sends a confirmation request when the SNS email subscription is created. Alerts are not delivered until that subscription is confirmed.

The EventBridge rule checks `https://runyourdinner.eu/rest/frontend/v1/runningdinner` every two hours. The request timeout defaults to 10 seconds and the Lambda timeout is 15 seconds.
