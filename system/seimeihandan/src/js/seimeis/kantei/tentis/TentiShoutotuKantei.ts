import Seimei from "../../units/Seimei";
import Kantei from "../Kantei";
import KanteiViewBase from "../KanteiViewBase";
import Msg1KanteiView from "../Msg1KanteiView";


const SHOUTOTU_SET = new Set<number>(
[3,
5,
9
]);

export default class TentiShoutotuKantei{
    public static of(seimei:Seimei):KanteiViewBase
    {
        let seiFirst = seimei.sei[0];
        let meiFirst = seimei.mei[0];

        if(SHOUTOTU_SET.has(seiFirst.kakusu) && SHOUTOTU_SET.has(meiFirst.kakusu))
        {
            return new Msg1KanteiView(seiFirst.name + meiFirst.name,Kantei.TENTI_SHOUTOTU);
        }
        else
        {
            return null;    
        }
    }
}    
