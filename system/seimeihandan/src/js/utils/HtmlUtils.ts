


//HTML関連の操作を行うクラス
export default class HtmlUtils {
    public static rgb2Hex(orig: string): string {
        let rgb = orig.replace(/\s/g, '').match(/^rgba?\((\d+),(\d+),(\d+)/i);
        return (rgb && rgb.length === 4) ?
            ("0" + parseInt(rgb[1], 10).toString(16)).slice(-2) +
            ("0" + parseInt(rgb[2], 10).toString(16)).slice(-2) +
            ("0" + parseInt(rgb[3], 10).toString(16)).slice(-2) : orig;
    }

    public static paramList(): Map<string, string> {
        let result = new Map<string, string>();

        var urlParam = location.search.substring(1);
        if (urlParam != "") {
            urlParam.split('&').forEach((str) => {
                let params = str.split('=');
                if (2 <= params.length) {
                    result.set(params[0], params[1]);
                }
            });
        }

        return result;
    }

    public static zeroPadding(num: string, length: number) {
        return ('0000000000' + num).slice(-length);
    }

    public static toHex(moji: string): string {
        let hex = moji.codePointAt(0)
            .toString(16)
            .toLocaleUpperCase();
        let length = Math.max(4, hex.length);
        return `U+${HtmlUtils.zeroPadding(hex, length)}`;
    }

    public static setLocalJPDate(): void {
        $.datepicker.setDefaults({
            closeText: "閉じる",
            prevText: "&#x3C;前",
            nextText: "次&#x3E;",
            currentText: "今日",
            monthNames: ["1月", "2月", "3月", "4月", "5月", "6月",
                "7月", "8月", "9月", "10月", "11月", "12月"],
            monthNamesShort: ["1月", "2月", "3月", "4月", "5月", "6月",
                "7月", "8月", "9月", "10月", "11月", "12月"],
            dayNames: ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"],
            dayNamesShort: ["日", "月", "火", "水", "木", "金", "土"],
            dayNamesMin: ["日", "月", "火", "水", "木", "金", "土"],
            weekHeader: "週",
            dateFormat: "yy年mm月dd日",
            firstDay: 0,
            isRTL: false,
            showMonthAfterYear: true,
            yearSuffix: "年"
        });
    }

    public static getCheck(name: string): boolean {
        return $(`#${name}:checked`).val() == "on";
    }
}
