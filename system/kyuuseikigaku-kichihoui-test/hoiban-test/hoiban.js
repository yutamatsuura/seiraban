// 九星気学方位盤計算ロジック（JavaScript実装）

// 月盤テーブル（Qsei.ts:9-22から移植）
const MONTH_TABLE = [
    [8, 2, 5],  // 2月 添字0
    [7, 1, 4],  // 3月 添字1
    [6, 9, 3],  // 4月 添字2
    [5, 8, 2],  // 5月 添字3
    [4, 7, 1],  // 6月 添字4
    [3, 6, 9],  // 7月 添字5
    [2, 5, 8],  // 8月 添字6
    [1, 4, 7],  // 9月 添字7
    [9, 3, 6],  // 10月 添字8
    [8, 2, 5],  // 11月 添字9
    [7, 1, 4],  // 12月 添字10
    [6, 9, 3],  // 13月 添字11
];

// 九星データ（Qsei.ts:36-117から簡略化）
const QSEI_DATA = {
    1: { name: "一白水星", kiban8: [6, 4, 8, 9, 5, 7, 3, 2], gogyou: "水" },
    2: { name: "二黒土星", kiban8: [7, 5, 9, 1, 6, 8, 4, 3], gogyou: "土" },
    3: { name: "三碧木星", kiban8: [8, 6, 1, 2, 7, 9, 5, 4], gogyou: "木" },
    4: { name: "四緑木星", kiban8: [9, 7, 2, 3, 8, 1, 6, 5], gogyou: "木" },
    5: { name: "五黄土星", kiban8: [1, 8, 3, 4, 9, 2, 7, 6], gogyou: "土" },
    6: { name: "六白金星", kiban8: [2, 9, 4, 5, 1, 3, 8, 7], gogyou: "金" },
    7: { name: "七赤金星", kiban8: [3, 1, 5, 6, 2, 4, 9, 8], gogyou: "金" },
    8: { name: "八白土星", kiban8: [4, 2, 6, 7, 3, 5, 1, 9], gogyou: "土" },
    9: { name: "九紫火星", kiban8: [5, 3, 7, 8, 4, 6, 2, 1], gogyou: "火" },
};

// 五行相関（Gogyou.ts:11-15から移植）
const GOGYOU_DATA = {
    "木": { seiki: "水", taiki: "火", shozoku: [3, 4] },
    "火": { seiki: "木", taiki: "土", shozoku: [9] },
    "土": { seiki: "火", taiki: "金", shozoku: [2, 5, 8] },
    "金": { seiki: "土", taiki: "水", shozoku: [6, 7] },
    "水": { seiki: "金", taiki: "木", shozoku: [1] },
};

// 方位インデックス（北=0, 東北=1, 東=2...）
const HOUI_NAMES = ["北", "東北", "東", "東南", "南", "西南", "西", "西北"];

// 十二支と方位の対応（簡略化）
const ETO_HOUI_MAP = {
    0: 0,  // 子 → 北
    1: 1,  // 丑 → 東北
    2: 2,  // 寅 → 東北
    3: 2,  // 卯 → 東
    4: 3,  // 辰 → 東南
    5: 3,  // 巳 → 東南
    6: 4,  // 午 → 南
    7: 5,  // 未 → 西南
    8: 5,  // 申 → 西南
    9: 6,  // 酉 → 西
    10: 7, // 戌 → 西北
    11: 7  // 亥 → 西北
};

