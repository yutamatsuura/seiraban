import CanvasOption from "./canvases/CanvasOption";
import StorageUtils from "./units/StorageUtils";
import LocalDate from "../times/LocalDate";

interface IDefaultKipou
{
    level:number;    
    enable?:boolean;    
}


export default class Config {
    public static readonly SEX = "kiban_sex";
    public static readonly YEAR = "kiban_year";
    public static readonly MONTH = "kiban_month";
    public static readonly DAY = "kiban_day";
    public static readonly NANBOKU = "_kiban_nanboku_check";
    public static readonly TORIKESHI = "_kiban_torikeshi_check";

    //吉方    
    public static readonly SAIDAI = "_kiban_saidai";
    public static readonly DAIKI = "_kiban_daiki";
    public static readonly DOUKAI = "_kiban_doukai";
    public static readonly RINJU_KITI = "_kiban_rinjukiti";
    public static readonly TENDO = "_kiban_tendo";
    public static readonly DAISAN = "_kiban_daisan";
    public static readonly TAISAI = "_kiban_taisai";
    public static readonly GEKKEN = "_kiban_gekken";
    public static readonly NISSIN = "_kiban_nissin";

    //凶報
    public static readonly GOOU = "_kiban_goou";
    public static readonly ANKEN = "_kiban_anken";
    public static readonly HONMEI = "_kiban_honmei";
    public static readonly GETUMEI = "_kiban_getumei";
    public static readonly SAIHA = "_kiban_saiha";
    public static readonly GEPPA = "_kiban_geppa";
    public static readonly NIPPA = "_kiban_nippa";
    public static readonly HONMEI_TEKI = "_kiban_honmeiteki";
    public static readonly GETUMEI_TEKI = "_kiban_getumeiteki";
    public static readonly KOJI = "_kiban_koji_num";
    public static readonly RINJU_KYOU = "_kiban_koji";
    public static readonly TEII_TEKI = "_kiban_teii";

    //吉方よりも凶を優先するため、色塗りLevelの値は異なる。    
    public static readonly LEVEL_KYOU_STRONG = 100;    
    public static readonly LEVEL_KYOU_WEAK = 50;
    public static readonly LEVEL_KYOU_NONE = 0;
    public static readonly LEVEL_KIPOU_STRONG = 10;
    public static readonly LEVEL_KIPOU_WEAK = 5;
    public static readonly LEVEL_KIPOU_NONE = 0;

    public static readonly CLASS_MAP = new Map<number,string>(
        [
            [Config.LEVEL_KYOU_STRONG,"kyou_strong"],
            [Config.LEVEL_KYOU_WEAK,"kyou_weak"],
            [Config.LEVEL_KIPOU_STRONG,"kipou_strong"],
            [Config.LEVEL_KIPOU_WEAK,"kipou_weak"],
            [Config.LEVEL_KIPOU_NONE,"normal"],
        ]
    );        


    public static readonly DEFAULT_KIPOU_MAP = new Map<string, IDefaultKipou>(
        [
            //吉
            [Config.SAIDAI,{level:Config.LEVEL_KIPOU_STRONG}],
            [Config.DAIKI, {level:Config.LEVEL_KIPOU_STRONG}],
            [Config.DOUKAI, {level:Config.LEVEL_KIPOU_STRONG,enable:false}],            
            [Config.RINJU_KITI, {level:Config.LEVEL_KIPOU_STRONG,enable:false}],
            [Config.TENDO, {level:Config.LEVEL_KIPOU_NONE}],
            [Config.DAISAN, {level:Config.LEVEL_KIPOU_NONE}],
            [Config.TAISAI, {level:Config.LEVEL_KIPOU_NONE,enable:false}],
            [Config.GEKKEN, {level:Config.LEVEL_KIPOU_NONE,enable:false}],
            [Config.NISSIN, {level:Config.LEVEL_KIPOU_NONE,enable:false}],

            //凶        
            [Config.GOOU, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.ANKEN, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.HONMEI, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.GETUMEI, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.SAIHA, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.GEPPA, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.NIPPA, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.HONMEI_TEKI, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.GETUMEI_TEKI, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.KOJI, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.RINJU_KYOU, {level:Config.LEVEL_KYOU_STRONG,enable:false}],
            [Config.KOJI, {level:Config.LEVEL_KYOU_STRONG}],
            [Config.TEII_TEKI, {level:Config.LEVEL_KYOU_NONE}],
        ]);



 
    public static getKipouLeves(): Map<string, number> {
        let result = new Map<string, number>();
        Config.DEFAULT_KIPOU_MAP.forEach((value, key) => {
            result.set(key, StorageUtils.getNumberDefault(key, value.level));
        });

        return result;
    }

    public static getKipouEnables(): Map<string, boolean> {
        let result = new Map<string, boolean>();
        Config.DEFAULT_KIPOU_MAP.forEach((value, key) => {
            let enabledId = Config.getEnableId(key);            
            let enabled = value.enable;
            if(enabled === undefined)
            {
                enabled = true;
            }
            result.set(enabledId, StorageUtils.getBooleanDefault(enabledId,enabled));
        });

        return result;
    }

    public static getEnableId(key:string):string
    {
        return key + "_enable";    
    }    

    public static getCanvasOption(): CanvasOption {
        return {
            nanbokuRev: StorageUtils.getBooleanDefault(Config.NANBOKU, false),
            viewTorikeshi: StorageUtils.getBooleanDefault(Config.TORIKESHI, false),
            kipouLevels:Config.getKipouLeves(),
            kipouEnables:Config.getKipouEnables()
        };
    }

    public static getBirthDate():LocalDate
    {
        return LocalDate.of(
            StorageUtils.getNumberDefault(Config.YEAR,2000),
            StorageUtils.getNumberDefault(Config.MONTH,1),
            StorageUtils.getNumberDefault(Config.DAY,1)
        );        
    }

    public static getMan():boolean
    {
        return StorageUtils.getStringDefault(Config.SEX,"男") == "男";
    }
}