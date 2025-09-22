import axios, { AxiosResponse } from 'axios';
import {
  LoginRequest,
  LoginResponse,
  UserResponse,
  AuthErrorResponse,
  MessageResponse
} from '../models';

const BASE_URL = 'http://localhost:8500';

export class AuthenticationApi {
  constructor(private basePath: string = BASE_URL) {}

  /**
   * Login
   * @param loginRequest ログイン認証とUTAGE連携確認
   */
  async login(loginRequest: LoginRequest): Promise<AxiosResponse<LoginResponse>> {
    return axios.post<LoginResponse>(
      `${this.basePath}/api/v1/auth/login`,
      loginRequest
    );
  }

  /**
   * Verify Token
   * @param authorization Authorization header with Bearer token
   */
  async verifyToken(authorization?: string): Promise<AxiosResponse<UserResponse>> {
    const headers: Record<string, string> = {};
    if (authorization) {
      headers.authorization = authorization;
    }

    return axios.get<UserResponse>(
      `${this.basePath}/api/v1/auth/verify`,
      { headers }
    );
  }

  /**
   * Logout
   * @param authorization Authorization header with Bearer token
   */
  async logout(authorization?: string): Promise<AxiosResponse<MessageResponse>> {
    const headers: Record<string, string> = {};
    if (authorization) {
      headers.authorization = authorization;
    }

    return axios.post<MessageResponse>(
      `${this.basePath}/api/v1/auth/logout`,
      {},
      { headers }
    );
  }

  /**
   * Test Error Response (Development only)
   */
  async testErrorResponse(): Promise<AxiosResponse<AuthErrorResponse>> {
    return axios.get<AuthErrorResponse>(
      `${this.basePath}/api/v1/auth/test-error`
    );
  }
}