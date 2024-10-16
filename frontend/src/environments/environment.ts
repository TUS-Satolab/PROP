// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
  production: process.env.PRODUCTION === 'true' || false,
  apiKey: process.env.BACKEND_APIKEY || 'DUMMY',
  fileSizeLimit: Number(process.env.FILE_SIZE_LIMIT) || 10000000,
  baseUrl: process.env.BASE_URL || 'http://localhost:5004',
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/dist/zone-error';  // Included with Angular CLI.
