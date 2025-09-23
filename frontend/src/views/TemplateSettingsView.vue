<template>
  <MainLayout>
    <div class="template-settings-view">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">
        <img src="/src/assets/icons/template.svg" alt="テンプレート設定" class="page-title-icon" />
        テンプレート設定
      </h1>
      <p class="page-subtitle">鑑定書のレイアウトとデザインをカスタマイズできます</p>
    </div>

    <!-- Main Content -->
    <div class="main-content" :class="{ 'settings-collapsed': isSettingsCollapsed }">
      <!-- Settings Panel (Mobile First) -->
      <div class="settings-panel mobile-panel" :class="{ collapsed: isSettingsCollapsed }">
        <div class="panel-header">
          <h2 v-if="!isSettingsCollapsed">カスタマイズ設定</h2>
          <div v-if="isSettingsCollapsed" class="collapsed-indicator">
            <span class="material-icons">tune</span>
            <span class="collapsed-text">設定</span>
          </div>
          <button @click="toggleSettings" class="collapse-btn" :title="isSettingsCollapsed ? '設定パネルを展開' : '設定パネルを閉じる'">
            <span class="material-icons">{{ isSettingsCollapsed ? 'expand_more' : 'expand_less' }}</span>
          </button>
        </div>

        <div v-if="!isSettingsCollapsed" class="panel-content">
          <!-- Tab Navigation -->
          <div class="tab-navigation">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              class="tab-button"
              :class="{ active: activeTab === tab.id }"
            >
              <span class="material-icons">{{ tab.icon }}</span>
              {{ tab.label }}
            </button>
          </div>

          <!-- Settings Form -->
          <form @submit.prevent="saveSettings" class="settings-form">
            <!-- Basic Information Tab -->
            <div v-if="activeTab === 'basic'" class="tab-content">
              <div class="compact-form-section">
                <div class="form-row">
                  <div class="form-group">
                    <label for="businessName">事業者名</label>
                    <input
                      id="businessName"
                      v-model="templateSettings.businessName"
                      type="text"
                      placeholder="事業者名を入力"
                      class="form-input"
                    />
                  </div>
                  <div class="form-group">
                    <label for="operatorName">鑑定者名</label>
                    <input
                      id="operatorName"
                      v-model="templateSettings.operatorName"
                      type="text"
                      placeholder="鑑定者名を入力"
                      class="form-input"
                    />
                  </div>
                </div>
                <div class="form-group">
                  <label for="diagnosisTitle">鑑定書タイトル</label>
                  <input
                    id="diagnosisTitle"
                    v-model="templateSettings.diagnosisTitle"
                    type="text"
                    placeholder="鑑定書タイトルを入力"
                    class="form-input"
                  />
                </div>
              </div>
            </div>

            <!-- Logo Settings Tab -->
            <div v-if="activeTab === 'logo'" class="tab-content">
              <div class="compact-logo-settings">
                <!-- Current Logo Preview -->
                <div v-if="templateSettings.logoUrl" class="compact-logo-card">
                  <div class="logo-preview-compact">
                    <img :src="logoImageUrl" alt="現在のロゴ" class="logo-image" />
                    <div class="logo-actions">
                      <button @click="triggerLogoUpload" type="button" class="compact-btn change-btn">
                        <span class="material-icons">edit</span>
                        変更
                      </button>
                      <button @click="removeLogo" type="button" class="compact-btn remove-btn">
                        <span class="material-icons">delete</span>
                        削除
                      </button>
                    </div>
                  </div>
                  <p class="logo-status">
                    <span class="material-icons">check_circle</span>
                    ロゴが設定されています
                  </p>
                </div>

                <!-- Upload Zone -->
                <div v-else class="compact-upload-zone" @click="triggerLogoUpload" @dragover.prevent @drop.prevent="handleLogoDrop">
                  <span class="material-icons upload-icon">cloud_upload</span>
                  <h4>ロゴをアップロード</h4>
                  <p>JPEG・PNG・GIF・WebP（最大5MB）</p>
                </div>

                <input
                  id="logoFile"
                  ref="logoFileInput"
                  type="file"
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  @change="handleLogoUpload"
                  class="logo-file-input"
                />
              </div>
            </div>

            <!-- Color Settings Tab -->
            <div v-if="activeTab === 'color'" class="tab-content">
              <div class="compact-color-grid">
                <div
                  v-for="preset in colorPresets"
                  :key="preset.name"
                  @click="selectColorPreset(preset)"
                  class="compact-color-preset"
                  :class="{ active: templateSettings.colorTheme === preset.name }"
                >
                  <div class="color-preview">
                    <div class="primary-color" :style="{ backgroundColor: preset.primary }"></div>
                    <div class="accent-color" :style="{ backgroundColor: preset.accent }"></div>
                  </div>
                  <span class="preset-name">{{ preset.label }}</span>
                </div>
              </div>
            </div>

            <!-- Font Settings Tab -->
            <div v-if="activeTab === 'font'" class="tab-content">
              <div class="compact-font-controls">
                <!-- Font Family -->
                <div class="compact-font-section">
                  <h4>フォントファミリー</h4>
                  <div class="compact-font-grid">
                    <div
                      v-for="font in fontFamilyOptions"
                      :key="font.value"
                      @click="templateSettings.fontFamily = font.value"
                      class="compact-font-card"
                      :class="{ active: templateSettings.fontFamily === font.value }"
                    >
                      <div class="font-preview" :style="{ fontFamily: font.fontFamily }">あが</div>
                      <div class="font-name">{{ font.label }}</div>
                    </div>
                  </div>
                </div>

                <!-- Font Size -->
                <div class="compact-font-section">
                  <h4>フォントサイズ</h4>
                  <div class="compact-size-options">
                    <div
                      v-for="size in fontSizeOptions"
                      :key="size.value"
                      @click="templateSettings.fontSize = size.value"
                      class="compact-size-option"
                      :class="{ active: templateSettings.fontSize === size.value }"
                    >
                      <div class="size-preview" :style="{ fontSize: size.preview }">あ</div>
                      <div class="size-label">{{ size.label }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Typography Settings Tab -->
            <div v-if="activeTab === 'typography'" class="tab-content">
              <div class="compact-typography-controls">
                <!-- Title Font -->
                <div class="compact-typography-section">
                  <h4>タイトルフォント</h4>
                  <div class="compact-typography-grid">
                    <div
                      v-for="font in titleFontOptions"
                      :key="font.value"
                      @click="templateSettings.titleFont = font.value"
                      class="compact-typography-card"
                      :class="{ active: templateSettings.titleFont === font.value }"
                    >
                      <div class="typography-preview" :style="{ fontFamily: font.fontFamily, fontWeight: font.fontWeight }">
                        タイトル
                      </div>
                      <div class="typography-name">{{ font.label }}</div>
                    </div>
                  </div>
                </div>

                <!-- Body Font -->
                <div class="compact-typography-section">
                  <h4>本文フォント</h4>
                  <div class="compact-typography-grid">
                    <div
                      v-for="font in bodyFontOptions"
                      :key="font.value"
                      @click="templateSettings.bodyFont = font.value"
                      class="compact-typography-card"
                      :class="{ active: templateSettings.bodyFont === font.value }"
                    >
                      <div class="typography-preview">
                        本文サンプル
                      </div>
                      <div class="typography-name">{{ font.label }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="compact-form-actions">
              <button
                type="button"
                @click="resetToDefaults"
                class="btn btn-secondary"
                :disabled="isSaving"
              >
                リセット
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="isSaving"
              >
                {{ isSaving ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Preview Area -->
      <div class="preview-area">
        <div class="preview-header enhanced-preview-header">
          <div class="preview-title">
            <span class="material-icons">preview</span>
            <h2>リアルタイムプレビュー</h2>
          </div>
          <div class="preview-controls">
            <div class="preview-zoom">
              <button @click="previewZoom = Math.max(0.5, previewZoom - 0.1)" class="zoom-btn">
                <span class="material-icons">zoom_out</span>
              </button>
              <span class="zoom-level">{{ Math.round(previewZoom * 100) }}%</span>
              <button @click="previewZoom = Math.min(1.5, previewZoom + 0.1)" class="zoom-btn">
                <span class="material-icons">zoom_in</span>
              </button>
            </div>
            <button @click="refreshPreview" class="refresh-btn" :disabled="isPreviewLoading">
              <span class="material-icons">refresh</span>
              {{ isPreviewLoading ? '更新中...' : '更新' }}
            </button>
          </div>
        </div>

        <!-- Template Preview -->
        <div class="template-preview" :style="{ transform: `scale(${previewZoom})`, transformOrigin: 'top left' }">
          <!-- Loading State -->
          <div v-if="isPreviewLoading" class="preview-loading">
            <div class="loading-spinner"></div>
            <p>プレビューを更新中...</p>
          </div>

          <!-- プレビューコンテンツ全体にpattern-cleanクラスを適用 -->
          <div v-else class="diagnosis-content pattern-clean" :style="templateStyles">
          <!-- Header Section - 実際のPreviewView.vueと同じ構造 -->
          <div class="template-header modern-minimal">
            <div class="header-background"></div>
            <div class="header-content">
              <!-- Logo Section -->
              <div class="logo-section">
                <div v-if="templateSettings.logoUrl" class="logo-container">
                  <img :src="logoImageUrl" alt="ロゴ" class="logo-image" />
                </div>
                <div v-else class="logo-placeholder">
                  <div class="logo-placeholder-content">
                    ロゴ未設定
                  </div>
                </div>
              </div>

              <!-- Main Title Section -->
              <div class="title-section">
                <div class="title-ornament"></div>
                <h1 class="diagnosis-title" :style="{ fontFamily: 'var(--title-font)', fontSize: `calc(1.8rem * var(--font-size-multiplier))` }">
                  {{ templateSettings.diagnosisTitle || '九星気学・姓名判断 総合鑑定書' }}
                </h1>
                <div class="title-ornament"></div>
              </div>

              <!-- Business Info Section -->
              <div class="business-section">
                <div v-if="templateSettings.businessName" class="business-card">
                  <div class="business-info">
                    <h2 class="business-name" :style="{ fontFamily: 'var(--title-font)', fontSize: `calc(1.2rem * var(--font-size-multiplier))` }">{{ templateSettings.businessName }}</h2>
                    <p v-if="templateSettings.operatorName" class="operator-name" :style="{ fontFamily: 'var(--body-font)', fontSize: `calc(1rem * var(--font-size-multiplier))` }">
                      <span class="operator-label">鑑定士</span>
                      <span class="operator-value">{{ templateSettings.operatorName }}</span>
                    </p>
                  </div>
                </div>
                <div v-else class="business-card debug-placeholder">
                  <div class="business-info">
                    <h2 class="business-name" :style="{ fontFamily: 'var(--title-font)', fontSize: `calc(1.2rem * var(--font-size-multiplier))` }">事業者名未設定</h2>
                    <p class="operator-name" :style="{ fontFamily: 'var(--body-font)', fontSize: `calc(1rem * var(--font-size-multiplier))` }">
                      <span class="operator-label">鑑定士</span>
                      <span class="operator-value">鑑定者名未設定</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Date Section -->
            <div class="date-section">
              <div class="date-container">
                <span class="date-label">鑑定実施日</span>
                <span class="date-value">{{ formatDate(new Date()) }}</span>
              </div>
            </div>
          </div>

          <!-- Client Information -->
          <div class="card client-info">
            <div class="card-header">
              <h2>依頼者情報</h2>
            </div>
            <div class="card-body">
              <div class="info-grid">
                <div class="info-item">
                  <label>お名前</label>
                  <span :style="{ fontFamily: 'var(--body-font)', fontSize: `calc(1rem * var(--font-size-multiplier))` }">山田 花子</span>
                </div>
                <div class="info-item">
                  <label>生年月日</label>
                  <span :style="{ fontFamily: 'var(--body-font)', fontSize: `calc(1rem * var(--font-size-multiplier))` }">1985年4月15日 (39歳)</span>
                </div>
                <div class="info-item">
                  <label>十二支</label>
                  <span :style="{ fontFamily: 'var(--body-font)', fontSize: `calc(1rem * var(--font-size-multiplier))` }">丑年</span>
                </div>
                <div class="info-item">
                  <label>性別</label>
                  <span :style="{ fontFamily: 'var(--body-font)', fontSize: `calc(1rem * var(--font-size-multiplier))` }">女性</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Kyusei Results -->
          <div class="card kyusei-results">
            <div class="card-header">
              <h2>九星気学・吉方位の鑑定結果</h2>
            </div>
            <div class="card-body">
              <!-- Basic Nine Star Information -->
              <div class="section">
                <h3>基本九星情報</h3>
                <div class="nine-star-grid">
                  <div class="star-item">
                    <label>本命星</label>
                    <span class="star-value" :style="{ fontFamily: 'var(--body-font)', fontSize: `calc(1rem * var(--font-size-multiplier))` }">八白土星</span>
                  </div>
                  <div class="star-item">
                    <label>月命星</label>
                    <span class="star-value" :style="{ fontFamily: 'var(--body-font)', fontSize: `calc(1rem * var(--font-size-multiplier))` }">三碧木星</span>
                  </div>
                </div>
              </div>

              <!-- Zodiac Information -->
              <div class="section">
                <h3>干支情報</h3>
                <div class="zodiac-grid">
                  <div class="zodiac-item">
                    <label>年干支</label>
                    <span>乙丑</span>
                  </div>
                  <div class="zodiac-item">
                    <label>月干支</label>
                    <span>庚辰</span>
                  </div>
                  <div class="zodiac-item">
                    <label>日干支</label>
                    <span>甲申</span>
                  </div>
                </div>
              </div>

              <!-- Direction Information -->
              <div class="section">
                <h3>吉方位情報</h3>
                <div class="direction-grid">
                  <div class="direction-item">
                    <label>最大吉方</label>
                    <span>北東</span>
                  </div>
                  <div class="direction-item">
                    <label>吉方</label>
                    <span>南西</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Seimei Results -->
          <div class="card seimei-results">
            <div class="card-header">
              <h2>姓名判断の鑑定結果</h2>
            </div>
            <div class="card-body">
              <!-- Character Table -->
              <div class="section">
                <h3>文字の構成</h3>
                <div class="character-table">
                  <table>
                    <thead>
                      <tr>
                        <th>文字</th>
                        <th>姓1</th>
                        <th>姓2</th>
                        <th>名1</th>
                        <th>名2</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>漢字</td>
                        <td>山</td>
                        <td>田</td>
                        <td>花</td>
                        <td>子</td>
                      </tr>
                      <tr>
                        <td>画数</td>
                        <td>3</td>
                        <td>5</td>
                        <td>7</td>
                        <td>3</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Stroke Results -->
              <div class="section">
                <h3>画数の鑑定結果</h3>
                <div class="stroke-grid">
                  <div class="stroke-item">
                    <label>天格</label>
                    <span>8画</span>
                  </div>
                  <div class="stroke-item">
                    <label>人格</label>
                    <span>12画</span>
                  </div>
                  <div class="stroke-item">
                    <label>地格</label>
                    <span>10画</span>
                  </div>
                  <div class="stroke-item">
                    <label>総格</label>
                    <span>18画</span>
                  </div>
                </div>
              </div>

              <!-- Result Content -->
              <div class="section">
                <div class="result-content">
                  <div class="score-section">
                    <span class="score-value">75</span>
                    <span class="score-label">点</span>
                  </div>
                  <div class="message-section">
                    <p :style="{ fontFamily: 'var(--body-font)', fontSize: `calc(1rem * var(--font-size-multiplier))` }">総合的に良いバランスの名前です。人格運が特に良く、対人関係に恵まれる傾向があります。</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer Section -->
          <div class="template-footer modern-minimal">
            <div class="footer-content">
              <div class="footer-info">
                <div class="footer-business">{{ templateSettings.businessName || '事業者名未設定' }}</div>
                <div class="footer-operator">鑑定士: {{ templateSettings.operatorName || '鑑定者名未設定' }}</div>
              </div>
              <div class="footer-disclaimer">
                本鑑定書は参考情報としてご活用ください。結果について一切の責任を負いません。
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>

      <!-- Settings Panel (Desktop) -->
      <div class="settings-panel desktop-panel" :class="{ collapsed: isSettingsCollapsed }">
        <div class="panel-header">
          <h2 v-if="!isSettingsCollapsed">カスタマイズ設定</h2>
          <div v-if="isSettingsCollapsed" class="collapsed-indicator" @click="toggleSettings">
            <div class="floating-indicator">
              <span class="material-icons">tune</span>
              <span class="collapsed-text">設定</span>
              <div class="pulse-ring"></div>
            </div>
            <div class="hover-tooltip">クリックで設定を開く</div>
          </div>
          <button @click="toggleSettings" class="collapse-btn" :title="isSettingsCollapsed ? '設定パネルを展開' : '設定パネルを閉じる'">
            <span class="material-icons">{{ isSettingsCollapsed ? 'chevron_left' : 'chevron_right' }}</span>
          </button>
        </div>

        <div v-if="!isSettingsCollapsed" class="panel-content">
          <!-- Tab Navigation -->
          <div class="tab-navigation">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              class="tab-button"
              :class="{ active: activeTab === tab.id }"
            >
              <span class="material-icons">{{ tab.icon }}</span>
              {{ tab.label }}
            </button>
          </div>

          <!-- Settings Form -->
          <form @submit.prevent="saveSettings" class="settings-form">
            <!-- Basic Information Tab -->
            <div v-if="activeTab === 'basic'" class="tab-content">
              <div class="compact-form-section">
                <div class="form-row">
                  <div class="form-group">
                    <label for="businessName2">事業者名</label>
                    <input
                      id="businessName2"
                      v-model="templateSettings.businessName"
                      type="text"
                      placeholder="事業者名を入力"
                      class="form-input"
                    />
                  </div>
                  <div class="form-group">
                    <label for="operatorName2">鑑定者名</label>
                    <input
                      id="operatorName2"
                      v-model="templateSettings.operatorName"
                      type="text"
                      placeholder="鑑定者名を入力"
                      class="form-input"
                    />
                  </div>
                </div>
                <div class="form-group">
                  <label for="diagnosisTitle2">鑑定書タイトル</label>
                  <input
                    id="diagnosisTitle2"
                    v-model="templateSettings.diagnosisTitle"
                    type="text"
                    placeholder="鑑定書タイトルを入力"
                    class="form-input"
                  />
                </div>
              </div>
            </div>

            <!-- Logo Settings Tab -->
            <div v-if="activeTab === 'logo'" class="tab-content">
              <div class="compact-logo-settings">
                <!-- Current Logo Preview -->
                <div v-if="templateSettings.logoUrl" class="compact-logo-card">
                  <div class="logo-preview-compact">
                    <img :src="logoImageUrl" alt="現在のロゴ" class="logo-image" />
                    <div class="logo-actions">
                      <button @click="triggerLogoUpload" type="button" class="compact-btn change-btn">
                        <span class="material-icons">edit</span>
                        変更
                      </button>
                      <button @click="removeLogo" type="button" class="compact-btn remove-btn">
                        <span class="material-icons">delete</span>
                        削除
                      </button>
                    </div>
                  </div>
                  <p class="logo-status">
                    <span class="material-icons">check_circle</span>
                    ロゴが設定されています
                  </p>
                </div>

                <!-- Upload Zone -->
                <div v-else class="compact-upload-zone" @click="triggerLogoUpload" @dragover.prevent @drop.prevent="handleLogoDrop">
                  <span class="material-icons upload-icon">cloud_upload</span>
                  <h4>ロゴをアップロード</h4>
                  <p>JPEG・PNG・GIF・WebP（最大5MB）</p>
                </div>

                <input
                  id="logoFile2"
                  ref="logoFileInput"
                  type="file"
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  @change="handleLogoUpload"
                  class="logo-file-input"
                />
              </div>
            </div>

            <!-- Color Settings Tab -->
            <div v-if="activeTab === 'color'" class="tab-content">
              <div class="compact-color-grid">
                <div
                  v-for="preset in colorPresets"
                  :key="preset.name"
                  @click="selectColorPreset(preset)"
                  class="compact-color-preset"
                  :class="{ active: templateSettings.colorTheme === preset.name }"
                >
                  <div class="color-preview">
                    <div class="primary-color" :style="{ backgroundColor: preset.primary }"></div>
                    <div class="accent-color" :style="{ backgroundColor: preset.accent }"></div>
                  </div>
                  <span class="preset-name">{{ preset.label }}</span>
                </div>
              </div>
            </div>

            <!-- Font Settings Tab -->
            <div v-if="activeTab === 'font'" class="tab-content">
              <div class="compact-font-controls">
                <!-- Font Family -->
                <div class="compact-font-section">
                  <h4>フォントファミリー</h4>
                  <div class="compact-font-grid">
                    <div
                      v-for="font in fontFamilyOptions"
                      :key="font.value"
                      @click="templateSettings.fontFamily = font.value"
                      class="compact-font-card"
                      :class="{ active: templateSettings.fontFamily === font.value }"
                    >
                      <div class="font-preview" :style="{ fontFamily: font.fontFamily }">あが</div>
                      <div class="font-name">{{ font.label }}</div>
                    </div>
                  </div>
                </div>

                <!-- Font Size -->
                <div class="compact-font-section">
                  <h4>フォントサイズ</h4>
                  <div class="compact-size-options">
                    <div
                      v-for="size in fontSizeOptions"
                      :key="size.value"
                      @click="templateSettings.fontSize = size.value"
                      class="compact-size-option"
                      :class="{ active: templateSettings.fontSize === size.value }"
                    >
                      <div class="size-preview" :style="{ fontSize: size.preview }">あ</div>
                      <div class="size-label">{{ size.label }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Typography Settings Tab -->
            <div v-if="activeTab === 'typography'" class="tab-content">
              <div class="compact-typography-controls">
                <!-- Title Font -->
                <div class="compact-typography-section">
                  <h4>タイトルフォント</h4>
                  <div class="compact-typography-grid">
                    <div
                      v-for="font in titleFontOptions"
                      :key="font.value"
                      @click="templateSettings.titleFont = font.value"
                      class="compact-typography-card"
                      :class="{ active: templateSettings.titleFont === font.value }"
                    >
                      <div class="typography-preview" :style="{ fontFamily: font.fontFamily, fontWeight: font.fontWeight }">
                        タイトル
                      </div>
                      <div class="typography-name">{{ font.label }}</div>
                    </div>
                  </div>
                </div>

                <!-- Body Font -->
                <div class="compact-typography-section">
                  <h4>本文フォント</h4>
                  <div class="compact-typography-grid">
                    <div
                      v-for="font in bodyFontOptions"
                      :key="font.value"
                      @click="templateSettings.bodyFont = font.value"
                      class="compact-typography-card"
                      :class="{ active: templateSettings.bodyFont === font.value }"
                    >
                      <div class="typography-preview">
                        本文サンプル
                      </div>
                      <div class="typography-name">{{ font.label }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="compact-form-actions">
              <button
                type="button"
                @click="resetToDefaults"
                class="btn btn-secondary"
                :disabled="isSaving"
              >
                リセット
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="isSaving"
              >
                {{ isSaving ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { apiClient } from '@/services/api-client'
import MainLayout from '@/components/layout/MainLayout.vue'

// Types
interface TemplateSettings {
  businessName: string
  operatorName: string
  diagnosisTitle: string
  logoUrl: string
  primaryColor: string
  accentColor: string
  colorTheme: string
  fontFamily: string
  fontSize: string
  titleFont: string
  bodyFont: string
}

// Stores
const userStore = useUserStore()

// Reactive Data
const isSaving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const isSettingsCollapsed = ref(true)
const isPreviewLoading = ref(true)
const previewZoom = ref(1)
const activeTab = ref('basic')

// Tab definitions
const tabs = [
  { id: 'basic', label: '基本', icon: 'info' },
  { id: 'logo', label: 'ロゴ', icon: 'image' },
  { id: 'color', label: 'カラー', icon: 'palette' },
  { id: 'font', label: 'フォント', icon: 'text_fields' },
  { id: 'typography', label: 'スタイル', icon: 'title' }
]

const templateSettings = reactive<TemplateSettings>({
  businessName: '',
  operatorName: '',
  diagnosisTitle: '鑑定書',
  logoUrl: '',
  primaryColor: '#2c3e50',
  accentColor: '#34495e',
  colorTheme: 'navy',
  fontFamily: 'default',
  fontSize: 'medium',
  titleFont: 'default',
  bodyFont: 'default'
})

// フォント設定用のオプション定義
const fontFamilyOptions = [
  { value: 'default', label: 'デフォルト', description: '標準フォント', fontFamily: 'system-ui, sans-serif' },
  { value: 'gothic', label: 'ゴシック体', description: 'すっきりとした印象', fontFamily: 'Noto Sans JP, sans-serif' },
  { value: 'mincho', label: '明朝体', description: '上品で落ち着いた印象', fontFamily: 'Noto Serif JP, serif' },
  { value: 'rounded', label: '丸ゴシック', description: '親しみやすい印象', fontFamily: 'M PLUS Rounded 1c, sans-serif' }
]

const fontSizeOptions = [
  { value: 'small', label: '小', description: 'コンパクト', preview: '0.9rem' },
  { value: 'medium', label: '中', description: '標準', preview: '1rem' },
  { value: 'large', label: '大', description: '読みやすい', preview: '1.1rem' }
]

const titleFontOptions = [
  { value: 'default', label: 'デフォルト', description: '標準タイトル', fontFamily: 'system-ui, sans-serif', fontWeight: 'normal' },
  { value: 'bold-gothic', label: '太ゴシック', description: 'インパクトのあるタイトル', fontFamily: 'Noto Sans JP, sans-serif', fontWeight: 'bold' },
  { value: 'mincho', label: '明朝体', description: '伝統的なタイトル', fontFamily: 'Noto Serif JP, serif', fontWeight: 'normal' },
  { value: 'decorative', label: '装飾フォント', description: '特別感のあるタイトル', fontFamily: 'Zen Antique Soft, serif', fontWeight: 'normal' }
]

const bodyFontOptions = [
  { value: 'default', label: 'デフォルト', description: '標準本文', fontFamily: 'system-ui, sans-serif' },
  { value: 'gothic', label: 'ゴシック体', description: '読みやすい本文', fontFamily: 'Noto Sans JP, sans-serif' },
  { value: 'mincho', label: '明朝体', description: '上品な本文', fontFamily: 'Noto Serif JP, serif' },
  { value: 'rounded', label: '丸ゴシック', description: 'やわらかい本文', fontFamily: 'M PLUS Rounded 1c, sans-serif' }
]

// Color Presets - 落ち着いた色合い
const colorPresets = [
  { name: 'navy', label: 'ネイビー', primary: '#2c3e50', accent: '#34495e' },
  { name: 'sage', label: 'セージ', primary: '#95a5a6', accent: '#7f8c8d' },
  { name: 'charcoal', label: 'チャコール', primary: '#36454f', accent: '#708090' },
  { name: 'olive', label: 'オリーブ', primary: '#6c7b4f', accent: '#556b2f' },
  { name: 'burgundy', label: 'バーガンディ', primary: '#800020', accent: '#a0002a' },
  { name: 'slate', label: 'スレート', primary: '#465b6b', accent: '#5a6c7d' },
  { name: 'bronze', label: 'ブロンズ', primary: '#8b6914', accent: '#b8860b' },
  { name: 'plum', label: 'プラム', primary: '#663366', accent: '#8b4789' }
]

// Default Settings
const defaultSettings: TemplateSettings = {
  businessName: '',
  operatorName: '',
  diagnosisTitle: '鑑定書',
  logoUrl: '',
  primaryColor: '#2c3e50',
  accentColor: '#34495e',
  colorTheme: 'navy',
  fontFamily: 'default',
  fontSize: 'medium',
  titleFont: 'default',
  bodyFont: 'default'
}

// テンプレートスタイルの計算（プレビュー用）
const templateStyles = computed(() => {
  const selectedPreset = colorPresets.find(p => p.name === templateSettings.colorTheme)

  // フォントファミリーのマッピング
  const fontFamilyMap: Record<string, string> = {
    'default': '"Hiragino Kaku Gothic ProN", "Hiragino Sans", "Yu Gothic Medium", "Meiryo", sans-serif',
    'gothic': '"Yu Gothic Medium", "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Meiryo", sans-serif',
    'mincho': '"Yu Mincho", "Hiragino Mincho ProN", "HG Mincho E", "MS Mincho", serif',
    'rounded': '"Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic Medium", "Meiryo", sans-serif'
  }

  // フォントサイズのマッピング
  const fontSizeMap: Record<string, string> = {
    'small': '0.9',
    'medium': '1.0',
    'large': '1.1'
  }

  const fontSizeMultiplier = fontSizeMap[templateSettings.fontSize] || '1.0'

  const computedStyles = {
    '--primary-color': selectedPreset?.primary || templateSettings.primaryColor,
    '--accent-color': selectedPreset?.accent || templateSettings.accentColor,
    '--font-family': fontFamilyMap[templateSettings.fontFamily] || fontFamilyMap['default'],
    '--title-font': fontFamilyMap[templateSettings.titleFont] || fontFamilyMap[templateSettings.fontFamily] || fontFamilyMap['default'],
    '--body-font': fontFamilyMap[templateSettings.bodyFont] || fontFamilyMap[templateSettings.fontFamily] || fontFamilyMap['default'],
    '--font-size-multiplier': fontSizeMultiplier,
    fontSize: `${parseFloat(fontSizeMultiplier) * 16}px`,
    fontFamily: fontFamilyMap[templateSettings.fontFamily] || fontFamilyMap['default'],
    color: selectedPreset?.primary || templateSettings.primaryColor
  }

  // CSS変数デバッグ用ログ
  console.log('CSS変数計算結果:', {
    titleFont: templateSettings.titleFont,
    bodyFont: templateSettings.bodyFont,
    titleFontCSS: computedStyles['--title-font'],
    bodyFontCSS: computedStyles['--body-font'],
    fontSize: templateSettings.fontSize,
    fontSizeCSS: computedStyles['--font-size-multiplier']
  })

  return computedStyles
})

// ロゴURL用computed（相対URLを絶対URLに変換）
const logoImageUrl = computed(() => {
  if (!templateSettings.logoUrl) return ''

  // 既に絶対URLの場合はそのまま返す
  if (templateSettings.logoUrl.startsWith('http') || templateSettings.logoUrl.startsWith('data:')) {
    return templateSettings.logoUrl
  }

  // 相対パスの場合は絶対URLに変換
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8502'
  return `${apiBaseUrl}${templateSettings.logoUrl}`
})

// 設定パネルの開閉
const toggleSettings = () => {
  isSettingsCollapsed.value = !isSettingsCollapsed.value
}

// Methods
const loadSettings = async (retryCount = 0, maxRetries = 3) => {
  try {
    console.log(`設定読み込み開始 (試行${retryCount + 1}/${maxRetries + 1})`)

    const settings = await apiClient.getTemplateSettings()
    console.log('設定読み込み結果:', settings)

    if (settings) {
      // APIから返されるsnake_case形式をcamelCase形式に変換
      templateSettings.businessName = settings.business_name || ''
      templateSettings.operatorName = settings.operator_name || ''
      templateSettings.logoUrl = settings.logo_url || ''
      templateSettings.diagnosisTitle = settings.diagnosis_title || '鑑定書'
      templateSettings.primaryColor = settings.primary_color || '#2c3e50'
      templateSettings.accentColor = settings.accent_color || '#34495e'
      templateSettings.colorTheme = settings.color_theme || 'navy'
      templateSettings.fontFamily = settings.font_family || 'default'
      templateSettings.fontSize = settings.font_size || 'medium'
      templateSettings.titleFont = settings.title_font || 'default'
      templateSettings.bodyFont = settings.body_font || 'default'

      console.log('APIレスポンス生データ:', settings)
      console.log('設定適用後のtemplateSettings:', {
        diagnosisTitle: templateSettings.diagnosisTitle,
        fontSize: templateSettings.fontSize,
        titleFont: templateSettings.titleFont,
        bodyFont: templateSettings.bodyFont,
        colorTheme: templateSettings.colorTheme,
        fontFamily: templateSettings.fontFamily
      })
    } else {
      // APIから設定が返されない場合はデフォルト値を明示的に設定
      console.log('APIから設定が返されないため、デフォルト値を設定')
      templateSettings.diagnosisTitle = '鑑定書'
      templateSettings.fontSize = 'medium'
      templateSettings.titleFont = 'default'
      templateSettings.bodyFont = 'default'
    }

    // 成功した場合はエラーメッセージをクリア
    errorMessage.value = ''

    // 設定読み込み完了後、0.5秒のローディング表示
    setTimeout(() => {
      isPreviewLoading.value = false
    }, 500)

  } catch (error) {
    console.error(`設定の読み込みに失敗 (試行${retryCount + 1}):`, error)

    // リトライ可能なエラーの場合、指定回数まで再試行
    if (retryCount < maxRetries && (
      error.message?.includes('SSL connection') ||
      error.message?.includes('timeout') ||
      error.message?.includes('500') ||
      error.message?.includes('503') ||
      error.message?.includes('OperationalError')
    )) {
      console.log(`データベース接続エラーのためリトライ中... (${retryCount + 1}/${maxRetries})`)
      setTimeout(() => {
        loadSettings(retryCount + 1, maxRetries)
      }, 1000 * (retryCount + 1)) // 1秒、2秒、3秒の間隔でリトライ
      return
    }

    // 最終的な失敗
    errorMessage.value = `設定の読み込みに失敗しました${retryCount > 0 ? ` (${retryCount + 1}回試行)` : ''}`

    // エラーが発生してもローディングを終了
    setTimeout(() => {
      isPreviewLoading.value = false
    }, 1000)
  }
}

// Logo Upload Functions
const logoFileInput = ref<HTMLInputElement>()

const triggerLogoUpload = () => {
  logoFileInput.value?.click()
}

const handleLogoUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  // ファイルサイズチェック (5MB) - バックエンドと同じ制限
  if (file.size > 5 * 1024 * 1024) {
    errorMessage.value = 'ファイルサイズは5MB以下にしてください'
    return
  }

  // ファイル形式チェック
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    errorMessage.value = '対応していないファイル形式です。JPEG、PNG、GIF、WebPのみ対応しています。'
    return
  }

  try {
    errorMessage.value = ''
    successMessage.value = 'ロゴをアップロード中...'

    // 実際のAPIアップロード
    const response = await apiClient.uploadLogo(file)

    if (response.success) {
      // サーバーから返されたURLを設定
      templateSettings.logoUrl = response.logo_url
      successMessage.value = `ロゴが正常にアップロードされました (${Math.round(response.file_size / 1024)}KB)`

      setTimeout(() => {
        successMessage.value = ''
      }, 5000)
    } else {
      throw new Error('アップロードに失敗しました')
    }
  } catch (error) {
    console.error('ロゴアップロードに失敗:', error)
    errorMessage.value = error instanceof Error ? error.message : 'ロゴアップロードに失敗しました'

    // ファイル選択をリセット
    if (logoFileInput.value) {
      logoFileInput.value.value = ''
    }
  }
}

// Handle drag and drop for logo upload
const handleLogoDrop = async (event: DragEvent) => {
  event.preventDefault()
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    if (file.type.startsWith('image/')) {
      await uploadLogoFile(file)
    }
  }
}

const removeLogo = async () => {
  try {
    errorMessage.value = ''
    successMessage.value = 'ロゴを削除中...'

    // 実際のAPI削除
    const response = await apiClient.deleteLogo()

    if (response.success) {
      templateSettings.logoUrl = ''
      successMessage.value = 'ロゴが正常に削除されました'

      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      throw new Error('削除に失敗しました')
    }
  } catch (error) {
    console.error('ロゴ削除に失敗:', error)
    errorMessage.value = error instanceof Error ? error.message : 'ロゴ削除に失敗しました'
  }
}

// Color Preset Selection
const selectColorPreset = (preset: any) => {
  templateSettings.colorTheme = preset.name
  templateSettings.primaryColor = preset.primary
  templateSettings.accentColor = preset.accent

  // カラー変更時にプレビューを更新
  refreshPreview()
}

const saveSettings = async () => {
  try {
    isSaving.value = true
    errorMessage.value = ''
    successMessage.value = ''

    // API用の形式に変換
    const apiSettings = {
      business_name: templateSettings.businessName,
      operator_name: templateSettings.operatorName,
      diagnosis_title: templateSettings.diagnosisTitle,
      color_theme: templateSettings.colorTheme,
      font_family: templateSettings.fontFamily,
      layout_style: 'modern', // 仮の値
      logo_url: templateSettings.logoUrl,
      font_size: templateSettings.fontSize,
      title_font: templateSettings.titleFont,
      body_font: templateSettings.bodyFont
    }

    // Base64画像データがある場合は一時的に除外（データベース制限のため）
    if (apiSettings.logo_url && apiSettings.logo_url.startsWith('data:')) {
      console.log('Base64ロゴデータを除外して保存します（データベース制限のため）')
      apiSettings.logo_url = '' // 空文字で保存
    }

    console.log('templateSettings確認:', {
      diagnosisTitle: templateSettings.diagnosisTitle,
      fontSize: templateSettings.fontSize,
      titleFont: templateSettings.titleFont,
      bodyFont: templateSettings.bodyFont,
      全体: templateSettings
    })
    console.log('保存するAPIデータ:', apiSettings)

    // 値がundefinedの場合、強制的にデフォルト値を設定
    if (!templateSettings.diagnosisTitle) {
      console.log('diagnosisTitleがundefinedのため、デフォルト値を設定')
      templateSettings.diagnosisTitle = '鑑定書'
      apiSettings.diagnosis_title = '鑑定書'
    }
    if (!templateSettings.fontSize) {
      console.log('fontSizeがundefinedのため、デフォルト値を設定')
      templateSettings.fontSize = 'medium'
      apiSettings.font_size = 'medium'
    }
    if (!templateSettings.titleFont) {
      console.log('titleFontがundefinedのため、デフォルト値を設定')
      templateSettings.titleFont = 'default'
      apiSettings.title_font = 'default'
    }
    if (!templateSettings.bodyFont) {
      console.log('bodyFontがundefinedのため、デフォルト値を設定')
      templateSettings.bodyFont = 'default'
      apiSettings.body_font = 'default'
    }

    console.log('修正後のAPIデータ:', apiSettings)
    const result = await apiClient.updateTemplateSettings(apiSettings)
    console.log('保存結果:', result)

    successMessage.value = '設定を保存しました'

    // Success message auto-hide
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    console.error('設定の保存に失敗:', error)
    errorMessage.value = '設定の保存に失敗しました'
  } finally {
    isSaving.value = false
  }
}

const resetToDefaults = () => {
  Object.assign(templateSettings, defaultSettings)
  successMessage.value = 'デフォルト設定に戻しました'
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

const refreshPreview = () => {
  isPreviewLoading.value = true

  // 0.5秒のローディング
  setTimeout(() => {
    isPreviewLoading.value = false
    console.log('プレビューを更新しました')
  }, 500)
}

const formatDate = (date: Date): string => {
  return date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Watchers
watch([
  () => templateSettings.primaryColor,
  () => templateSettings.accentColor
], ([primaryColor, accentColor]) => {
  // Apply CSS variables for live preview
  document.documentElement.style.setProperty('--primary-color', primaryColor)
  document.documentElement.style.setProperty('--accent-color', accentColor)
})

// 自動保存のwatcher - templateSettingsの変更を監視
watch(templateSettings, async (newVal, oldVal) => {
  if (oldVal) { // 初回読み込み時は除外
    console.log('設定変更を検知 - 自動保存開始:', {
      diagnosisTitle: newVal.diagnosisTitle,
      fontSize: newVal.fontSize,
      titleFont: newVal.titleFont,
      bodyFont: newVal.bodyFont,
      全体: newVal
    })
    await saveSettings()
  }
}, { deep: true })

// Lifecycle
onMounted(async () => {
  if (!userStore.isAuthenticated) {
    errorMessage.value = 'ログインが必要です'
    return
  }

  await loadSettings()

  // Apply initial colors
  document.documentElement.style.setProperty('--primary-color', templateSettings.primaryColor)
  document.documentElement.style.setProperty('--accent-color', templateSettings.accentColor)
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';
// 完全独立スタイル - diagnosis-templates.scssをApp.vueで管理することで競合を回避
.template-settings-view {
  @include page-container;
}

.page-header {
  @include page-header;

  .page-title {
    @include page-title;
    display: flex;
    align-items: center;
    gap: 12px;

    .page-title-icon {
      width: 32px;
      height: 32px;
    }
  }

  .page-subtitle {
    @include small-text;
    margin: 0;
    font-style: normal;
    font-weight: 300;
  }
}

.main-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  align-items: start;
  transition: grid-template-columns 0.3s ease;
  min-height: 150vh;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;

    .mobile-panel {
      order: -1;
    }

    .desktop-panel {
      display: none;
    }

    &.settings-collapsed {
      grid-template-columns: 1fr;

      .mobile-panel {
        &.collapsed {
          height: 60px;
          width: 100%;
          background: linear-gradient(90deg, #3498db, #2980b9);

          .panel-header {
            flex-direction: row;
            padding: 16px 24px;

            .collapsed-indicator {
              flex-direction: row;
              gap: 8px;

              .collapsed-text {
                font-size: 14px;
              }
            }

            .collapse-btn .material-icons {
              transform: rotate(0deg);
            }
          }

          &::before {
            display: none;
          }
        }
      }
    }
  }
}

.preview-area {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  overflow: hidden;
  min-height: 1200px;

  .enhanced-preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #e0e0e0;
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);

    .preview-title {
      display: flex;
      align-items: center;
      gap: 12px;

      .material-icons {
        color: var(--primary-main);
        font-size: 1.5rem;
      }

      h2 {
        margin: 0;
        font-size: 1.2rem;
        font-weight: 600;
        color: #2c3e50;
      }
    }

    .preview-controls {
      display: flex;
      align-items: center;
      gap: 16px;

      .preview-zoom {
        display: flex;
        align-items: center;
        gap: 8px;
        background: white;
        border-radius: 8px;
        padding: 4px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

        .zoom-btn {
          background: none;
          border: none;
          padding: 6px;
          border-radius: 4px;
          cursor: pointer;
          transition: background 0.2s ease;
          color: var(--primary-main);

          &:hover {
            background: rgba(52, 152, 219, 0.1);
          }

          .material-icons {
            font-size: 1.2rem;
          }
        }

        .zoom-level {
          font-size: 0.9rem;
          font-weight: 500;
          color: var(--text-primary);
          min-width: 40px;
          text-align: center;
        }
      }

      .refresh-btn {
        background: linear-gradient(135deg, var(--primary-main), var(--primary-dark));
        color: white;
        border: none;
        padding: 10px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);

        &:hover:not(:disabled) {
          background: linear-gradient(135deg, var(--primary-dark), var(--primary-main));
          transform: translateY(-1px);
          box-shadow: 0 4px 16px rgba(52, 152, 219, 0.4);
        }

        &:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .material-icons {
          font-size: 1.1rem;
        }
      }
    }
  }

  .template-preview {
    padding: 24px;
    /* 高さ制限を削除してスクロールバー不要に */
    position: relative;

    .preview-loading {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 400px;
      color: var(--text-secondary);

      .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid var(--primary-main);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 16px;
      }

      p {
        margin: 0;
        font-size: 0.9rem;
        color: var(--text-secondary);
      }

      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    }
  }
}

.settings-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  overflow: hidden;
  transition: all 0.3s ease;

  &.desktop-panel {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 400px;
    max-height: calc(100vh - 40px);
    overflow-y: auto;
    z-index: 10;

    &.collapsed {
      width: 80px;
    }

    @media (max-width: 1200px) {
      display: none;
    }
  }

  &.mobile-panel {
    display: none;

    @media (max-width: 1200px) {
      display: block;
      position: relative;
      top: 0;
      margin-bottom: 24px;
    }
  }

  &.collapsed {
    width: 100px;
    background: linear-gradient(135deg, #3498db, #2980b9);
    border: 2px solid #2980b9;
    box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      transform: scale(1.05);
      box-shadow: 0 8px 25px rgba(52, 152, 219, 0.5);

      .floating-indicator .pulse-ring {
        animation: pulse 1.5s infinite;
      }

      .hover-tooltip {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .panel-header {
      padding: 20px 12px;
      background: transparent;
      border-bottom: none;
      flex-direction: column;
      gap: 12px;
      position: relative;

      .collapsed-indicator {
        position: relative;

        .floating-indicator {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          color: white;
          position: relative;

          .material-icons {
            font-size: 28px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
          }

          .collapsed-text {
            font-size: 12px;
            font-weight: 700;
            text-align: center;
            white-space: nowrap;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
          }

          .pulse-ring {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 50px;
            height: 50px;
            border: 2px solid rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            opacity: 0;
          }
        }

        .hover-tooltip {
          position: absolute;
          top: 100%;
          left: 50%;
          transform: translateX(-50%) translateY(10px);
          background: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 11px;
          white-space: nowrap;
          opacity: 0;
          transition: all 0.3s ease;
          pointer-events: none;
          z-index: 1000;

          &::before {
            content: '';
            position: absolute;
            top: -4px;
            left: 50%;
            transform: translateX(-50%);
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 4px solid rgba(0, 0, 0, 0.8);
          }
        }
      }

      .collapse-btn {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;

        &:hover {
          background: rgba(255, 255, 255, 0.3);
          transform: rotate(180deg);
        }

        .material-icons {
          color: white;
          font-size: 18px;
        }
      }
    }
  }

  .panel-header {
    padding: 20px 24px;
    border-bottom: 1px solid #e0e0e0;
    background: #f8f9fa;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0;
      font-size: 1.2rem;
      font-weight: 600;
      color: #333;
    }

    .collapse-btn {
      background: none;
      border: none;
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      transition: background-color 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;

      &:hover {
        background: rgba(0, 0, 0, 0.1);
      }

      .material-icons {
        font-size: 20px;
        color: #666;
      }
    }
  }

  .panel-content {
    padding: 24px;
    max-height: calc(100vh - 140px);
    overflow-y: auto;
  }
}


.settings-form {
  .form-section {
    margin-bottom: 32px;

    &:last-child {
      margin-bottom: 0;
    }

    h3 {
      margin: 0 0 16px 0;
      font-size: 1.1rem;
      font-weight: 600;
      color: #333;
      padding-bottom: 8px;
      border-bottom: 2px solid #3498db;
    }
  }

  .form-group {
    margin-bottom: 20px;

    label {
      display: block;
      margin-bottom: 6px;
      font-weight: 500;
      color: #333;
      font-size: 0.9rem;
    }

    .form-input {
      width: 100%;
      padding: 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 1rem;
      transition: border-color 0.2s;

      &:focus {
        outline: none;
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
      }

      &.color-input {
        width: 60px;
        height: 40px;
        padding: 4px;
        cursor: pointer;
      }
    }

    /* Enhanced Logo Settings Styles */
    .logo-settings-enhanced {
      .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;

        .section-icon {
          color: #3498db;
          font-size: 1.5rem;
        }

        h3 {
          margin: 0;
          color: #2c3e50;
          font-size: 1.3rem;
          font-weight: 600;
        }
      }

      .logo-upload-container {
        /* Current Logo Card */
        .current-logo-card {
          background: white;
          border-radius: 16px;
          padding: 24px;
          border: 1px solid #e9ecef;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

          .logo-preview-enhanced {
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 120px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 2px dashed #dee2e6;
            margin-bottom: 16px;
            overflow: hidden;

            .logo-image {
              max-width: 200px;
              max-height: 100px;
              object-fit: contain;
              border-radius: 8px;
            }

            .logo-overlay {
              position: absolute;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              background: rgba(0, 0, 0, 0.7);
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 12px;
              opacity: 0;
              transition: opacity 0.3s ease;

              .overlay-btn {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                font-size: 0.9rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;

                .material-icons {
                  font-size: 1.1rem;
                }

                &.change-btn {
                  background: var(--primary-main);
                  color: white;

                  &:hover {
                    background: var(--primary-dark);
                    transform: translateY(-1px);
                  }
                }

                &.remove-btn {
                  background: #e74c3c;
                  color: white;

                  &:hover {
                    background: #c0392b;
                    transform: translateY(-1px);
                  }
                }
              }
            }

            &:hover .logo-overlay {
              opacity: 1;
            }
          }

          .logo-info {
            .logo-status {
              display: flex;
              align-items: center;
              gap: 8px;
              margin: 0;
              color: #27ae60;
              font-size: 0.9rem;
              font-weight: 500;

              .status-icon {
                font-size: 1.1rem;
              }
            }
          }
        }

        /* Upload Zone */
        .upload-zone {
          background: white;
          border: 2px dashed #ced4da;
          border-radius: 16px;
          padding: 48px 24px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
          min-height: 200px;
          display: flex;
          align-items: center;
          justify-content: center;

          &:hover {
            border-color: var(--primary-main);
            background: #f8f9fa;
            transform: translateY(-2px);
          }

          .upload-content {
            .upload-icon {
              font-size: 3rem;
              color: var(--primary-main);
              margin-bottom: 16px;
              display: block;
            }

            h4 {
              margin: 0 0 8px 0;
              color: var(--text-primary);
              font-size: 1.2rem;
              font-weight: 600;
            }

            .upload-subtitle {
              margin: 0 0 24px 0;
              color: var(--text-secondary);
              font-size: 0.9rem;
            }

            .upload-specs {
              display: flex;
              flex-direction: column;
              gap: 8px;

              .spec-item {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                color: var(--text-secondary);
                font-size: 0.85rem;

                .material-icons {
                  font-size: 1rem;
                  color: var(--primary-main);
                }
              }
            }
          }
        }

        .logo-file-input {
          display: none;
        }
      }
    }

    /* Enhanced Font Settings Styles */
    .font-settings-enhanced {
      .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;

        .section-icon {
          color: var(--primary-main);
          font-size: 1.5rem;
        }

        h3 {
          margin: 0;
          color: var(--text-primary);
          font-size: 1.3rem;
          font-weight: 600;
        }
      }

      .font-controls {
        display: flex;
        flex-direction: column;
        gap: 32px;

        .enhanced-label {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 16px;
          font-size: 1.1rem;
          font-weight: 600;
          color: #2c3e50;

          .material-icons {
            color: #3498db;
            font-size: 1.2rem;
            font-family: 'Material Icons';
          }
        }

        .font-family-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;

          @media (max-width: 768px) {
            grid-template-columns: 1fr;
          }

          .font-family-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;

            &:hover {
              border-color: #3498db;
              transform: translateY(-2px);
              box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }

            &.active {
              border-color: #3498db;
              background: rgba(52, 152, 219, 0.05);
              box-shadow: 0 4px 16px rgba(52, 152, 219, 0.2);
            }

            .font-preview {
              font-size: 2rem;
              margin-bottom: 12px;
              color: var(--text-primary);
              line-height: 1;
            }

            .font-name {
              font-weight: 600;
              color: var(--text-primary);
              margin-bottom: 4px;
            }

            .font-description {
              font-size: 0.85rem;
              color: var(--text-secondary);
            }
          }
        }

        .font-size-slider {
          .size-options {
            display: flex;
            gap: 16px;
            justify-content: center;

            .size-option {
              background: white;
              border: 2px solid #e9ecef;
              border-radius: 12px;
              padding: 24px;
              text-align: center;
              cursor: pointer;
              transition: all 0.3s ease;
              min-width: 120px;

              &:hover {
                border-color: var(--primary-main);
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
              }

              &.active {
                border-color: var(--primary-main);
                background: rgba(52, 152, 219, 0.05);
                box-shadow: 0 4px 16px rgba(52, 152, 219, 0.2);
              }

              .size-preview {
                color: var(--text-primary);
                margin-bottom: 12px;
                line-height: 1;
              }

              .size-label {
                font-weight: 600;
                color: var(--text-primary);
                margin-bottom: 4px;
              }

              .size-description {
                font-size: 0.85rem;
                color: var(--text-secondary);
              }
            }
          }
        }
      }
    }

    /* Enhanced Typography Settings Styles */
    .typography-settings-enhanced {
      .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;

        .section-icon {
          color: var(--primary-main);
          font-size: 1.5rem;
        }

        h3 {
          margin: 0;
          color: var(--text-primary);
          font-size: 1.3rem;
          font-weight: 600;
        }
      }

      .typography-controls {
        display: flex;
        flex-direction: column;
        gap: 32px;

        .enhanced-label {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 16px;
          font-size: 1.1rem;
          font-weight: 600;
          color: var(--text-primary);

          .material-icons {
            color: var(--primary-main);
            font-size: 1.2rem;
          }
        }

        .typography-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 16px;

          .typography-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;

            &:hover {
              border-color: #3498db;
              transform: translateY(-2px);
              box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }

            &.active {
              border-color: #3498db;
              background: rgba(52, 152, 219, 0.05);
              box-shadow: 0 4px 16px rgba(52, 152, 219, 0.2);
            }

            .typography-preview {
              margin-bottom: 12px;
              color: var(--text-primary);
              line-height: 1.4;

              &.title-preview {
                font-size: 1.5rem;
                margin-bottom: 8px;
              }

              &.body-preview {
                font-size: 0.9rem;
                line-height: 1.6;
              }
            }

            .typography-name {
              font-weight: 600;
              color: var(--text-primary);
              margin-bottom: 4px;
            }

            .typography-description {
              font-size: 0.85rem;
              color: var(--text-secondary);
            }
          }
        }
      }
    }

    /* Color Presets Styles */
    .color-presets {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
      gap: 12px;
      margin-top: 8px;

      .color-preset {
        padding: 12px;
        border: 2px solid #e1e8ed;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;

        &:hover {
          border-color: var(--primary-main);
          transform: translateY(-2px);
        }

        &.active {
          border-color: var(--primary-main);
          background: rgba(52, 152, 219, 0.1);
        }

        .color-preview {
          display: flex;
          height: 24px;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 8px;

          .primary-color,
          .accent-color {
            flex: 1;
          }
        }

        .preset-name {
          font-size: 0.85rem;
          color: var(--text-secondary);
          font-weight: 500;
        }
      }
    }

    /* Font Size Options */
    .font-size-options {
      display: flex;
      gap: 12px;
      margin-top: 8px;

      .radio-option {
        display: flex;
        align-items: center;
        gap: 6px;
        cursor: pointer;

        input[type="radio"] {
          margin: 0;
        }

        .radio-label {
          font-size: 0.9rem;
          color: var(--text-secondary);
        }
      }
    }

    .form-help {
      margin: 6px 0 0 0;
      font-size: 0.8rem;
      color: #666;
    }
  }

  .form-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    padding-top: 24px;
    border-top: 1px solid #e0e0e0;

    .btn {
      padding: 12px 24px;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      &.btn-secondary {
        background: #f8f9fa;
        color: #666;
        border: 1px solid #ddd;

        &:hover:not(:disabled) {
          background: #e9ecef;
        }
      }

      &.btn-primary {
        background: #3498db;
        color: white;

        &:hover:not(:disabled) {
          background: #2980b9;
        }
      }
    }
  }
}

.error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #e74c3c;
  color: white;
  padding: 12px 20px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 1000;
}

.success-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #27ae60;
  color: white;
  padding: 12px 20px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 1000;
}

@keyframes fadeInOut {
  0% { opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { opacity: 0; }
}

@keyframes pulse {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.8);
  }
  50% {
    opacity: 0.6;
    transform: translate(-50%, -50%) scale(1.2);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(1.4);
  }
}
</style>