// 吉凶方位定義
const KIPOU_TYPES = {
    // 吉方位
    SAIDAI: { name: "最大吉方", type: "吉", priority: 1 },
    DAIKI: { name: "吉方", type: "吉", priority: 2 },
    DOUKAI: { name: "同会吉方", type: "吉", priority: 3 },
    TENDOU: { name: "天道", type: "吉", priority: 4 },
    TAISAI: { name: "太歳", type: "吉", priority: 5 },
    GEKKEN: { name: "月建", type: "吉", priority: 6 },
    NISSIN: { name: "日辰", type: "吉", priority: 7 },

    // 凶方位
    GOOU: { name: "五黄殺", type: "凶", priority: 1 },
    ANKEN: { name: "暗剣殺", type: "凶", priority: 2 },
    SAIHA: { name: "歳破", type: "凶", priority: 3 },
    GEPPA: { name: "月破", type: "凶", priority: 4 },
    NIPPA: { name: "日破", type: "凶", priority: 5 },
    HONMEI: { name: "本命殺", type: "凶", priority: 6 },
    GETUMEI: { name: "月命殺", type: "凶", priority: 7 },
    HONMEI_TEKI: { name: "本命的殺", type: "凶", priority: 8 },
    GETUMEI_TEKI: { name: "月命的殺", type: "凶", priority: 9 },
    TEII_TEKI: { name: "定位対冲", type: "凶", priority: 10 }
};

class HoibanCalculator {
    constructor() {}

    // 方位の対角計算（Houi.ts:60-70から移植）
    getOppositeHoui(houiIndex) {
        if (houiIndex === -1) return -1; // 中央
        return (houiIndex + 4) % 8;
    }

    // 年干支計算（簡略化）
    getYearEto(year) {
        return year % 12;
    }

    // 月干支計算（簡略化）
    getMonthEto(year, month) {
        return (month - 1) % 12;
    }

    // 日干支計算（簡略化）
    getDayEto(year, month, day) {
        const date = new Date(year, month - 1, day);
        const daysSinceEpoch = Math.floor(date.getTime() / (1000 * 60 * 60 * 24));
        return daysSinceEpoch % 12;
    }

