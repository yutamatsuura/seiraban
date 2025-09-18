import KanteiViewBase from "../KanteiViewBase";
import Seimei from "../../units/Seimei";
import Kantei from "../Kantei";


const EXCLUDES = new Set<string>(
    [
        Kantei.KUDASI_HAPPY.eng,
        Kantei.KUDASI_SONKI.eng
    ])
    

export default class YomikudasiViewKantei {

    public static of(seimei: Seimei): Array<KanteiViewBase> {
        let result = new Array<KanteiViewBase>();

        seimei.ngs.forEach((ng) => {
            ng.reasons.forEach((reason) => {
                let kantei = Kantei.of(reason.reason);
                if(EXCLUDES.has(kantei.eng))
                {                
                    result.push(new ExcludeMyView(reason.sp, ng.name, kantei));
                }
                else
                {
                    result.push(new MyView(reason.sp, ng.name, kantei));
                }                
            });
        });

        return result;
    }
}



class MyView extends KanteiViewBase {
    private overrideText: string;
    constructor(overrideText: string, target: string, kantei: Kantei) {
        super(target, kantei);
        this.overrideText = overrideText;
    }

    public message() {
        if (this.overrideText == "") {
            return this.msg1;
        }
        else {
            return this.overrideText;
        }
    }
}
class ExcludeMyView extends KanteiViewBase {
    private overrideText: string;
    constructor(overrideText: string, target: string, kantei: Kantei) {
        super(target, kantei);
        this.overrideText = overrideText;
    }

    public isView(score:number)
    {        
        console.log(score);
        return score < this.findScore(Kantei.SCORE_KYOU_OR_KIPOU);
    }

    public getOrder()
    {
        return -10;    
    }


    public message() {
        if (this.overrideText == "") {
            return this.msg1;
        }
        else {
            return this.overrideText;
        }
    }
}
