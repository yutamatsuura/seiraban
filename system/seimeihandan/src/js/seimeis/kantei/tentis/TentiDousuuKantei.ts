import Seimei from "../../units/Seimei";
import Kantei from "../Kantei";
import Msg1KanteiView from "../Msg1KanteiView";
import KanteiViewBase from "../KanteiViewBase";


export default class TentiDousuuKantei {
    public static of(seimei:Seimei):KanteiViewBase
    {
        let seiFirst = seimei.sei[0];
        let meiFirst = seimei.mei[0];

        if(seiFirst.kakusu == meiFirst.kakusu)
        {
            let kantei = seiFirst.kakusu % 2 == 0 ? Kantei.TENTI_DOUSU_GUSU:Kantei.TENTI_DOUSU_KISUU;            
            return new Msg1KanteiView(seiFirst.name + meiFirst.name,kantei);
        }
        else
        {
            return null;    
        }
    }
}    
