import { Page, BrowserContext, expect } from '@playwright/test';

/**
 * 認証用の共通ヘルパー関数群
 *
 * このファイルには、E2Eテストで使用する認証関連の共通機能が含まれています。
 * - ログイン処理
 * - ログアウト処理
 * - 認証状態の確認
 * - セッション管理
 */

export interface TestUser {
  email: string;
  password: string;
  business_name?: string;
  operator_name?: string;
  is_superuser?: boolean;
}

// テスト用ユーザー設定（環境変数から取得）
export const TEST_USERS = {
  // 一般ユーザー
  user: {
    email: process.env.TEST_USER_EMAIL || 'test@example.com',
    password: process.env.TEST_USER_PASSWORD || 'testpass123',
    business_name: '運命織テスト事業所',
    operator_name: 'テスト鑑定士',
    is_superuser: false,
  },

  // 管理者ユーザー
  admin: {
    email: process.env.TEST_ADMIN_EMAIL || 'admin@example.com',
    password: process.env.TEST_ADMIN_PASSWORD || 'adminpass123',
    business_name: '運命織管理事業所',
    operator_name: '管理者',
    is_superuser: true,
  },
} as const;

/**
 * ログイン処理を実行する
 * @param page - Playwrightのページオブジェクト
 * @param user - ログインするユーザー情報
 * @param options - ログインオプション
 */
export async function login(
  page: Page,
  user: TestUser,
  options: {
    skipRedirect?: boolean;
    expectUrl?: string;
    timeout?: number;
  } = {}
): Promise<void> {
  const { skipRedirect = false, expectUrl = '/dashboard', timeout = 10000 } = options;

  // ログインページに移動
  await page.goto('/login');

  // ページが読み込まれるまで待機
  await page.waitForLoadState('networkidle');

  // ログインフォームの表示を確認
  await expect(page.locator('.login-form')).toBeVisible({ timeout });

  // メールアドレス入力
  const emailInput = page.locator('#email');
  await expect(emailInput).toBeVisible({ timeout });
  await emailInput.fill(user.email);

  // パスワード入力
  const passwordInput = page.locator('#password');
  await expect(passwordInput).toBeVisible({ timeout });
  await passwordInput.fill(user.password);

  // ログインボタンのクリック
  const loginButton = page.locator('.login-button');
  await expect(loginButton).toBeEnabled({ timeout });

  // ログイン実行（ネットワーク処理の完了を待機）
  await Promise.all([
    page.waitForResponse(response =>
      response.url().includes('/api/auth/login') &&
      response.status() === 200
    ),
    loginButton.click(),
  ]);

  // リダイレクトが無効でない場合、期待するURLへの遷移を確認
  if (!skipRedirect) {
    await page.waitForURL(expectUrl, { timeout });
  }

  // 認証状態の確認（ローカルストレージにトークンが保存されていることを確認）
  const token = await page.evaluate(() => localStorage.getItem('auth_token'));
  expect(token).toBeTruthy();

  console.log(`✅ ログイン成功: ${user.email}`);
}

/**
 * 管理者としてログインする
 * @param page - Playwrightのページオブジェクト
 * @param options - ログインオプション
 */
export async function loginAsAdmin(
  page: Page,
  options: {
    skipRedirect?: boolean;
    expectUrl?: string;
    timeout?: number;
  } = {}
): Promise<void> {
  await login(page, TEST_USERS.admin, {
    expectUrl: '/admin',
    ...options
  });
}

/**
 * 一般ユーザーとしてログインする
 * @param page - Playwrightのページオブジェクト
 * @param options - ログインオプション
 */
export async function loginAsUser(
  page: Page,
  options: {
    skipRedirect?: boolean;
    expectUrl?: string;
    timeout?: number;
  } = {}
): Promise<void> {
  await login(page, TEST_USERS.user, options);
}

/**
 * ログアウト処理を実行する
 * @param page - Playwrightのページオブジェクト
 * @param options - ログアウトオプション
 */
export async function logout(
  page: Page,
  options: {
    timeout?: number;
  } = {}
): Promise<void> {
  const { timeout = 10000 } = options;

  // サイドバーまたはヘッダーからログアウトボタンを探す
  const logoutButton = page.locator('[data-testid="logout-button"], .logout-button, button:has-text("ログアウト")').first();

  if (await logoutButton.isVisible({ timeout: 3000 })) {
    await Promise.all([
      page.waitForResponse(response =>
        response.url().includes('/api/auth/logout')
      ),
      logoutButton.click(),
    ]);
  } else {
    // ログアウトボタンが見つからない場合、直接ローカルストレージをクリア
    await page.evaluate(() => {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    });
  }

  // ログインページにリダイレクトされることを確認
  await page.waitForURL('/login', { timeout });

  // ローカルストレージからトークンが削除されていることを確認
  const token = await page.evaluate(() => localStorage.getItem('auth_token'));
  expect(token).toBeNull();

  console.log('✅ ログアウト成功');
}

