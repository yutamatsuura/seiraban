import Kaku from "../../units/Kaku";
import Kantei from "../Kantei";
import Msg1KanteiView from "../Msg1KanteiView";
import KanteiViewBase from "../KanteiViewBase";


export default class SeimeiDousuuKantei{
    public static of(tenkaku:Kaku,tikaku:Kaku):KanteiViewBase
    {
        if(tenkaku.kakusu == tikaku.kakusu)
        {
            return new Msg1KanteiView(tenkaku.seimei.allNameWithSpace(),Kantei.SEIMEI_DOUSU);
        }
        else
        {
            return null;   
        }
    }
}    
