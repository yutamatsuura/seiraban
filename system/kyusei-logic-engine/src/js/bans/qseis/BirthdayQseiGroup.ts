import Qsei from "./Qsei";
import LocalDate from "../../times/LocalDate";
import Keisha from "../units/Keisha";
import Doukai from "../units/Doukai";
import Hakka from "../units/Hakka";
import QseiGroupBase from "./QseiGroupBase";
import QseiDay from "../dates/QseiDay";
import QseiDayCreater from "../dates/QseiDayCreater";

const BIRTH_MODIFY = [
    null,
    9,
    6,
    4,
    3,
    -1,
    2,
    8,
    7,
    1    
];

//九星の年、月、日を一括で保持するクラス
//再利用性を促すため
export default class BirthdayQseiGroup extends QseiGroupBase
{
    private _man:boolean;
    private _rewriteMonth:Qsei;
    constructor(year:Qsei,month:Qsei,dayInfo:QseiDay,date:LocalDate,rewriteMonth:Qsei,man:boolean)
    {
        super(year,month,dayInfo,date);
        this._man = man;
        this._rewriteMonth = rewriteMonth;
    }

    public man():boolean
    {
        return this._man;
    }    
    public keisha(man:boolean):Qsei
    {
        let keisha = Keisha.of(this.year.index,this._rewriteMonth.index,man);    
        return Qsei.of(keisha);
    }

    public doukai(man:boolean):Qsei
    {
        let doukai = Doukai.of(this.year.index,this._rewriteMonth.index,man);        
        return Qsei.of(doukai);
    }

    
    public hakka(): Hakka {
        if (this.year.index == this._rewriteMonth.index) {
            //中宮傾斜                
            if (this.year.index === 5) {
                if (this.man) {
                    return Hakka.DAKYUU_K;
                }
                else {
                    return Hakka.KENKYUU_K;
                }
            }
            else {
                return this.year.hakka.reverse();
            }
        }
        else {
            let found = this._rewriteMonth.kiban12.findIndex((val) => {
                return val == this.year.index;
            });

            if (found < 0) {
                return null;
            }

            return Hakka.KEISHAS[found];
        }
    }

  

    public static of(date:LocalDate,man:boolean):BirthdayQseiGroup
    {
        let year = Qsei.getYear(date);    
        let month = Qsei.getMonth(date);
        let day = QseiDayCreater.getDay(date);
        let rewriteMonth = this.getBirthMonth(year,month,man);

        return new BirthdayQseiGroup(year,month,day,date,rewriteMonth,man);        
    }
    
   
    protected static getBirthMonth(year:Qsei,month:Qsei,man:boolean):Qsei
    {
        if(year.index == month.index)
        {
            let modify = BIRTH_MODIFY[year.index];
            if(modify == -1)
            {
                if(man)    
                {
                    return Qsei.SEVEN;
                }
                else
                {
                    return Qsei.SIX;
                }
            }
            else
            {
                return Qsei.of(modify);
            }            
        }
        else
        {
            return month;    
        }
    }
}