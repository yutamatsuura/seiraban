import Seimei from "../../units/Seimei";
import Kantei from "../Kantei";
import Msg1KanteiView from "../Msg1KanteiView";
import KanteiViewBase from "../KanteiViewBase";



export default class OneCharaKantei extends Msg1KanteiView
{
    public static of(seimei:Seimei):KanteiViewBase
    {
        if(seimei.mei.length == 1)    
        {
            return new Msg1KanteiView(seimei.mei[0].name,Kantei.KUDASI_ONE_CHARA);
        }
        else
        {
            return null;    
        }
    }
}