const HoibanCalculator = require('./hoiban.js');

// テストケース：1982年10月12日生まれの人の現在時点での方位盤
const calculator = new HoibanCalculator();

console.log("=== 九星気学方位盤ロジックテスト ===");
console.log("生年月日: 1982年10月12日男性");
console.log("鑑定日: 2025年9月24日（現在）");
console.log();

// 生年月日で本命星・月命星を計算
const birthData = calculator.generateHoiban(1982, 10, 12);
const birthYearQsei = birthData.meta.yearQsei.index;
const birthMonthQsei = birthData.meta.monthQsei.index;

console.log(`本命星: ${birthData.meta.yearQsei.name}`);
console.log(`月命星: ${birthData.meta.monthQsei.name}`);
console.log();

// 現在時点での方位盤データ生成
const currentData = calculator.generateHoibanForPerson(2025, 9, 24, birthYearQsei, birthMonthQsei);

// 結果出力
calculator.printHoibanForPerson(currentData);

console.log();
console.log("=== 計算詳細 ===");
console.log("【生年月日計算】");
console.log(`本命星: ${birthData.meta.yearQsei.name} (1982年計算)`);
console.log(`月命星: ${birthData.meta.monthQsei.name} (1982年10月計算)`);

console.log();
console.log("【現在時点計算】");
console.log(`現在年盤: ${currentData.meta.currentYearQsei.name} (2025年)`);
console.log(`現在月盤: ${currentData.meta.currentMonthQsei.name} (2025年9月)`);
console.log(`現在日盤: ${currentData.meta.currentDayQsei.name} (2025年9月24日)`);

console.log();
console.log("=== JSON出力 ===");
console.log(JSON.stringify(currentData, null, 2));