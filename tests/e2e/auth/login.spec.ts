import { test, expect } from '@playwright/test';
import { login, logout, loginAsUser, loginAsAdmin, isAuthenticated, TEST_USERS } from '../../helpers/auth';

/**
 * 認証機能のE2Eテスト
 *
 * このテストスイートでは、以下の認証機能をテストします：
 * - ログイン機能
 * - ログアウト機能
 * - 認証状態の確認
 * - 管理者権限の確認
 */

test.describe('認証機能', () => {

  test.beforeEach(async ({ page }) => {
    // 各テスト前に認証状態をクリア
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('一般ユーザーとしてログインできる', async ({ page }) => {
    // ログイン実行
    await loginAsUser(page);

    // ダッシュボードに遷移していることを確認
    await expect(page).toHaveURL('/dashboard');

    // 認証状態を確認
    const authStatus = await isAuthenticated(page);
    expect(authStatus).toBe(true);

    // ユーザー情報の表示確認（サイドバーやヘッダーにユーザー名が表示される想定）
    await expect(page.locator('[data-testid="user-email"], .user-email')).toContainText(TEST_USERS.user.email);
  });

  test('管理者としてログインできる', async ({ page }) => {
    // 管理者ログイン実行
    await loginAsAdmin(page);

    // 管理者ページに遷移していることを確認
    await expect(page).toHaveURL('/admin');

    // 認証状態を確認
    const authStatus = await isAuthenticated(page);
    expect(authStatus).toBe(true);

    // 管理者権限の確認
    const userData = await page.evaluate(() => {
      const data = localStorage.getItem('user_data');
      return data ? JSON.parse(data) : null;
    });
    expect(userData?.is_superuser).toBe(true);
  });

  test('間違ったパスワードでログインが失敗する', async ({ page }) => {
    // ログインページに移動
    await page.goto('/login');

    // 間違った認証情報を入力
    await page.fill('#email', TEST_USERS.user.email);
    await page.fill('#password', 'wrong-password');

    // ログインボタンをクリック
    await page.click('.login-button');

    // エラーメッセージの表示を確認
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText(/ログインに失敗|認証に失敗|パスワードが間違って/i);

    // ログインページに留まっていることを確認
    await expect(page).toHaveURL('/login');

    // 認証状態を確認（未認証のまま）
    const authStatus = await isAuthenticated(page);
    expect(authStatus).toBe(false);
  });

  test('存在しないユーザーでログインが失敗する', async ({ page }) => {
    // ログインページに移動
    await page.goto('/login');

    // 存在しないユーザーの認証情報を入力
    await page.fill('#email', 'nonexistent@example.com');
    await page.fill('#password', 'password123');

    // ログインボタンをクリック
    await page.click('.login-button');

    // エラーメッセージの表示を確認
    await expect(page.locator('.error-message')).toBeVisible();

    // ログインページに留まっていることを確認
    await expect(page).toHaveURL('/login');
  });

  test('ログアウトできる', async ({ page }) => {
    // まずログイン
    await loginAsUser(page);
    await expect(page).toHaveURL('/dashboard');

    // ログアウト実行
    await logout(page);

    // ログインページにリダイレクトされることを確認
    await expect(page).toHaveURL('/login');

    // 認証状態を確認（未認証になっている）
    const authStatus = await isAuthenticated(page);
    expect(authStatus).toBe(false);
  });

  test('未認証でのダッシュボードアクセスはログインページにリダイレクトされる', async ({ page }) => {
    // 未認証状態でダッシュボードにアクセス
    await page.goto('/dashboard');

    // ログインページにリダイレクトされることを確認
    await expect(page).toHaveURL(/\/login/);

    // ログイン後のリダイレクト先がクエリパラメータに含まれていることを確認
    const url = page.url();
    expect(url).toContain('redirect');
  });

  test('未認証での管理者ページアクセスはログインページにリダイレクトされる', async ({ page }) => {
    // 未認証状態で管理者ページにアクセス
    await page.goto('/admin');

    // ログインページにリダイレクトされることを確認
    await expect(page).toHaveURL(/\/login/);
  });

  test('一般ユーザーでの管理者ページアクセスは権限エラーになる', async ({ page }) => {
    // 一般ユーザーとしてログイン
    await loginAsUser(page);

    // 管理者ページにアクセスを試行
    await page.goto('/admin');

    // 権限エラーまたはアクセス拒否が表示されることを確認
    // （実装によりログインページにリダイレクト、403エラー、またはエラーメッセージ表示）
    const url = page.url();
    const hasErrorMessage = await page.locator('.error-message, .access-denied').isVisible().catch(() => false);

    // いずれかの条件が満たされることを確認
    const isBlocked = url.includes('/login') ||
                     url.includes('/dashboard') ||
                     url.includes('/403') ||
                     hasErrorMessage;

    expect(isBlocked).toBe(true);
  });

  test('ログイン状態を維持したままページをリロードできる', async ({ page }) => {
    // ログイン
    await loginAsUser(page);
    await expect(page).toHaveURL('/dashboard');

    // ページをリロード
    await page.reload();

    // 認証状態が維持されていることを確認
    await expect(page).toHaveURL('/dashboard');

    const authStatus = await isAuthenticated(page);
    expect(authStatus).toBe(true);
  });

  test('ログインフォームのバリデーションが機能する', async ({ page }) => {
    await page.goto('/login');

    // 空のフォームでログインボタンを押す
    const loginButton = page.locator('.login-button');

    // メールアドレス未入力の場合、ボタンが無効化されているかHTML5バリデーションでエラーになる
    await expect(loginButton).toBeDisabled();

    // 無効なメールアドレス形式を入力
    await page.fill('#email', 'invalid-email');
    await page.fill('#password', 'password123');

    // HTML5バリデーションまたはカスタムバリデーションエラーを確認
    await loginButton.click();

    // フォームバリデーションエラーまたはエラーメッセージの表示を確認
    const validationError = page.locator('.error-message, :invalid');
    const hasValidationError = await validationError.count() > 0;
    expect(hasValidationError).toBe(true);
  });
});