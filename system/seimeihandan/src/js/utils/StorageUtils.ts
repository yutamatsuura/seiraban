import LocalDateTime from "../times/LocalDateTime";


export default class StorageUtils {
    public static getNumber(key: string): number {
        let item = localStorage.getItem(key);
        if (item == null) {
            return null;
        }
        else {
            return Number(item);
        }
    }

    public static getDateTime(key:string):LocalDateTime{
        let item = localStorage.getItem(key);
        if (item == null) {
            return null;
        }
        else {
            return LocalDateTime.ofTime(Date.parse(item));
        }
    }

    public static getDateTimeDefault(key:string,init:LocalDateTime):LocalDateTime
    {
        let val = StorageUtils.getDateTime(key);
        if(val == null)
        {
            return init;    
        }
        else
        {
            return val;    
        }
    }

    
    public static setDateTime(key:string,dateTime:LocalDateTime){
        localStorage.setItem(key,dateTime.getDateString());
    }


    public static getBoolean(key: string): boolean {
        let item = localStorage.getItem(key);
        if (item == null) {
            return null;
        }
        else {
            return item === "true";
        }
    }

    public static getNumberDefault(key: string, def: number): number {
        let val = StorageUtils.getNumber(key);
        if (val == null) {
            return def;
        }
        else {
            return val;
        }
    }

    public static getBooleanDefault(key: string, def: boolean): boolean {
        let val = StorageUtils.getBoolean(key);
        if (val == null) {
            return def;
        }
        else {
            return val;
        }
    }



    public static setNumber(key: string, value: number) {
        localStorage.setItem(key, String(value));
    }

    public static setString(key: string, value: string) {
        localStorage.setItem(key,value);
    }

    public static setBoolean(key: string, value: boolean) {
        localStorage.setItem(key, String(value));
    }

    public static getString(key: string): string {
        return localStorage.getItem(key);
    }

    public static getStringDefault(key: string, init: string): string {
        let val = StorageUtils.getString(key);
        if (val == null) {
            return init;
        }
        else {
            return val;
        }
    }
}