    // 詳細吉凶判定（Kipou.ts:46-118から移植）
    calculateDetailedKipous(kiban, centerQsei, birthYearQsei, birthMonthQsei, year, month, day, banType) {
        const kipousByDirection = Array(8).fill(null).map(() => []);

        // 干支による歳破・太歳計算
        let taisaiIndex = -1;
        let hakaiIndex = -1;

        if (banType === 'year') {
            const yearEto = this.getYearEto(year);
            taisaiIndex = ETO_HOUI_MAP[yearEto];
            hakaiIndex = this.getOppositeHoui(taisaiIndex);
        } else if (banType === 'month') {
            const monthEto = this.getMonthEto(year, month);
            taisaiIndex = ETO_HOUI_MAP[monthEto];
            hakaiIndex = this.getOppositeHoui(taisaiIndex);
        } else if (banType === 'day') {
            const dayEto = this.getDayEto(year, month, day);
            taisaiIndex = ETO_HOUI_MAP[dayEto];
            hakaiIndex = this.getOppositeHoui(taisaiIndex);
        }

        // 本命的殺・月命的殺の位置計算
        const honMeiIndex = kiban.findIndex(val => val === birthYearQsei);
        const honMeiTekiIndex = honMeiIndex === -1 ? -1 : (honMeiIndex + 4) % 8;

        const getuMeiIndex = kiban.findIndex(val => val === birthMonthQsei);
        const getuMeiTekiIndex = getuMeiIndex === -1 ? -1 : (getuMeiIndex + 4) % 8;

        // 各方位の吉凶判定
        for (let i = 0; i < 8; i++) {
            const k = kiban[i]; // この方位にある九星
            const oppositeK = kiban[(i + 4) % 8]; // 対角の九星

            // 五黄殺
            if (k === 5) {
                kipousByDirection[i].push({ type: 'GOOU', ...KIPOU_TYPES.GOOU });
            }

            // 暗剣殺
            if (oppositeK === 5) {
                kipousByDirection[i].push({ type: 'ANKEN', ...KIPOU_TYPES.ANKEN });
            }

            // 歳破・月破・日破
            if (hakaiIndex === i) {
                if (banType === 'year') {
                    kipousByDirection[i].push({ type: 'SAIHA', ...KIPOU_TYPES.SAIHA });
                } else if (banType === 'month') {
                    kipousByDirection[i].push({ type: 'GEPPA', ...KIPOU_TYPES.GEPPA });
                } else if (banType === 'day') {
                    kipousByDirection[i].push({ type: 'NIPPA', ...KIPOU_TYPES.NIPPA });
                }
            }

            // 太歳・月建・日辰
            if (taisaiIndex === i) {
                if (banType === 'year') {
                    kipousByDirection[i].push({ type: 'TAISAI', ...KIPOU_TYPES.TAISAI });
                } else if (banType === 'month') {
                    kipousByDirection[i].push({ type: 'GEKKEN', ...KIPOU_TYPES.GEKKEN });
                } else if (banType === 'day') {
                    kipousByDirection[i].push({ type: 'NISSIN', ...KIPOU_TYPES.NISSIN });
                }
            }

            // 本命殺
            if (k === birthYearQsei) {
                kipousByDirection[i].push({ type: 'HONMEI', ...KIPOU_TYPES.HONMEI });
            }

            // 本命的殺
            if (honMeiTekiIndex !== -1 && k === kiban[honMeiTekiIndex]) {
                kipousByDirection[i].push({ type: 'HONMEI_TEKI', ...KIPOU_TYPES.HONMEI_TEKI });
            }

            // 月命殺
            if (k === birthMonthQsei) {
                kipousByDirection[i].push({ type: 'GETUMEI', ...KIPOU_TYPES.GETUMEI });
            }

            // 月命的殺
            if (getuMeiTekiIndex !== -1 && k === kiban[getuMeiTekiIndex]) {
                kipousByDirection[i].push({ type: 'GETUMEI_TEKI', ...KIPOU_TYPES.GETUMEI_TEKI });
            }

            // 定位対冲（九星の定位と現在位置が対角）
            const qseiOriginalHoui = this.getQseiOriginalHoui(k);
            if (qseiOriginalHoui !== -1 && this.getOppositeHoui(qseiOriginalHoui) === i) {
                kipousByDirection[i].push({ type: 'TEII_TEKI', ...KIPOU_TYPES.TEII_TEKI });
            }

            // 基本吉方（既存ロジック）
            const basicKipous = this.findKipous(centerQsei);
            if (basicKipous.includes(k)) {
                const isMaxKipou = this.isMaxKipou(k, centerQsei, birthYearQsei, birthMonthQsei);
                if (isMaxKipou) {
                    kipousByDirection[i].push({ type: 'SAIDAI', ...KIPOU_TYPES.SAIDAI });
                } else {
                    kipousByDirection[i].push({ type: 'DAIKI', ...KIPOU_TYPES.DAIKI });
                }
            }
        }

        return kipousByDirection;
    }

    // 九星の定位方位取得
    getQseiOriginalHoui(qseiIndex) {
        const originalPositions = { 1: 0, 2: 5, 3: 2, 4: 3, 5: -1, 6: 7, 7: 6, 8: 1, 9: 4 };
        return originalPositions[qseiIndex] || -1;
    }

    // 最大吉方判定
    isMaxKipou(qseiIndex, centerQsei, birthYearQsei, birthMonthQsei) {
        const yearKipous = this.findKipous(birthYearQsei);
        const monthKipous = this.findKipous(birthMonthQsei);

        // 年盤と月盤両方の吉方で、かつ年命星・月命星と重複しない
        return yearKipous.includes(qseiIndex) &&
               monthKipous.includes(qseiIndex) &&
               qseiIndex !== birthYearQsei &&
               qseiIndex !== birthMonthQsei;
    }

