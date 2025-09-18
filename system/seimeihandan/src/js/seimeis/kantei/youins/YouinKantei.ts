import Seimei from "../../units/Seimei";
import Kantei from "../Kantei";
import Msg1KanteiView from "../Msg1KanteiView";
import KanteiViewBase from "../KanteiViewBase";




interface ICountReport {
    youCount: number;
    inCount: number;
}



abstract class KanteiJudgeBase {
    private _result: Kantei;

    constructor(url: Kantei) {
        this._result = url;
    }
    
    get result() {
        return this._result;
    }

    public count(items: Array<boolean>): ICountReport {
        let youCount = 0;
        let inCount = 0;
        items.forEach((c) => {
            if (c) {
                youCount++;
            }
            else {
                inCount++;
            }
        });

        return {
            youCount: youCount,
            inCount: inCount
        };
    }



    public abstract action(seis: Array<boolean>, meis: Array<boolean>, alls: Array<boolean>,rev:boolean): boolean;
}

class Katayori extends KanteiJudgeBase {
    private rev:boolean;
    constructor(kantei:Kantei,rev:boolean) {
        super(kantei);
        this.rev = rev;
    }

    public action(seis: Array<boolean>, meis: Array<boolean>, alls: Array<boolean>,rev:boolean): boolean {
        if(this.rev != rev)
        {
            return false;    
        }
        
        for (let i = 0; i < seis.length; i++) {
            let c = seis[i];
            if (c == false) {
                return false;
            }
        }

        for (let i = 0; i < meis.length; i++) {
            let c = meis[i];
            if (c == false) {
                return false;
            }
        }

        return true;
    }
}


class Chudan extends KanteiJudgeBase {
    constructor() {
        super(Kantei.INYOU_CHUDAN);
    }

    public action(seis: Array<boolean>, meis: Array<boolean>, alls: Array<boolean>): boolean {
        for (let i = 0; i < seis.length; i++) {
            let c = seis[i];
            if (c == false) {
                return false;
            }
        }

        for (let i = 0; i < meis.length; i++) {
            let c = meis[i];
            if (c == true) {
                return false;
            }
        }

        return true;
    }
}

class Makinaoshi extends KanteiJudgeBase {
    private youOver: boolean;
    constructor(kantei:Kantei,judge:boolean) {
        super(kantei);
        this.youOver = judge;
    }

    private preJudge(alls: Array<boolean>): boolean {
        let i = 0;
        for (; i < alls.length; i++) {
            let c = alls[i];
            if (c == false) {
                break;
            }
        }

        for (; i < alls.length; i++) {
            let c = alls[i];
            if (c == true) {
                //陰が連続するべきなのに、途中で陽になったら    
                return false;
            }
        }

        //陽が連続した後に、陰が連続した        
        return true;
    }



    public action(seis: Array<boolean>, meis: Array<boolean>, alls: Array<boolean>): boolean {
        //まず連続が2回しているかを判定
        if (this.preJudge(alls) == false) {
            return false;
        }

        let count = this.count(alls);
        let youOver = count.inCount < count.youCount;
        if (youOver === this.youOver) {
            return true;
        }
        else {
            return false;
        }        
    }
}

class HanInyou extends KanteiJudgeBase {
    constructor() {
        super(Kantei.INYOU_INYOU);
    }

    public action(seis: Array<boolean>, meis: Array<boolean>, alls: Array<boolean>): boolean {
        let seiLast = seis[seis.length - 1];
        let meiFirst = meis[0];
        if (seiLast != meiFirst) {
            let report = this.count(meis);
            if (0 < report.inCount && 0 < report.youCount) {
                return true;
            }
        }
        return false;
    }
}


class Shibari extends KanteiJudgeBase {
    constructor() {
        super(Kantei.INYOU_SHIBARI);
    }

    public action(seis: Array<boolean>, meis: Array<boolean>, alls: Array<boolean>): boolean {
        return true;
    }
}




class Ohbasami extends KanteiJudgeBase {
    constructor() {
        super(Kantei.INYOU_OHBASAMI);
    }

    public action(seis: Array<boolean>, meis: Array<boolean>, alls: Array<boolean>): boolean {
        let seiLast = seis[seis.length - 1];
        let meiFirst = meis[0];
        if (seiLast == meiFirst) {
            let seiReport = this.count(seis);
            let meiReport = this.count(meis);

            if (seiLast) {
                //陽だったら    
                if (0 < seiReport.inCount && 0 < meiReport.inCount) {                 
                    return true;
                }
            }
            else {
                //陰だったら    
                if (0 < seiReport.youCount && 0 < meiReport.youCount) {
                    return true;
                }
            }
        }

        return false;
    }
}



class NijuBasami extends KanteiJudgeBase {
    constructor() {
        super(Kantei.INYOU_NIJU_BASAMI);
    }

    public action(seis: Array<boolean>, meis: Array<boolean>, alls: Array<boolean>): boolean {    
        for (let i = seis.length; i < alls.length - 2; i++) {
            let item = alls[i];
            if (item == false) {
                let beforeReport = this.count(alls.slice(0, i));
                let afterReport = this.count(alls.slice(i + 1));
                if (beforeReport.inCount == 0 && afterReport.inCount == 0) {
                    return true;
                }
            }
        }

        return false;
    }
}

export default class YouinKantei {
    public static readonly JUDGES = [
        new NijuBasami(),
        new Ohbasami(),
        new Katayori(Kantei.INYOU_SIRO_KATAYORI,false),
        new Katayori(Kantei.INYOU_KURO_KATAYORI,true),
        new Chudan(),
        new Makinaoshi(Kantei.INYOU_UE_MAKINAOSI, false),
        new Makinaoshi(Kantei.INYOU_SITA_MAKINAOSI, true),        
        new HanInyou(),
        new Shibari()
    ];





    //全てを陽にするメソッド
    static toNormalze(youins: Array<boolean>, first: boolean): Array<boolean> {
        let result = new Array<boolean>();
        if (first) {
            //はじめの文字が陽だった場合にはそのまま格納
            youins.forEach((youin) => {
                result.push(youin);
            });
        }
        else {
            //はじめの文字が陰だった場合には陽に反転する
            youins.forEach((youin) => {
                result.push(!youin);
            });
        }

        return result;
    }




    public static of(seimei: Seimei): KanteiViewBase {
        let seis = new Array<boolean>();
        seimei.sei.forEach((sei) => {
            seis.push(sei.youin.you);
        });

        let meis = new Array<boolean>();
        seimei.mei.forEach((mei) => {
            meis.push(mei.youin.you);
        });

        let title = seimei.allNameWithSpace();
        return YouinKantei.ofNormalize(title, seis, meis,!seimei.mei[0].youin.you);
    }

    //テストしやすくするために、今回のメソッドを用意
    public static ofNormalize(title: string, unNormSeis: Array<boolean>, unNormMeis: Array<boolean>,rev:boolean): KanteiViewBase 
    {
        let seis = YouinKantei.toNormalze(unNormSeis, unNormSeis[0]);
        let meis = YouinKantei.toNormalze(unNormMeis, unNormSeis[0]);

        let alls = seis.slice().concat(meis);

        for (let i = 0; i < YouinKantei.JUDGES.length; i++) {
            let judge = YouinKantei.JUDGES[i];
            if (judge.action(seis, meis, alls,rev)) {
                return new Msg1KanteiView(title, judge.result);
            }
        }

        return null;
    }
}