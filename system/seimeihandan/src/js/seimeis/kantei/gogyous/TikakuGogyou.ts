import KanteiBase from "../KanteiViewBase";
import Seimei from "../../units/Seimei";
import Kantei from "../Kantei";
import Msg2KanteiView from "../Msg2KanteiView";






export default class TikakuGogyouKantei
{                
    public static of(seimei:Seimei):KanteiBase
    {
        if(seimei.mei.length < 2)
        {
            return null;    
        }
        let mei0 = seimei.mei[0];
        let mei1 = seimei.mei[1];

        let key = mei0.gogyou.key(mei1.gogyou);
        let kantei = Kantei.of(key);
        let name = mei0.name + mei1.name;        
        return new MyView("地格：" + name,kantei);
    }
}    


class MyView extends Msg2KanteiView
{
    constructor(target:string,kantei:Kantei)
    {
        super(target,kantei);        
    }

    public isView()
    {
        return this.score != 0;        
    }    
}