    // 年盤計算（Qsei.ts:248-262から修正移植）
    calculateYearQsei(year, month, day) {
        // 正確な節入り調整（QseiDate.of()ロジック）
        let targetYear = year;
        const setu = this.calculateSetuEnters(year);
        const currentDate = new Date(year, month - 1, day);
        const setuRissyun = setu[0]; // 2月節入り

        if (currentDate < setuRissyun) {
            targetYear = year - 1;
        }

        // Qsei.ts:248-258のgetYearSubメソッド実装
        let mod = targetYear % 9;
        if (mod === 0) {
            mod = 9;
        } else if (mod === 1) {
            mod = 10;
        }

        const result = 11 - mod;
        console.log(`年星計算: targetYear=${targetYear}, mod=${mod}, result=${result}`);
        return result;
    }

    // 月盤計算（Qsei.ts:266-270から正確移植）
    calculateMonthQsei(year, month, day) {
        const yearQsei = this.calculateYearQsei(year, month, day);

        // QseiDateの月インデックス計算
        const qseiDate = this.calculateQseiDate(year, month, day);
        const monthIndex = qseiDate.monthIndex;

        const index2 = (yearQsei - 1) % 3;
        const result = MONTH_TABLE[monthIndex][index2];
        console.log(`月星計算: year=${year}, month=${month}, day=${day}`);
        console.log(`  yearQsei=${yearQsei}, monthIndex=${monthIndex}, index2=${index2}`);
        console.log(`  MONTH_TABLE[${monthIndex}][${index2}] = ${result}`);
        return result;
    }

    // QseiDate計算（QseiDate.ts:131-175から移植）
    calculateQseiDate(year, month, day) {
        const currentDate = new Date(year, month - 1, day);
        const currentSetu = this.calculateSetuEnters(year);
        const beforeSetu = this.calculateSetuEnters(year - 1);

        let qseiYear = year;
        let monthIndex = -1;

        if (currentDate < currentSetu[0]) { // 2月節入り前
            qseiYear = year - 1;
            const lastSetu = beforeSetu[beforeSetu.length - 1]; // 前年12月節入り
            if (currentDate < lastSetu) {
                monthIndex = 10; // 12月扱い
            } else {
                monthIndex = 11; // 13月扱い
            }
        } else {
            // 今年系の月判定
            for (let i = 0; i < currentSetu.length; i++) {
                if (currentDate < currentSetu[i]) {
                    monthIndex = i - 1;
                    break;
                }
            }
            if (monthIndex === -1) {
                monthIndex = currentSetu.length - 1; // 最後の月
            }
        }

        return {
            year: qseiYear,
            monthIndex: monthIndex
        };
    }

    // 日盤計算（QseiDayCreater.ts完全実装）
    calculateDayQsei(year, month, day) {
        const targetDate = new Date(year, month - 1, day);

        // 前年夏至から開始
        const geshi = this.calculateGeshi(year - 1);
        const kirikaeStart = this.toKirikae(geshi);

        let current = new Date(kirikaeStart);
        let qsei = 1; // 一白水星からスタート
        let isGeshi = true; // 夏至期間フラグ

        while (current <= targetDate) {
            const nextKirikae = this.getNextKirikae(current, isGeshi);

            if (targetDate < nextKirikae) {
                return qsei;
            }

            current = nextKirikae;
            qsei = this.getNextQsei(qsei, isGeshi);

            // 夏至/冬至の切り替えチェック
            const currentYear = current.getFullYear();
            const touji = this.calculateTouji(currentYear);
            const nextGeshi = this.calculateGeshi(currentYear + 1);

            if (current >= touji && isGeshi) {
                isGeshi = false; // 冬至期間に移行
            } else if (current >= nextGeshi && !isGeshi) {
                isGeshi = true; // 夏至期間に移行
            }
        }

        return qsei;
    }

    // 夏至計算（Setu.ts参考）
    calculateGeshi(year) {
        const D = 21.851;
        const A = 0.2422;
        const Y = year - 1900;
        const day = Math.floor(D + (A * Y)) - Math.floor(Y / 4);
        return new Date(year, 5, day); // 6月
    }

    // 冬至計算
    calculateTouji(year) {
        const D = 22.747;
        const A = 0.2422;
        const Y = year - 1900;
        const day = Math.floor(D + (A * Y)) - Math.floor(Y / 4);
        return new Date(year, 11, day); // 12月
    }

