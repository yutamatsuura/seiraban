// TypeScript type definitions generated from FastAPI OpenAPI schema

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  subscription_status: string;
  utage_user_id?: string | null;
}

export interface UserResponse {
  id: number;
  email: string;
  business_name?: string | null;
  operator_name?: string | null;
  subscription_status: string;
  utage_user_id?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientInfoRequest {
  name: string;
  birth_date: string;
  birth_time?: string | null;
  gender: GenderType;
  birth_place?: string | null;
  email: string;
}

export interface KanteiCalculateRequest {
  client_info: ClientInfoRequest;
  custom_message?: string | null;
}

export interface KyuseiKigakuResult {
  honmei: string;
  gekkyu: string;
  nichikyu: string;
  seikaku: string;
}

export interface SeimeiHandanResult {
  soukaku: number;
  tenkaku: number;
  jinkaku: number;
  chikaku: number;
  gaikaku: number;
  hyoka: string;
}

export interface KichikouiResult {
  honnen: string;
  gekkan: string;
  suishin: string;
}

export interface KanteiCalculationResponse {
  id: number;
  client_name: string;
  kyusei_kigaku: KyuseiKigakuResult;
  seimei_handan: SeimeiHandanResult;
  kichihoui: KichikouiResult;
  template_ids: number[];
  status: KanteiStatusType;
  created_at: string;
}

export interface KanteiTemplate {
  id: number;
  category: string;
  pattern_name: string;
  title: string;
  content: string;
  keywords: string[];
  usage_count?: number;
  is_active?: boolean;
}

export interface KanteiTemplatesResponse {
  total: number;
  templates: KanteiTemplate[];
  categories: string[];
}

export interface AuthErrorResponse {
  success: boolean;
  error_code: string;
  message: string;
  detail?: string | null;
}

export interface KanteiErrorResponse {
  error_code: string;
  error_message: string;
  details?: Record<string, any> | null;
}

export interface MessageResponse {
  success: boolean;
  message: string;
  data?: Record<string, any> | null;
}

export type GenderType = 'male' | 'female';
export type KanteiStatusType = 'created' | 'processing' | 'completed' | 'failed';

export interface HTTPValidationError {
  detail?: ValidationError[];
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}