import Kaku from "../../units/Kaku";
import Kantei from "../Kantei";
import KanteiViewBase from "../KanteiViewBase";


const VIEW = new Set<number>(
[9,19]    
);



export default class KakusuKantei{
    private static getTitle(kaku: Kaku): string {
        return `${kaku.name}:${kaku.getSeimeiWithSpace()}`;
    }


    public static of(kaku: Kaku): KanteiViewBase {
        if(VIEW.has(kaku.kakusu))    
        {
            let kantei = Kantei.KAKUSUES.get(kaku.kakusu);
            let title = KakusuKantei.getTitle(kaku);
            return new MyView(title,kantei);        
        }
        else
        {
            return null;    
        }
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
        return this.score != 0;
    }    

    public message():string
    {
        return `${this.msg1}。${this.msg2}`;
    }
}