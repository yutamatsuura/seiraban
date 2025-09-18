import Seimei from "../../units/Seimei";
import KanteiViewBase from "../KanteiViewBase";
import Msg1KanteiView from "../Msg1KanteiView";
import Kantei from "../Kantei";



export default class BunriKantei
{
    public static isAllBunri(seimei:Seimei)
    {
        for(let i = 0; i < seimei.all.length;i++)
        {
            let c = seimei.all[i];
            if(c.isBunri == false)
            {
                return false;    
            }            
        }

        return true;        
    }

    
    public static of(seimei:Seimei):KanteiViewBase
    {
        if(this.isAllBunri(seimei)) 
        {      
            return new Msg1KanteiView(seimei.allNameWithSpace(),Kantei.KUDASI_BUNRI);                
        }
        else
        {        
            return null;        
        }
    }
}