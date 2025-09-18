import Qsei from "./Qsei";
import LocalDate from "../../times/LocalDate";
import QseiGroupBase from "./QseiGroupBase";
import QseiDay from "../dates/QseiDay";
import QseiDayCreater from "../dates/QseiDayCreater";



//九星の年、月、日を一括で保持するクラス
//再利用性を促すため
export default class CurrentQseiGroup extends QseiGroupBase
{
    constructor(year:Qsei,month:Qsei,dayInfo:QseiDay,date:LocalDate)
    {
        super(year,month,dayInfo,date);        
    }
    

    public static of(date:LocalDate):CurrentQseiGroup
    {
        let year = Qsei.getYear(date);
        let month = Qsei.getMonth(date);
        let dayInfo = QseiDayCreater.getDay(date);
        return new CurrentQseiGroup(year,month,dayInfo,date);
    }

    //日課九星の演算は重いため、一括計算したものをパラメータとして渡す    
    public static ofLight(date:LocalDate,dayInfo:QseiDay):CurrentQseiGroup
    {
        let year = Qsei.getYear(date);
        let month = Qsei.getMonth(date);
        return new CurrentQseiGroup(year,month,dayInfo,date);
    }
}