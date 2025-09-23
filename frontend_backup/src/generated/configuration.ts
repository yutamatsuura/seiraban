import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

export interface Configuration {
  basePath?: string;
  baseOptions?: AxiosRequestConfig;
  accessToken?: string | (() => string);
}

export class ApiClient {
  private instance: AxiosInstance;
  private _configuration: Configuration;

  constructor(configuration: Configuration = {}) {
    this._configuration = {
      basePath: 'http://localhost:8500',
      ...configuration,
    };

    this.instance = axios.create({
      baseURL: this._configuration.basePath,
      ...this._configuration.baseOptions,
    });

    // Request interceptor to add authorization header
    this.instance.interceptors.request.use((config: any) => {
      const token = this.getAccessToken();
      if (token) {
        config.headers = config.headers || {};
        config.headers.authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.instance.interceptors.response.use(
      (response: any) => response,
      (error: any) => {
        // Handle common error responses
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login or refresh token
          console.warn('Unauthorized access - token may be expired');
        }
        return Promise.reject(error);
      }
    );
  }

  get configuration(): Configuration {
    return this._configuration;
  }

  set configuration(configuration: Configuration) {
    this._configuration = configuration;
  }

  get axios(): AxiosInstance {
    return this.instance;
  }

  private getAccessToken(): string | undefined {
    if (typeof this._configuration.accessToken === 'function') {
      return this._configuration.accessToken();
    }
    return this._configuration.accessToken;
  }

  setAccessToken(token: string | undefined): void {
    this._configuration.accessToken = token;
  }
}

// Default API client instance
export const apiClient = new ApiClient();