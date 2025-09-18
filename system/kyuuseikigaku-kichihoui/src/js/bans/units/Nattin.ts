
export default class Nattin
{
    private _name:string;
    private _rubi:string;
    private _index:number;

    private constructor(index:number,name:string,rubi:string)    
    {
        this._index = index;
        this._name = name;
        this._rubi = rubi;    
    }

    get index()
    {
        return this._index;    
    }    

    get name()
    {
        return this._name;    
    }    

    get rubi()
    {
        return this._rubi;    
    }    

    static readonly VALUES = [
        new Nattin(0,"海中金","かいちゅうきん"),  
        new Nattin(1,"炉中火","ろちゅうか"),  
        new Nattin(2,"大林木","たいりんぼく"),
        new Nattin(3,"路傍土","ろぼうど"),  
        new Nattin(4,"釼鋒金","じんぼうきん"), 
        new Nattin(5,"山頭火","さんとうか"),   
        new Nattin(6,"澗下水","かんかすい"),   
        new Nattin(7,"城頭土","じょうとうど"),  
        new Nattin(8,"白鑞金","はくろうきん"),  
        new Nattin(9,"楊柳木","ようりゅうぼく"),
        new Nattin(10,"井泉水","せいせんすい"), 
        new Nattin(11,"屋上土","おくじょうど"), 
        new Nattin(12,"霹靂火","へきれきか"),   
        new Nattin(13,"松柏木","しょうはくぼく"),  
        new Nattin(14,"長流水","ちょうりゅうすい"),

        new Nattin(15,"沙中金","さちゅうきん"),
        new Nattin(16,"山下火","さんげか"),  
        new Nattin(17,"平地木","へいちぼく"),   
        new Nattin(18,"壁上土","へきじょうど"), 
        new Nattin(19,"金箔金","きんぱくきん"), 
        new Nattin(20,"覆燈火","ふくとうか"),   
        new Nattin(21,"天河水","てんがすい"),   
        new Nattin(22,"大駅土","たいえきど"),   
        new Nattin(23,"釵釧金","さいせんきん"),  
        new Nattin(24,"桑柘木","そうしゃくもく"),
        new Nattin(25,"大溪水","だいけいすい"), 
        new Nattin(26,"沙中土","さちゅうど"),   
        new Nattin(27,"天上火","てんじょうか"), 
        new Nattin(28,"柘榴木","ざくろぼく"),   
        new Nattin(29,"大海水","大海水"),
    ]

    public static of(index:number):Nattin
    {
        return Nattin.VALUES[index];
    }

}