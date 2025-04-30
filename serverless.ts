import type { AWS } from "@serverless/typescript";

import functions from "@/infrastructure/serverless/functions";
import resources from "@/infrastructure/serverless/resources";

const serverlessConfiguration: AWS = {
  service: "bgc-name-checker-v2",
  frameworkVersion: "3",
  plugins: [
    "serverless-better-credentials",
    "serverless-esbuild",
    "serverless-iam-roles-per-function",
    "api-gateway-stage-tag-plugin",
  ],
  configValidationMode: "off",
  provider: {
    memorySize: 256,
    name: "aws",
    profile: "${self:custom.stage}-bgc",
    region: "us-east-1",
    versionFunctions: false,
    runtime: "nodejs20.x",
    apiGateway: {
      minimumCompressionSize: 1024,
      shouldStartNameWithService: true,
      apiKeySourceType: "AUTHORIZER",
    },
    architecture: "arm64",
    logs: {
      restApi: {
        accessLogging: true,
        executionLogging: false,
        format:
          '{ "requestId":"$context.requestId", "ip": "$context.identity.sourceIp", "caller":"$context.identity.caller", "user":"$context.identity.user","requestTime":"$context.requestTime", "httpMethod":"$context.httpMethod","resourcePath":"$context.resourcePath", "status":"$context.status","protocol":"$context.protocol", "responseLength":"$context.responseLength" }',
      },
    },
    environment: {
      AWS_NODEJS_CONNECTION_REUSE_ENABLED: "1",
      DISCORD_URL: "${self:custom.discordsUrls.${self:custom.stage}}",
      DOMAIN_URL: { Ref: "RestDomainName" },
      DYNAMO_DB_SEARCHES_TABLE: { Ref: "dynamodbSearchesTable" },
      DYNAMO_DB_PROVIDERS_TABLE: { Ref: "dynamodbProvidersTable" },
      NODE_OPTIONS: "--enable-source-maps --stack-trace-limit=1000",
      SHORT_SERVICE_NAME: "${self:custom.shortServiceName}",
      STAGE: "${self:custom.stage}",
      CRAWLER_REGISTER_QUEUE_URL:
        "${cf:bgc-crawlers-${self:custom.stage}.CrawlRegisterQueueURL}",
      PROCESS_INFORMATION_CHECKER_RESULT_BASE_URL:
        "name-checker-v2.${cf:bgc-infra-${self:custom.stage}.NewHostedZoneName}",
      DISCORD_ERROR_CHANNEL_URL:
        "${self:custom.discordsUrls.${self:custom.stage}}",
      INFORMATION_CHECKER_CREATE_SEARCH_LAMBDA_NAME:
        "bgc-information-checker-HttpCreateSearch",
    },
    vpc: {
      subnetIds: [
        "${cf:bgc-infra-${self:custom.stage}.StaticIpPrivatePrivateSubnet1Id}",
        "${cf:bgc-infra-${self:custom.stage}.StaticIpPrivatePrivateSubnet2Id}",
        "${cf:bgc-infra-${self:custom.stage}.StaticIpPrivatePrivateSubnet3Id}",
      ],
      securityGroupIds: [
        "${cf:bgc-infra-${self:custom.stage}.StaticIpPrivateSecurityGroupId}",
      ],
    },
  },
  functions: { ...functions },
  resources: { ...resources },
  package: {
    individually: true,
    excludeDevDependencies: true,
  },
  custom: {
    stage: "${opt:stage, 'dev'}",
    shortServiceName: "name-checker-v2",
    authenticator: {
      arn: "${cf:bgc-access-controller-${self:custom.stage}.AuthenticatorLambdaArn}",
      resultTtlInSeconds: 500,
      type: "request",
      managedExternally: true,
      identitySource:
        "method.request.header.Authorization, context.path,   context.httpMethod",
    },
    "authenticator-websocket": {
      arn: "${cf:bgc-access-controller-${self:custom.stage}.AuthenticatorLambdaArn}",
      identitySource: ["route.request.querystring.Authorization"],
    },
    discordsUrls: {
      dev: "https://discord.com/api/webhooks/1204789047646621726/bg_BnuVONTeNtjnPoGJPfvmY3cQ4ZM0HVLt4Tn9ExyNN8VuoSP2Bn5f7qSI2Fwa4nDg6",
      staging:
        "https://discord.com/api/webhooks/1204789047646621726/bg_BnuVONTeNtjnPoGJPfvmY3cQ4ZM0HVLt4Tn9ExyNN8VuoSP2Bn5f7qSI2Fwa4nDg6",
      production:
        "https://discordapp.com/api/webhooks/1019757515036172398/nG8bnEj9XQYLEPlA0sxJJaWS12KeLXMdgWN2nH6su4quaB_fgP4TvIlbRJsIKhPLVIDG",
    },
    esbuild: {
      bundle: true,
      minify: false,
      sourcemap: true,
      target: "node20",
      exclude: [
        "@aws-sdk/client-s3",
        "@aws-sdk/client-sns",
        "@aws-sdk/client-sqs",
      ],
    },
    "serverless-offline": {
      noPrependStageInUrl: true,
      localEnvironment: true,
    },
    apiStageTags: {
      orchestrator: "false",
      type: "private",
    },
  },
};

module.exports = serverlessConfiguration;
