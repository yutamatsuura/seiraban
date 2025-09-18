import KanteiBase from "../KanteiViewBase";
import Seimei from "../../units/Seimei";
import Kantei from "../Kantei";
import Msg1KanteiView from "../Msg1KanteiView";







export default class JinkakuGogyouKantei
{
    public static of(seimei:Seimei):KanteiBase
    { 
        let seiLast = seimei.sei[seimei.sei.length - 1];
        let meiFirst = seimei.mei[0];

        let key = seiLast.gogyou.key(meiFirst.gogyou);
        let kantei = Kantei.of(key);
        let name = seiLast.name + meiFirst.name;


        return new Msg1KanteiView("人格："+name,kantei);
    }
}    
