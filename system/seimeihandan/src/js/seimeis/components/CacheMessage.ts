import StorageUtils from "../../utils/StorageUtils";
import KanteiResult from "../kantei/KanteiResult";
import LocalDateTime from "../../times/LocalDateTime";


const DATE_KEY = "seimei_cache_date";
const MESSAGE_KEY = "seimei_cache_message";


//バグが怖くなったのでキャッシュ機能はデフォルトで無効
export default class CacheMessage
{
    static getMssage():{[key:string]:KanteiResult}
    {
        let message = StorageUtils.getString(MESSAGE_KEY);
        if(message == null)
        {
            return {};    
        }
        else
        {
            return JSON.parse(message);            
        }
    }

    
    static getCacheDate():LocalDateTime
    {
        return StorageUtils.getDateTimeDefault(DATE_KEY,LocalDateTime.MIN);
    }

    static isCacheUse(date:LocalDateTime)
    {
        return date.getTime() <= this.getCacheDate().getTime();        
    }
    


    
}