// 鑑定書作成用の既存システム統合モジュール

class KanteiSystemIntegration {
    constructor() {
        this.cache = new Map(); // データキャッシュ
    }

    /**
     * 既存システムから方位盤データを取得
     * @param {number} year - 生年
     * @param {number} month - 生月
     * @param {number} day - 生日
     * @param {string} gender - 性別 ('male' or 'female')
     * @returns {Promise<Object>} 方位盤データ
     */
    async fetchExistingSystemData(year, month, day, gender = 'male') {
        const cacheKey = `${year}-${month}-${day}-${gender}`;

        // キャッシュ確認
        if (this.cache.has(cacheKey)) {
            console.log('キャッシュからデータを取得:', cacheKey);
            return this.cache.get(cacheKey);
        }

        try {
            // 既存システムからデータ取得
            const data = await this.callExistingSystemAPI(year, month, day, gender);

            // データを整形
            const formattedData = this.formatHoibanData(data);

            // キャッシュに保存
            this.cache.set(cacheKey, formattedData);

            return formattedData;
        } catch (error) {
            console.error('既存システムデータ取得エラー:', error);
            throw error;
        }
    }

    /**
     * 既存システムAPIを呼び出し
     */
    async callExistingSystemAPI(year, month, day, gender) {
        const url = 'https://kigaku-navi.com/qsei/ban_kipou.php';
        const params = {
            birth_y: year,
            birth_m: month.toString().padStart(2, '0'),
            birth_d: day.toString().padStart(2, '0'),
            sex: gender === 'male' ? '1' : '0',
            action: 'calc'
        };

        // プロキシサーバー経由でリクエスト
        const response = await fetch('/api/existing-system-proxy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * 鑑定書用にデータを整形
     */
    formatHoibanData(rawData) {
        return {
            // 基本情報
            birthInfo: {
                date: rawData.birth_info?.date || '',
                yearQsei: rawData.birth_info?.year_qsei || '',
                monthQsei: rawData.birth_info?.month_qsei || '',
                dayQsei: rawData.birth_info?.day_qsei || ''
            },

            // 年盤データ
            yearBan: {
                title: '年盤',
                period: this.calculateYearPeriod(new Date().getFullYear()),
                kiban: rawData.year_ban?.kiban || [],
                center: rawData.year_ban?.center || 5,
                kipous: this.extractKipouInfo(rawData.kipou_info, 'year')
            },

            // 月盤データ
            monthBan: {
                title: '月盤',
                period: this.calculateMonthPeriod(new Date().getMonth() + 1),
                kiban: rawData.month_ban?.kiban || [],
                center: rawData.month_ban?.center || 5,
                kipous: this.extractKipouInfo(rawData.kipou_info, 'month')
            },

            // 日盤データ
            dayBan: {
                title: '日盤',
                period: this.calculateDayPeriod(new Date().getDate()),
                kiban: rawData.day_ban?.kiban || [],
                center: rawData.day_ban?.center || 7,
                kipous: this.extractKipouInfo(rawData.kipou_info, 'day')
            },

            // 総合吉凶判定
            overallKipou: this.analyzeOverallKipou(rawData.kipou_info)
        };
    }

    /**
     * 期間計算
     */
    calculateYearPeriod(year) {
        return `${year}年 (${year}/2/3～${year + 1}/2/3)`;
    }

    calculateMonthPeriod(month) {
        const nextMonth = month === 12 ? 1 : month + 1;
        return `${month}月 (${month}/7～${nextMonth}/7)`;
    }

    calculateDayPeriod(day) {
        return `${day}日`;
    }

    /**
     * 吉凶情報を抽出・整理
     */
    extractKipouInfo(kipouList, banType) {
        if (!kipouList) return [];

        return kipouList
            .filter(kipou => kipou.ban_type === banType || !kipou.ban_type)
            .map(kipou => ({
                type: kipou.type,
                direction: kipou.direction || '',
                description: kipou.text || '',
                level: this.getKipouLevel(kipou.type)
            }))
            .sort((a, b) => b.level - a.level); // 重要度順
    }

    /**
     * 吉凶の重要度レベル
     */
    getKipouLevel(type) {
        const levels = {
            '最大吉方': 10,
            '吉方': 8,
            '五黄殺': -10,
            '暗剣殺': -9,
            '本命殺': -8,
            '月命殺': -7,
            '凶方': -5
        };
        return levels[type] || 0;
    }

    /**
     * 総合吉凶判定
     */
    analyzeOverallKipou(kipouList) {
        if (!kipouList) return { summary: '判定不可', recommendations: [] };

        const goodDirections = kipouList.filter(k => k.type === '最大吉方' || k.type === '吉方');
        const badDirections = kipouList.filter(k => k.type.includes('殺') || k.type === '凶方');

        return {
            summary: `吉方${goodDirections.length}方位、凶方${badDirections.length}方位`,
            goodDirections: goodDirections.map(k => k.direction).filter(Boolean),
            badDirections: badDirections.map(k => k.direction).filter(Boolean),
            recommendations: this.generateRecommendations(goodDirections, badDirections)
        };
    }

    /**
     * 推奨事項を生成
     */
    generateRecommendations(goodDirs, badDirs) {
        const recommendations = [];

        if (goodDirs.length > 0) {
            recommendations.push('🌟 ' + goodDirs.map(d => d.direction).join('、') + '方位への移動や活動がおすすめです');
        }

        if (badDirs.length > 0) {
            recommendations.push('⚠️ ' + badDirs.map(d => d.direction).join('、') + '方位は避けることをお勧めします');
        }

        return recommendations;
    }

    /**
     * 鑑定書用HTMLテンプレートを生成
     */
    generateKanteiHTML(data) {
        return `
        <div class="kantei-hoiban-section">
            <h2>📊 九星気学方位盤鑑定</h2>

            <div class="birth-info">
                <h3>🎂 基本情報</h3>
                <p><strong>生年月日:</strong> ${data.birthInfo.date}</p>
                <p><strong>本命星:</strong> ${data.birthInfo.yearQsei}</p>
                <p><strong>月命星:</strong> ${data.birthInfo.monthQsei}</p>
            </div>

            <div class="hoiban-grid">
                ${this.generateBanHTML(data.yearBan)}
                ${this.generateBanHTML(data.monthBan)}
                ${this.generateBanHTML(data.dayBan)}
            </div>

            <div class="overall-judgment">
                <h3>🎯 総合判定</h3>
                <p>${data.overallKipou.summary}</p>
                <ul>
                    ${data.overallKipou.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        </div>

        <style>
        .kantei-hoiban-section {
            font-family: 'Noto Sans JP', sans-serif;
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        .hoiban-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .ban-item {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 15px;
            background: #f9f9f9;
        }
        .birth-info, .overall-judgment {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        </style>
        `;
    }

    /**
     * 個別盤のHTML生成
     */
    generateBanHTML(banData) {
        return `
        <div class="ban-item">
            <h4>${banData.title}</h4>
            <p><strong>期間:</strong> ${banData.period}</p>
            <p><strong>中央:</strong> ${banData.center}</p>
            <div class="kipou-list">
                ${banData.kipous.map(k => `
                    <span class="kipou-item ${k.level > 0 ? 'good' : 'bad'}">
                        ${k.type} (${k.direction})
                    </span>
                `).join('')}
            </div>
        </div>
        `;
    }
}

// Node.js環境での使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KanteiSystemIntegration;
}

// ブラウザ環境での使用
if (typeof window !== 'undefined') {
    window.KanteiSystemIntegration = KanteiSystemIntegration;
}