/**
 * 認証状態を確認する
 * @param page - Playwrightのページオブジェクト
 * @returns 認証されている場合はtrue
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  const token = await page.evaluate(() => localStorage.getItem('auth_token'));
  return !!token;
}

/**
 * 管理者権限を確認する
 * @param page - Playwrightのページオブジェクト
 * @returns 管理者権限がある場合はtrue
 */
export async function isSuperuser(page: Page): Promise<boolean> {
  const userData = await page.evaluate(() => {
    const data = localStorage.getItem('user_data');
    return data ? JSON.parse(data) : null;
  });

  return userData?.is_superuser || false;
}

/**
 * 認証状態をセットアップする（ブラウザコンテキスト用）
 * @param context - ブラウザコンテキスト
 * @param user - ユーザー情報
 */
export async function setupAuthState(
  context: BrowserContext,
  user: TestUser
): Promise<void> {
  // 認証状態をローカルストレージに直接設定
  await context.addInitScript(({ email, business_name, operator_name, is_superuser }) => {
    // モックトークンを設定
    const mockToken = 'mock-jwt-token-for-testing';
    localStorage.setItem('auth_token', mockToken);

    // モックユーザーデータを設定
    const mockUser = {
      id: 1,
      email,
      business_name,
      operator_name,
      is_active: true,
      is_superuser: is_superuser || false,
      withdrawal_status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    localStorage.setItem('user_data', JSON.stringify(mockUser));
  }, user);

  console.log(`✅ 認証状態をセットアップ: ${user.email}`);
}

/**
 * 認証が必要なページアクセス時の共通処理
 * @param page - Playwrightのページオブジェクト
 * @param url - アクセスするURL
 * @param user - ログインするユーザー（未認証の場合）
 */
export async function navigateToProtectedPage(
  page: Page,
  url: string,
  user: TestUser = TEST_USERS.user
): Promise<void> {
  // ページに移動
  await page.goto(url);

  // 認証が必要な場合、ログインページにリダイレクトされる
  if (page.url().includes('/login')) {
    console.log('🔒 未認証のため、ログイン処理を実行');
    await login(page, user, { expectUrl: url });
  }

  // 最終的に期待するページに到達していることを確認
  await page.waitForURL(url);
}

/**
 * テスト用のユーザーを作成する（API経由）
 * @param page - Playwrightのページオブジェクト
 * @param user - 作成するユーザー情報
 */
export async function createTestUser(
  page: Page,
  user: TestUser
): Promise<void> {
  // ユーザー登録APIを直接呼び出し
  const response = await page.request.post('/api/auth/register', {
    data: {
      email: user.email,
      password: user.password,
      business_name: user.business_name,
      operator_name: user.operator_name,
    },
  });

  if (!response.ok()) {
    const error = await response.json();
    throw new Error(`ユーザー作成に失敗: ${error.detail || response.statusText()}`);
  }

  console.log(`✅ テストユーザー作成成功: ${user.email}`);
}

/**
 * テスト用のユーザーを削除する（API経由）
 * @param page - Playwrightのページオブジェクト
 * @param email - 削除するユーザーのメールアドレス
 */
export async function deleteTestUser(
  page: Page,
  email: string
): Promise<void> {
  // 管理者としてログイン
  await loginAsAdmin(page);

  // ユーザー削除APIを呼び出し（管理者権限が必要）
  const response = await page.request.delete(`/api/admin/users/by-email/${email}`);

  if (!response.ok() && response.status() !== 404) {
    const error = await response.json();
    throw new Error(`ユーザー削除に失敗: ${error.detail || response.statusText()}`);
  }

  console.log(`✅ テストユーザー削除成功: ${email}`);
}

/**
 * テスト環境の認証状態をリセットする
 * @param page - Playwrightのページオブジェクト
 */
export async function resetAuthState(page: Page): Promise<void> {
  // ローカルストレージをクリア
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  // Cookieをクリア
  await page.context().clearCookies();

  console.log('✅ 認証状態をリセット');
}