    // 切替日計算（60日周期）
    toKirikae(date) {
        const mjd = this.toMJD(date);
        const mod60 = (mjd + 50) % 60;
        const daysToAdd = mod60 === 0 ? 0 : (60 - mod60);

        const result = new Date(date);
        result.setDate(result.getDate() + daysToAdd);
        return result;
    }

    // 次の切替日
    getNextKirikae(current, isGeshi) {
        const result = new Date(current);
        result.setDate(result.getDate() + 60);
        return result;
    }

    // 次の九星
    getNextQsei(currentQsei, isGeshi) {
        if (isGeshi) {
            // 夏至期間: 1→8→3→4→9→2→7→6→5
            const geshiOrder = [1, 8, 3, 4, 9, 2, 7, 6, 5];
            const currentIndex = geshiOrder.indexOf(currentQsei);
            return geshiOrder[(currentIndex + 1) % 9];
        } else {
            // 冬至期間: 1→2→3→4→5→6→7→8→9
            return (currentQsei % 9) + 1;
        }
    }

    // MJD計算（JikanEto.ts参考）
    toMJD(date) {
        const y = date.getFullYear();
        const m = date.getMonth() + 1;
        const d = date.getDate();

        return Math.floor(365.25 * y) +
               Math.floor(y / 400) -
               Math.floor(y / 100) +
               Math.floor(30.59 * (m - 2)) +
               d - 678912;
    }

    // 節入り日計算（Setu.ts:46-86から移植）
    calculateSetuEnters(year) {
        const SETU_DATA = [
            { month: 2, D: 3.895, A: 0.2422, year: 0 },    // 立春(2月)
            { month: 3, D: 5.621, A: 0.2422, year: 0 },    // 啓蟄(3月)
            { month: 4, D: 5.085, A: 0.2422, year: 0 },    // 清明(4月)
            { month: 5, D: 5.520, A: 0.2422, year: 0 },    // 立夏(5月)
            { month: 6, D: 6.318, A: 0.2422, year: 0 },    // 芒種(6月)
            { month: 7, D: 7.108, A: 0.2422, year: 0 },    // 小暑(7月)
            { month: 8, D: 7.834, A: 0.2422, year: 0 },    // 立秋(8月)
            { month: 9, D: 8.518, A: 0.2422, year: 0 },    // 白露(9月)
            { month: 10, D: 8.142, A: 0.2422, year: 0 },   // 寒露(10月)
            { month: 11, D: 7.438, A: 0.2422, year: 0 },   // 立冬(11月)
            { month: 12, D: 7.130, A: 0.2422, year: 0 },   // 大雪(12月)
            { month: 1, D: 5.486, A: 0.2422, year: 1 }     // 大寒(翌年1月)
        ];

        const results = [];

        SETU_DATA.forEach(setu => {
            const targetYear = year + setu.year;
            const Y = targetYear - 1900;
            const day = Math.floor(setu.D + (setu.A * Y)) - Math.floor(Y / 4);
            results.push(new Date(targetYear, setu.month - 1, day));
        });

        return results;
    }

    // 吉方位計算（Qsei.ts:234-245から移植）
    findKipous(qseiIndex) {
        const qsei = QSEI_DATA[qseiIndex];
        const gogyou = GOGYOU_DATA[qsei.gogyou];

        // 脇（同五行で本命星以外）
        let waki = gogyou.shozoku.filter(val => val !== qseiIndex);

        // 生気・退気
        let seikiShozoku = GOGYOU_DATA[gogyou.seiki].shozoku;
        let taikiShozoku = GOGYOU_DATA[gogyou.taiki].shozoku;

        let result = [...waki, ...seikiShozoku, ...taikiShozoku];
        result = result.filter(val => val !== 5); // 五黄除外

        return [...new Set(result)].sort(); // 重複除去&ソート
    }

