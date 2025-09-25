

export default class Eto60
{
    private _index:number;    
    private static readonly TENKAI = [
        "寺鼠","乳牛","寝虎","野兎","出世竜","王様蛇",
        "兵隊馬","野羊","大猿","家鳥","狂犬","勇猪",
        "野鼠","耕牛","暴虎","家兎","上り竜","怒り蛇",
        "種馬","毛羊","王猿","水鳥","猟犬","遊猪",
        "木鼠","水牛","走虎","月兎","隠し竜","寝蛇",
        "競馬","白羊","赤猿","闘鳥","野犬","病猪",
        "家鼠","牧牛","母虎","玉兎","下り竜","長蛇",
        "神馬","病羊","山猿","野鳥","猛犬","家猪",
        "溝鼠","牽牛","猛虎","狡兎","寝竜","巻蛇",
        "荷馬","物言羊","芸猿","軍鳥","愛犬","荒猪",        
    ];

    private constructor(index:number)
    {
        this._index = index;
    }

    get index()
    {
        return this._index;
    }

    get name()
    {
        return Eto60.TENKAI[this._index];
    }

    get lastName()
    {
        let name = Eto60.TENKAI[this._index];
        return name.substring(name.length - 1,name.length);
    }    

    public static of(index:number):Eto60
    {
        return new Eto60(index);            
    }


}