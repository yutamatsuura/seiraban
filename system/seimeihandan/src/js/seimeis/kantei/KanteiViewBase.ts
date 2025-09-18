import Kantei from "./Kantei";
import KanteiResult from "./KanteiResult";


export default abstract class KanteiViewBase
{
    private _target:string;    
    private _kantei:Kantei;
    private _kanteiResult:KanteiResult;
    private _messages:{[key:string]:KanteiResult};

    constructor(target:string,kantei:Kantei)
    {
        this._target = target;
        this._kantei = kantei;
    }

    get viewTitle()
    {
        return this._kantei.viewtitle;    
    }

    set messages(messages:{[key:string]:KanteiResult})
    {
        this._messages = messages;    
    }

    public findScore(kantei:Kantei):number
    {
        return this._messages[kantei.eng].score;
    }
    

    get target()
    {
        return this._target;    
    }        

    get kantei()
    {
        return this._kantei;    
    }    

    get result()
    {
        return this._kanteiResult;    
    }    

    get title()
    {
        return this.kantei.jp;        
    }

    set result(kanteiResult:KanteiResult)    
    {
        this._kanteiResult = kanteiResult;    
    }

    get msg1()
    {
        if(this._kanteiResult == null)    
        {
            return "";    
        }
        else
        {
            return this._kanteiResult.msg1;    
        }        
    }

    
    get msg2()
    {
        if(this._kanteiResult == null)    
        {
            return "";    
        }
        else
        {
            return this._kanteiResult.msg2;    
        }        
    }

    get score()
    {
        if(this._kanteiResult == null)    
        {
            return "";    
        }
        else
        {
            return this._kanteiResult.score;
        }        
    }

    public abstract message():string;
    

    public isView(totalScore:number):boolean
    {
        return true;
    }

    public getOrder():number
    {
        return 0;    
    }
}