    // 特定人物用方位盤データ生成（生年月日の人の現在時点での方位盤）
    generateHoibanForPerson(currentYear, currentMonth, currentDay, birthYearQsei, birthMonthQsei) {
        const yearQsei = this.calculateYearQsei(currentYear, currentMonth, currentDay);
        const monthQsei = this.calculateMonthQsei(currentYear, currentMonth, currentDay);
        const dayQsei = this.calculateDayQsei(currentYear, currentMonth, currentDay);

        const yearKiban = QSEI_DATA[yearQsei].kiban8;
        const monthKiban = QSEI_DATA[monthQsei].kiban8;
        const dayKiban = QSEI_DATA[dayQsei].kiban8;

        // 詳細吉凶判定（生年月日の本命星・月命星を使用）
        const yearDetailedKipous = this.calculateDetailedKipous(yearKiban, yearQsei, birthYearQsei, birthMonthQsei, currentYear, currentMonth, currentDay, 'year');
        const monthDetailedKipous = this.calculateDetailedKipous(monthKiban, monthQsei, birthYearQsei, birthMonthQsei, currentYear, currentMonth, currentDay, 'month');
        const dayDetailedKipous = this.calculateDetailedKipous(dayKiban, dayQsei, birthYearQsei, birthMonthQsei, currentYear, currentMonth, currentDay, 'day');

        return {
            meta: {
                currentDate: `${currentYear}年${currentMonth}月${currentDay}日`,
                birthYearQsei: { index: birthYearQsei, name: QSEI_DATA[birthYearQsei].name },
                birthMonthQsei: { index: birthMonthQsei, name: QSEI_DATA[birthMonthQsei].name },
                currentYearQsei: { index: yearQsei, name: QSEI_DATA[yearQsei].name },
                currentMonthQsei: { index: monthQsei, name: QSEI_DATA[monthQsei].name },
                currentDayQsei: { index: dayQsei, name: QSEI_DATA[dayQsei].name }
            },
            yearBan: {
                center: yearQsei,
                kiban: yearKiban,
                detailedKipous: yearDetailedKipous,
                summary: this.summarizeKipous(yearDetailedKipous, yearKiban)
            },
            monthBan: {
                center: monthQsei,
                kiban: monthKiban,
                detailedKipous: monthDetailedKipous,
                summary: this.summarizeKipous(monthDetailedKipous, monthKiban)
            },
            dayBan: {
                center: dayQsei,
                kiban: dayKiban,
                detailedKipous: dayDetailedKipous,
                summary: this.summarizeKipous(dayDetailedKipous, dayKiban)
            }
        };
    }

    // 方位盤データ生成
    generateHoiban(year, month, day) {
        const yearQsei = this.calculateYearQsei(year, month, day);
        const monthQsei = this.calculateMonthQsei(year, month, day);
        const dayQsei = this.calculateDayQsei(year, month, day);

        const yearKiban = QSEI_DATA[yearQsei].kiban8;
        const monthKiban = QSEI_DATA[monthQsei].kiban8;
        const dayKiban = QSEI_DATA[dayQsei].kiban8;

        // 詳細吉凶判定
        const yearDetailedKipous = this.calculateDetailedKipous(yearKiban, yearQsei, yearQsei, monthQsei, year, month, day, 'year');
        const monthDetailedKipous = this.calculateDetailedKipous(monthKiban, monthQsei, yearQsei, monthQsei, year, month, day, 'month');
        const dayDetailedKipous = this.calculateDetailedKipous(dayKiban, dayQsei, yearQsei, monthQsei, year, month, day, 'day');

        return {
            meta: {
                date: `${year}年${month}月${day}日`,
                yearQsei: { index: yearQsei, name: QSEI_DATA[yearQsei].name },
                monthQsei: { index: monthQsei, name: QSEI_DATA[monthQsei].name },
                dayQsei: { index: dayQsei, name: QSEI_DATA[dayQsei].name }
            },
            yearBan: {
                center: yearQsei,
                kiban: yearKiban,
                detailedKipous: yearDetailedKipous,
                summary: this.summarizeKipous(yearDetailedKipous, yearKiban)
            },
            monthBan: {
                center: monthQsei,
                kiban: monthKiban,
                detailedKipous: monthDetailedKipous,
                summary: this.summarizeKipous(monthDetailedKipous, monthKiban)
            },
            dayBan: {
                center: dayQsei,
                kiban: dayKiban,
                detailedKipous: dayDetailedKipous,
                summary: this.summarizeKipous(dayDetailedKipous, dayKiban)
            }
        };
    }


