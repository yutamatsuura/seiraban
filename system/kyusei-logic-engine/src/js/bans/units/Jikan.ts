

export default class Jikan
{
    private _index:number;
    private _name:string;

    public static readonly KOU = new Jikan(0,"甲");
    public static readonly OTU = new Jikan(1,"乙");
    public static readonly HEI = new Jikan(2,"丙");
    public static readonly TEI = new Jikan(3,"丁");
    public static readonly BO = new Jikan(4,"戊");
    public static readonly KI = new Jikan(5,"己");
    public static readonly KANO = new Jikan(6,"庚");
    public static readonly SIN = new Jikan(7,"辛");
    public static readonly JIN = new Jikan(8,"壬");
    public static readonly MIZ = new Jikan(9,"癸");

    public static readonly JIKANS = new Array<Jikan>(
        Jikan.KOU,
        Jikan.OTU,
        Jikan.HEI,
        Jikan.TEI,
        Jikan.BO,
        Jikan.KI,
        Jikan.KANO,
        Jikan.SIN,
        Jikan.JIN,
        Jikan.MIZ,        
    );

    private constructor(index:number,name:string)
    {
        this._index = index;
        this._name = name;    
    }

    get index():number
    {
        return this._index;
    }    

    get name():string
    {
        return this._name;        
    }    

    public static of(index:number):Jikan
    {
        return Jikan.JIKANS[index];
    }
}