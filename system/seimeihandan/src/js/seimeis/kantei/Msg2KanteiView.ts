import Kantei from "./Kantei";
import KanteiViewBase from "./KanteiViewBase";


export default class Msg2KanteiView extends KanteiViewBase
{
    constructor(target:string,kantei:Kantei)
    {
        super(target,kantei);
    }

    public message():string
    {
        return this.msg2;    
    }
}