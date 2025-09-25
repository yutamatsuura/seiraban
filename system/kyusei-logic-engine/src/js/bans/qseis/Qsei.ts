import Gogyou from "../units/Gogyou";
import LocalDate from "../../times/LocalDate";
import Hakka from "../units/Hakka";
import Houi from "../units/Houi";
import QseiDate from "../dates/QseiDate";



const MONTH_TABLE = [
    [8, 2, 5],					//2月 添字0
    [7, 1, 4],					//3月 添字1
    [6, 9, 3],					//4月 添字2
    [5, 8, 2],					//5月 添字3
    [4, 7, 1],					//6月 添字4
    [3, 6, 9],					//7月 添字5
    [2, 5, 8],					//8月 添字6
    [1, 4, 7],					//9月 添字7
    [9, 3, 6],					//10月 添字8
    [8, 2, 5],					//11月 添字9
    [7, 1, 4],					//12月 添字10
    [6, 9, 3],					//13月 添字11
];



export default class Qsei {
    private _index: number;
    private _houi: Houi;
    private _name: string;
    private _rubi: string;
    private _gogyou: Gogyou;
    private _hakka: Hakka;
    private _kiban8: Array<number>;
    private _kiban12: Array<number>;

    public static readonly ONE = new Qsei(
        1,
        Houi.NORTH,
        "一白水星",
        "いっぱくすいせい",
        Gogyou.SUI_KIPOU,
        Hakka.KANKYUU_K,
        [6, 4, 8, 9, 5, 7, 3, 2]
    );

    public static readonly TWO = new Qsei(
        2,
        Houi.SOUTH_WEST,
        "二黒土星",
        "じこくどせい",
        Gogyou.DO_KIPOU,
        Hakka.KONKYUU_K,
        [7, 5, 9, 1, 6, 8, 4, 3]
    );
    public static readonly THREE = new Qsei(
        3,
        Houi.EAST,
        "三碧木星",
        "さんぺきもくせい",
        Gogyou.MOKU_KIPOU,
        Hakka.SINKYUU_K,
        [8, 6, 1, 2, 7, 9, 5, 4]
    );
    public static readonly FOUR = new Qsei(
        4,
        Houi.SOUTH_EAST,
        "四緑木星",
        "しろくもくせい",
        Gogyou.MOKU_KIPOU,
        Hakka.SONKYUU_K,
        [9, 7, 2, 3, 8, 1, 6, 5]
    );
    public static readonly FIVE = new Qsei(
        5,
        Houi.CHUUOU,
        "五黄土星",
        "ごおうどせい",
        Gogyou.DO_KIPOU,
        Hakka.TAIKYOKU,
        [1, 8, 3, 4, 9, 2, 7, 6]
    );
    public static readonly SIX = new Qsei(
        6,
        Houi.NORTH_WEST,
        "六白金星",
        "ろっぱくきんせい",
        Gogyou.KIN_KIPOU,
        Hakka.KENKYUU_K,
        [2, 9, 4, 5, 1, 3, 8, 7]
    );
    public static readonly SEVEN = new Qsei(
        7,
        Houi.WEST,
        "七赤金星",
        "しちせききんせい",
        Gogyou.KIN_KIPOU,
        Hakka.DAKYUU_K,
        [3, 1, 5, 6, 2, 4, 9, 8]
    );
    public static readonly EIGHT = new Qsei(
        8,
        Houi.NORTH_EAST,
        "八白土星",
        "はっぱくどせい",
        Gogyou.DO_KIPOU,
        Hakka.GONKYUU_K,
        [4, 2, 6, 7, 3, 5, 1, 9]
    );
    public static readonly NINE = new Qsei(
        9,
        Houi.SOUTH,
        "九紫火星",
        "きゅうしかせい",
        Gogyou.KA_KIPOU,
        Hakka.RIKYUU_K,
        [5, 3, 7, 8, 4, 6, 2, 1]
    );


