import Kaku from "../../units/Kaku";
import Kantei from "../Kantei";
import KanteiViewBase from "../KanteiViewBase";




export default class SoukakuKantei{
    private static getTitle(kaku: Kaku): string {
        let name = kaku.seimei.allNameWithSpace();
        let beginIndex = kaku.beginIndexWithSpace();
        let endIndex = kaku.endIndexWithSpace();
        let viewName = name.substring(beginIndex, endIndex + 1);

        return `${kaku.name}:${viewName}`;
    }


    public static of(kaku: Kaku): KanteiViewBase{
        let kantei = Kantei.KAKUSUES.get(kaku.kakusu);
        let title = SoukakuKantei.getTitle(kaku);
        return new MyView(title,kantei);        
    }
}



class MyView extends KanteiViewBase
{
    constructor(target:string,kantei:Kantei)
    {
        super(target,kantei);
    }

    public isView()
    {  
        return true;                  
    }    

    public message():string
    {
        return `${this.msg1}。${this.msg2}`;
    }
}