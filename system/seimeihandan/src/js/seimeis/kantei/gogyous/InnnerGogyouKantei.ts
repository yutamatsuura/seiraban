import Seimei from "../../units/Seimei";
import Kantei from "../Kantei";
import Msg1KanteiView from "../Msg1KanteiView";
import KanteiViewBase from "../KanteiViewBase";


export default class InnerGogyouKantei 
{
    private static countGogyouKind(seimei:Seimei):number
    {
        let kinds = new Set<string>();
        seimei.all.forEach((val)=>{
            kinds.add(val.gogyou.jp);
        });

        return kinds.size;        
    }

    public static of(seimei:Seimei):KanteiViewBase
    {
        if(3 <= this.countGogyouKind(seimei))
        {
            return new Msg1KanteiView(
                seimei.allNameWithSpace(),
                Kantei.GOGYOU_BALANCE_OK
            );
        }
        else
        {
            return new Msg1KanteiView(
                seimei.allNameWithSpace(),
                Kantei.GOGYOU_BALANCE_NG
            );
        }
    }
}