import Seimei from "../../units/Seimei";
import KanteiViewBase from "../KanteiViewBase";
import Gogyou from "../../units/Gogyou";
import Msg1KanteiView from "../Msg1KanteiView";
import Kantei from "../Kantei";


export default class TigyouSuiKantei
{    
    public static of(seimei:Seimei):KanteiViewBase
    {
        if(seimei.mei[0].gogyou == Gogyou.SUI)        
        {
            return new Msg1KanteiView(seimei.mei[0].name,Kantei.KUDASI_SUI);            
        }
        else
        {        
            return null;        
        }
    }
}