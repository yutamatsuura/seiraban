import Kantei from "../Kantei";
import KanteiViewBase from "../KanteiViewBase";
import Kaku from "../../units/Kaku";



export default class Tigyou9Kantei
{
    public static of(kakusu:number,name:string,kantei:Kantei):KanteiViewBase
    {
        if(kakusu == 9 || kakusu == 19)
        {            
            return new MyView(kakusu,name,kantei);
        }

        return null;        
    }

    public static ofKaku(kaku:Kaku,kantei:Kantei):KanteiViewBase
    {
        return Tigyou9Kantei.of(kaku.kakusu,`${kaku.name}:${kaku.getSeimei()}`,kantei);        
    }

}



class MyView extends KanteiViewBase
{
    private kakusu:number;    
    constructor(kakusu:number,target:string,kantei:Kantei)
    {
        super(target,kantei);
        this.kakusu = kakusu;
    }


    public message()
    {
        return this.msg1.replace("<<kakusu>>",String(this.kakusu));
    }    
}
