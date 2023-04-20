// Add     "@aws-sdk/client-ssm": "3.303.0" as devDependency to package.json again for including AWS SDK before uncommenting this code

// const { SSMClient, GetParameterCommand } = require("@aws-sdk/client-ssm")
// const {getAwsBaseParams} = require("./baseAwsParams");
//
// const client = new SSMClient(getAwsBaseParams());
//
// const getSsmParameterCached = (params, cacheTime) => {
//   let lastRefreshed = undefined;
//   let lastResult = undefined;
//   let queue = Promise.resolve();
//   return () => {
//     // serialize async calls
//     const res = queue.then(async () => {
//       const currentTime = new Date().getTime();
//       // check if cache is fresh enough
//       if (lastResult === undefined ||
//         lastRefreshed + cacheTime < currentTime) {
//         // refresh the value
//         const getParameterCommand = new GetParameterCommand(params);
//         lastResult = await client.send(getParameterCommand);
//         //lastResult = await ssm.getParameter(params).promise();
//         lastRefreshed = currentTime;
//       }
//       return lastResult;
//     });
//     queue = res.catch(() => {});
//     return res;
//   };
// };
//
// module.exports = {
//   getSsmParameterCached
// };
