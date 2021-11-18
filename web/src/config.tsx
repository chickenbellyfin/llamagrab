const env = process.env.NODE_ENV;

let baseUrl = ""

if (env === 'development') {
  baseUrl = "http://localhost:8000";
}

export const BASE_URL = baseUrl;
