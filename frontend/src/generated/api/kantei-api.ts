import axios, { AxiosResponse } from 'axios';
import {
  KanteiCalculateRequest,
  KanteiCalculationResponse,
  KanteiTemplatesResponse,
  MessageResponse
} from '../models';

const BASE_URL = 'http://localhost:8500';

export class KanteiApi {
  constructor(private basePath: string = BASE_URL) {}

  /**
   * 九星気学・姓名判断の統合計算
   * @param kanteiCalculateRequest 鑑定計算実行リクエスト
   */
  async calculateKantei(
    kanteiCalculateRequest: KanteiCalculateRequest
  ): Promise<AxiosResponse<KanteiCalculationResponse>> {
    return axios.post<KanteiCalculationResponse>(
      `${this.basePath}/api/v1/kantei/calculate`,
      kanteiCalculateRequest
    );
  }

  /**
   * 81パターンテキストテンプレート取得
   * @param category カテゴリフィルタ（九星気学/姓名判断/吉方位）
   * @param activeOnly 有効なテンプレートのみ取得
   * @param limit 取得件数制限
   */
  async getKanteiTemplates(
    category?: string,
    activeOnly: boolean = true,
    limit: number = 100
  ): Promise<AxiosResponse<KanteiTemplatesResponse>> {
    const params: Record<string, any> = {
      active_only: activeOnly,
      limit
    };

    if (category) {
      params.category = category;
    }

    return axios.get<KanteiTemplatesResponse>(
      `${this.basePath}/api/v1/kantei/templates`,
      { params }
    );
  }

  /**
   * 鑑定システムヘルスチェック
   */
  async healthCheck(): Promise<AxiosResponse<MessageResponse>> {
    return axios.get<MessageResponse>(
      `${this.basePath}/api/v1/kantei/health`
    );
  }
}