    // 吉凶サマリー作成（修正版）
    summarizeKipous(detailedKipous, kiban) {
        const summary = { 吉方: [], 凶方: [], 普通: [] };

        detailedKipous.forEach((kipous, index) => {
            const houiName = HOUI_NAMES[index];
            const qseiIndex = kiban[index];
            const qseiName = QSEI_DATA[qseiIndex].name.substring(0, 1);

            if (kipous.length === 0) {
                summary.普通.push(`${houiName}(${qseiName})`);
            } else {
                const hasKyou = kipous.some(k => k.type === '凶');
                const hasKichi = kipous.some(k => k.type === '吉');

                if (hasKyou) {
                    const kyouNames = kipous.filter(k => k.type === '凶').map(k => k.name);
                    summary.凶方.push(`${houiName}(${qseiName}): ${kyouNames.join(', ')}`);
                } else if (hasKichi) {
                    const kichiNames = kipous.filter(k => k.type === '吉').map(k => k.name);
                    summary.吉方.push(`${houiName}(${qseiName}): ${kichiNames.join(', ')}`);
                } else {
                    summary.普通.push(`${houiName}(${qseiName})`);
                }
            }
        });

        return summary;
    }

    // 特定人物用方位盤視覚化
    printHoibanForPerson(hoibanData) {
        console.log("=== 九星気学方位盤（詳細吉凶判定付き） ===");
        console.log(`鑑定日: ${hoibanData.meta.currentDate}`);
        console.log(`本命星: ${hoibanData.meta.birthYearQsei.name}`);
        console.log(`月命星: ${hoibanData.meta.birthMonthQsei.name}`);
        console.log();

        // 年盤
        console.log("【年盤】");
        this.printBan(hoibanData.yearBan);
        this.printDetailedKipous("年盤", hoibanData.yearBan);
        console.log();

        // 月盤
        console.log("【月盤】");
        this.printBan(hoibanData.monthBan);
        this.printDetailedKipous("月盤", hoibanData.monthBan);
        console.log();

        // 日盤
        console.log("【日盤】");
        this.printBan(hoibanData.dayBan);
        this.printDetailedKipous("日盤", hoibanData.dayBan);
    }

    // 方位盤視覚化（コンソール出力）
    printHoiban(hoibanData) {
        console.log("=== 九星気学方位盤（詳細吉凶判定付き） ===");
        console.log(hoibanData.meta.date);
        console.log(`本命星: ${hoibanData.meta.yearQsei.name}`);
        console.log(`月命星: ${hoibanData.meta.monthQsei.name}`);
        console.log();

        // 年盤
        console.log("【年盤】");
        this.printBan(hoibanData.yearBan);
        this.printDetailedKipous("年盤", hoibanData.yearBan);
        console.log();

        // 月盤
        console.log("【月盤】");
        this.printBan(hoibanData.monthBan);
        this.printDetailedKipous("月盤", hoibanData.monthBan);
        console.log();

        // 日盤
        console.log("【日盤】");
        this.printBan(hoibanData.dayBan);
        this.printDetailedKipous("日盤", hoibanData.dayBan);
    }

