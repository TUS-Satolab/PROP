/*
Set the environment variables for the frontend application.
For production, set the variables here as well BUT DON'T COMMIT THEM.
In the end, that was the only solution that was implementable in a reasonabl time.
*/

export const environment = {
  production: false,
  apiKey: 'DUMMY',
  fileSizeLimit: 10000000,
  baseUrl: 'http://localhost:5004',
};
