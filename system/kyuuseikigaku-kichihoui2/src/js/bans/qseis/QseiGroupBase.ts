import Qsei from "./Qsei";
import LocalDate from "../../times/LocalDate";
import ArrayUtils from "../../utils/ArrayUtils";
import QseiDay from "../dates/QseiDay";



//九星の年、月、日を一括で保持するクラス
//再利用性を促すため
export default abstract class QseiGroupBase
{
    protected _day:QseiDay;
    protected _month:Qsei;
    protected _year:Qsei;
    protected _date:LocalDate;

    constructor(year:Qsei,month:Qsei,day:QseiDay,date:LocalDate)
    {
        this._year = year;
        this._month= month;
        this._day = day;        
        this._date = date;    
    }

    get day():QseiDay
    {
        return this._day;
    }
    
    get date():LocalDate
    {
        return this._date;
    }    
    
    get month():Qsei
    {
        return this._month;    
    }

    get year():Qsei
    {
        return this._year;    
    }  
    

    public maxKipous(): Array<number> {
        let yearKipous = this._year.findKipous();
        let monthKipous = this._month.findKipous();
        yearKipous = yearKipous.filter((val)=>{
            return val != this._month.index;
        });
        monthKipous = monthKipous.filter((val)=>{
            return val != this._year.index;
        });

        let result = ArrayUtils.and(yearKipous,monthKipous);
        if(this._year.index == this._month.index)
        {
            result = ArrayUtils.sub(result,this._year.findWaki());
        }

        return result;        
    }

    public bigKipous():Array<number>{
        let yearKipous = this._year.findKipous();        
        yearKipous = yearKipous.filter((val)=>{
            return val != this._month.index;
        });
            
        return ArrayUtils.sub(yearKipous,this.maxKipous());
    }



}