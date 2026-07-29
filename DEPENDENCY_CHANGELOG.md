## 2026-07-28 – Dependency Update Run

### Updated

| Package                          | Location               | Old Version | New Version | Notes                                                                                                                                                                       |
| -------------------------------- | ---------------------- | ----------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| axios                            | root                   | 1.13.2      | 1.18.1      | Minor bump, no breaking changes                                                                                                                                             |
| date-fns                         | root                   | 4.1.0       | 4.4.0       | Minor bump, no breaking changes                                                                                                                                             |
| lodash-es                        | root                   | 4.17.21     | 4.18.1      | Minor bump, no breaking changes                                                                                                                                             |
| @aws-lambda-powertools/logger    | root                   | 2.19.1      | 2.34.0      | Minor bump, no breaking changes                                                                                                                                             |
| http-errors                      | root                   | 2.0.0       | 2.0.1       | Patch bump                                                                                                                                                                  |
| @types/aws-lambda                | root                   | 8.10.149    | 8.10.162    | Patch bump                                                                                                                                                                  |
| @types/http-errors               | root                   | 2.0.4       | 2.0.5       | Patch bump                                                                                                                                                                  |
| eslint-plugin-prettier           | root                   | 5.5.4       | 5.5.6       | Patch bump                                                                                                                                                                  |
| eslint-plugin-unused-imports     | root                   | 4.3.0       | 4.4.1       | Minor bump                                                                                                                                                                  |
| prettier                         | root                   | 3.6.2       | 3.9.6       | Minor bump                                                                                                                                                                  |
| typescript-eslint                | root                   | 8.46.2      | 8.65.0      | Minor bump                                                                                                                                                                  |
| vitest                           | root                   | 4.0.14      | 4.1.10      | Minor bump                                                                                                                                                                  |
| typescript                       | root                   | 5.8.3       | 6.0.3       | **MAJOR** – added `ignoreDeprecations: "6.0"` to tsconfig for `moduleResolution: "node"` deprecation; stays below TS 7 to remain compatible with typescript-eslint (<6.1.0) |
| uuid                             | root                   | 11.1.0      | 14.0.1      | **MAJOR** – named exports (v4, v7, etc.) unchanged                                                                                                                          |
| @types/node                      | root                   | 22.15.18    | 22.20.1     | **MAJOR** (latest 22.x); pinned to Node 22 to match Lambda runtime; added `"types": ["node"]` to tsconfig.json to restore `process` global                                  |
| eslint-plugin-simple-import-sort | root                   | 12.1.1      | 14.0.0      | **MAJOR** – no config changes needed                                                                                                                                        |
| globals                          | root                   | 15.9.0      | 17.8.0      | **MAJOR** – data-only package, no API changes                                                                                                                               |
| vite                             | root                   | 7.2.6       | 8.1.5       | **MAJOR** – Rolldown merge; vitest config unchanged, tests pass                                                                                                             |
| @aws-sdk/client-dynamodb         | packages/geocoding     | 3.812.0     | 3.1097.0    | Large patch jump within v3, backward compatible                                                                                                                             |
| @aws-sdk/client-ssm              | packages/geocoding     | 3.812.0     | 3.1097.0    | Large patch jump within v3, backward compatible                                                                                                                             |
| @aws-sdk/lib-dynamodb            | packages/geocoding     | 3.812.0     | 3.1097.0    | Large patch jump within v3, backward compatible                                                                                                                             |
| @aws-sdk/client-sqs              | packages/geocoding-sqs | 3.812.0     | 3.1097.0    | Large patch jump within v3, backward compatible                                                                                                                             |

### Skipped / Blocked

| Package     | Reason                                                                                                                             |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| eslint      | 9.39.1 → 10.x requires Node.js ≥22.13.0; current runtime is v22.12.0                                                               |
| @eslint/js  | Coupled with eslint, skipped for same reason                                                                                       |
| typescript  | Stopped at 6.0.3, not 7.0.2 – typescript-eslint@8.65.0 peer dep is `<6.1.0`; TS 7 also removes `moduleResolution: "node"` entirely |
| @types/node | Stopped at 22.x (22.20.1), not 26.x – Lambda runtime is Node 22; using Node 26 types risks referencing APIs absent at runtime      |
| @types/uuid | Kept at 9.0.8 – uuid v14 bundles its own types                                                                                     |
