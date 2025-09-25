import Eto from "./Eto";


export default class Sangou
{
    private _etos:Array<Eto>;
    private _name:string;
    public static readonly MOKU = new Sangou([Eto.INO,Eto.USA,Eto.HITUJI],"木局三号");
    public static readonly KA = new Sangou([Eto.TORA,Eto.UMA,Eto.INU],"火局三号");
    public static readonly KIN = new Sangou([Eto.MI,Eto.TORI,Eto.USHI],"金局三号");    
    public static readonly SUI = new Sangou([Eto.SARU,Eto.NE,Eto.TATU],"水局三号");


    public static readonly SANGOUS = new Map<number,Sangou>();
    public static ADD_MAP(sangou:Sangou)
    {
        sangou._etos.forEach((eto)=>{
            this.SANGOUS.set(eto.index,sangou);            
        });    
    }
 

    public static static_constructor()
    {
        Sangou.ADD_MAP(Sangou.MOKU);
        Sangou.ADD_MAP(Sangou.KA);
        Sangou.ADD_MAP(Sangou.KIN);
        Sangou.ADD_MAP(Sangou.SUI);
    }    


    constructor(etos:Array<Eto>,name:string)    
    {
        this._etos = etos;
        this._name = name;        
    }

    static of(eto:Eto):Sangou
    {
        return Sangou.SANGOUS.get(eto.index);        
    }

    
    get name()
    {
        return this._name;
    }


    public daisangou(eto:Eto):Eto
    {
        let foundIndex = this._etos.findIndex((val)=>{
            return val.index === eto.index;
        });
        if(foundIndex < 0)
        {
            return null;    
        }
        let nextIndex = (foundIndex + 1) % 3;
        return this._etos[nextIndex];        
    }

    public static ofDaisangou(eto:Eto):Eto
    {
        let sangou = Sangou.of(eto);
        if(sangou === null)
        {
            return null;    
        }

        return sangou.daisangou(eto);
    }
}

Sangou.static_constructor();