    public static readonly KOUTEN_JOUI = new Qsei(
        5,
        null,
        "後天定位",
        "こうてんじょうい",
        null,
        Hakka.RIKYUU_K,
        [1, 8, 3, 4, 9, 2, 7, 6]
    );

    public static readonly SENTEN_JOUI = new Qsei(
        -1,
        null,
        "先天定位",
        "先天てんじょうい",
        null,
        Hakka.RIKYUU_K,
        [2, 3, 9, 7, 6, 4, 1, 8]
    );    




    public static readonly ARRAYS = new Array<Qsei>(
        null,
        Qsei.ONE,
        Qsei.TWO,
        Qsei.THREE,
        Qsei.FOUR,
        Qsei.FIVE,
        Qsei.SIX,
        Qsei.SEVEN,
        Qsei.EIGHT,
        Qsei.NINE,
    );
    constructor(index: number, houi: Houi, name: string, rubi: string, gogyou: Gogyou, hakka: Hakka, kiban8: Array<number>) {
        this._index = index;
        this._houi = houi;
        this._name = name;
        this._rubi = rubi;
        this._hakka = hakka;
        this._gogyou = gogyou;
        this._kiban8 = kiban8;
        this._kiban12 = Qsei.toKiban12(kiban8);
    }

    private static toKiban12(kibanSrc: Array<number>): Array<number> {
        if (kibanSrc.length != 8) {
            throw new Error("パラメータが規定値以外でした");
        }

        return [
            kibanSrc[0],
            kibanSrc[1],
            kibanSrc[1],
            kibanSrc[2],
            kibanSrc[3],
            kibanSrc[3],
            kibanSrc[4],
            kibanSrc[5],
            kibanSrc[5],
            kibanSrc[6],
            kibanSrc[7],
            kibanSrc[7]
        ];
    }


    public static of(index: number): Qsei {
        return Qsei.ARRAYS[index];
    }

    get index(): number {
        return this._index;
    }

    get kiban8(): Array<number> {
        return this._kiban8.slice();
    }

    get kiban12(): Array<number> {
        return this._kiban12.slice();
    }

    get name(): string {
        return this._name;
    }

    get hakka(): Hakka {
        return this._hakka;
    }

    get rubi(): string {
        return this._rubi;
    }

    get gogyou(): Gogyou {
        return this._gogyou;
    }

    get houi(): Houi {
        return this._houi;
    }

    public getHeadName(): string {
        return this.name.substring(0, 1);
    }

    public findWaki(): Array<number> {        
        return this.gogyou.shozoku.filter((val) => {
            return val != this.index;
        });
    }

    public findKipous(): Array<number> {
        let result = this.findWaki();
        result = result.concat(Gogyou.of(this.gogyou.seiki).shozoku);
        result = result.concat(Gogyou.of(this.gogyou.taiki).shozoku);
        result = result.filter((val) => {
            return val != 5;
        });

        result = result.sort();


        return result;
    }

    private static getYearSub(year: number): number {
        let mod = year % 9;
        if (mod == 0) {
            mod = 9;
        }
        else if (mod == 1) {
            mod = 10;
        }

        return 11 - mod;
    }


    public static getYear(date: LocalDate): Qsei {
        return Qsei.of(this.getYearSub(QseiDate.of(date).year));
    }


    public static getMonth(date: LocalDate): Qsei {
        let qseiDate = QseiDate.of(date);    
        let index2 = (Qsei.getYear(date).index - 1) % 3;
        return Qsei.of(MONTH_TABLE[qseiDate.monthIndex][index2]);
    }


    static toText(qseiIndexs: Array<number>): string {
        if(qseiIndexs.length == 0)
        {
            return "ー";    
        }
        let qsei = new Array<string>();
        qseiIndexs.forEach((index) => {
            qsei.push(Qsei.of(index).name);
        });

        return qsei.join(",");
    }
}