    printBan(banData) {
        const kiban = banData.kiban;
        const center = banData.center;
        const detailedKipous = banData.detailedKipous || [];

        // 吉凶マーク取得関数
        const getKipouMark = (index) => {
            if (!detailedKipous[index] || detailedKipous[index].length === 0) return "  ";

            const hasKyou = detailedKipous[index].some(k => k.type === '凶');
            const hasKichi = detailedKipous[index].some(k => k.type === '吉');

            if (hasKyou && hasKichi) return "△";  // 混在
            if (hasKyou) return "×";              // 凶
            if (hasKichi) return "○";             // 吉
            return "  ";                          // 普通
        };

        // 詳細情報取得関数
        const getDetailInfo = (index) => {
            if (!detailedKipous[index] || detailedKipous[index].length === 0) return "";

            const kipouNames = detailedKipous[index].map(k => k.name.substring(0, 2)).join(",");
            return kipouNames.length > 8 ? kipouNames.substring(0, 8) + "..." : kipouNames;
        };

        console.log("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓");
        console.log(`┃                         方位盤                          ┃`);
        console.log("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫");
        console.log(`┃     ${QSEI_DATA[kiban[0]].name.substring(0,1)}${getKipouMark(0)}     ┃     ${QSEI_DATA[kiban[1]].name.substring(0,1)}${getKipouMark(1)}     ┃     ${QSEI_DATA[kiban[2]].name.substring(0,1)}${getKipouMark(2)}     ┃`);
        console.log(`┃     北      ┃     東北     ┃     東      ┃`);
        console.log(`┃ ${getDetailInfo(0).padEnd(10)} ┃ ${getDetailInfo(1).padEnd(11)} ┃ ${getDetailInfo(2).padEnd(10)} ┃`);
        console.log("┣━━━━━━━━━━━━━┫━━━━━━━━━━━━━━┫━━━━━━━━━━━━━┫");
        console.log(`┃   ${QSEI_DATA[kiban[7]].name.substring(0,1)}${getKipouMark(7)}     ┃     ${QSEI_DATA[center].name.substring(0,1)}      ┃     ${QSEI_DATA[kiban[3]].name.substring(0,1)}${getKipouMark(3)}   ┃`);
        console.log(`┃   西北      ┃     中央     ┃     東南    ┃`);
        console.log(`┃ ${getDetailInfo(7).padEnd(10)} ┃              ┃ ${getDetailInfo(3).padEnd(10)} ┃`);
        console.log("┣━━━━━━━━━━━━━┫━━━━━━━━━━━━━━┫━━━━━━━━━━━━━┫");
        console.log(`┃     ${QSEI_DATA[kiban[6]].name.substring(0,1)}${getKipouMark(6)}     ┃     ${QSEI_DATA[kiban[5]].name.substring(0,1)}${getKipouMark(5)}     ┃     ${QSEI_DATA[kiban[4]].name.substring(0,1)}${getKipouMark(4)}     ┃`);
        console.log(`┃     西      ┃     西南     ┃     南      ┃`);
        console.log(`┃ ${getDetailInfo(6).padEnd(10)} ┃ ${getDetailInfo(5).padEnd(11)} ┃ ${getDetailInfo(4).padEnd(10)} ┃`);
        console.log("┗━━━━━━━━━━━━━┻━━━━━━━━━━━━━━┻━━━━━━━━━━━━━┛");
        console.log("○:吉方 ×:凶方 △:混在");
    }

    printDetailedKipous(banName, banData) {
        if (!banData.summary) return;

        console.log(`${banName} 詳細吉凶判定:`);

        if (banData.summary.吉方.length > 0) {
            console.log(`  🟢 吉方: ${banData.summary.吉方.join(', ')}`);
        }

        if (banData.summary.凶方.length > 0) {
            console.log(`  🔴 凶方: ${banData.summary.凶方.join(', ')}`);
        }

        if (banData.summary.普通.length > 0) {
            console.log(`  ⚪ 普通: ${banData.summary.普通.join(', ')}`);
        }
    }
}

// ブラウザ環境対応
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HoibanCalculator;
}