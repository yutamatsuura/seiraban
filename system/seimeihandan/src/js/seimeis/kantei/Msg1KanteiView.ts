import Kantei from "./Kantei";
import KanteiViewBase from "./KanteiViewBase";


export default class Msg1KanteiView extends KanteiViewBase
{
    constructor(target:string,kantei:Kantei)
    {
        super(target,kantei);
    }

    public message():string
    {
        return this.msg1;
    }
}