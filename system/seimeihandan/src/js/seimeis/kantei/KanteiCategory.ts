import Kantei from "./Kantei";


export default class KanteiCategory
{
    private _eng:string;
    private _jp:string;
    private _subs:ReadonlyArray<Kantei>;

    get eng()
    {
        return this._eng;    
    }

    get jp()
    {
        return this._jp;    
    }    

    get subs()
    {
        return this._subs;    
    }

    constructor(eng:string,jp:string,subs:Array<Kantei>)    
    {
        this._eng = eng;
        this._jp = jp;
        this._subs = subs;
    }

    public toKeyFromEngjp(sub: Kantei): string {
        return KanteiCategory.toKeyFromString(this.eng, sub.eng);
    }

    public static toKeyFromString(first: string, sub: string): string     {
        return `${first}-${sub}`;
    }

    public static readonly GOGYOU = new KanteiCategory(
        'gogyou',
        '五行',
        [
            Kantei.GOGYOU_BALANCE_OK,        
            Kantei.GOGYOU_BALANCE_NG,        
        ]
    );

    public static readonly GOGYOU_KA = new KanteiCategory(
        'gogyou-ka',
        '五行-火',
        [
            Kantei.GOGYOU_KA_KA,
            Kantei.GOGYOU_KA_SUI,
            Kantei.GOGYOU_KA_MOKU,
            Kantei.GOGYOU_KA_DO,
            Kantei.GOGYOU_KA_KIN,
        ]
    );

    public static readonly GOGYOU_SUI = new KanteiCategory(
        'gogyou-sui',
        '五行-水',
        [
            Kantei.GOGYOU_SUI_KA,
            Kantei.GOGYOU_SUI_SUI,
            Kantei.GOGYOU_SUI_MOKU,
            Kantei.GOGYOU_SUI_DO,
            Kantei.GOGYOU_SUI_KIN,
        ]
    );

    public static readonly GOGYOU_MOKU = new KanteiCategory(
        'gogyou-moku',
        '五行-木',
        [
            Kantei.GOGYOU_MOKU_KA,
            Kantei.GOGYOU_MOKU_SUI,
            Kantei.GOGYOU_MOKU_MOKU,
            Kantei.GOGYOU_MOKU_DO,
            Kantei.GOGYOU_MOKU_KIN,
        ]
    );

    public static readonly GOGYOU_DO = new KanteiCategory(
        'gogyou-do',
        '五行-土',
        [
            Kantei.GOGYOU_DO_KA,
            Kantei.GOGYOU_DO_SUI,
            Kantei.GOGYOU_DO_MOKU,
            Kantei.GOGYOU_DO_DO,
            Kantei.GOGYOU_DO_KIN,
        ]
    );

    
    public static readonly GOGYOU_KIN = new KanteiCategory(
        'gogyou-kin',
        '五行-金',
        [
            Kantei.GOGYOU_KIN_KA,
            Kantei.GOGYOU_KIN_SUI,
            Kantei.GOGYOU_KIN_MOKU,
            Kantei.GOGYOU_KIN_DO,
            Kantei.GOGYOU_KIN_KIN,
        ]
    );


    public static readonly INYOU = new KanteiCategory(
        'inyou',
        '陰陽',
        [
            Kantei.INYOU_CHUDAN,    
            Kantei.INYOU_INYOU,
            Kantei.INYOU_SIRO_KATAYORI,
            Kantei.INYOU_KURO_KATAYORI,
            Kantei.INYOU_NIJU_BASAMI,
            Kantei.INYOU_OHBASAMI,
            Kantei.INYOU_SHIBARI,
            Kantei.INYOU_UE_MAKINAOSI,
            Kantei.INYOU_SITA_MAKINAOSI,
    ]);
    
    public static readonly TENTI = new KanteiCategory(
        'tenti',
        '天地',
        [
            Kantei.TENTI_DOUSU_GUSU,
            Kantei.TENTI_DOUSU_KISUU,
            Kantei.TENTI_SHOUTOTU,
            Kantei.SEIMEI_DOUSU
    ]);

    public static readonly YOMIKUDASI = new KanteiCategory(
        'yomikudasi', 
        '読み下し',
        [
            Kantei.KUDASI_ANIMAL,
            Kantei.KUDASI_FISH,
            Kantei.KUDASI_JIKAN,
            Kantei.KUDASI_KIKOU,
            Kantei.KUDASI_PLANT,
            Kantei.KUDASI_ROCK,
            Kantei.KUDASI_TENYOU,

            Kantei.KUDASI_HINKAKU,            
            Kantei.KUDASI_KEIBETU,
            Kantei.KUDASI_NO_SEX,
            Kantei.KUDASI_ETC,

            Kantei.KUDASI_ONE_CHARA,            
            Kantei.KUDASI_SUI,
            Kantei.KUDASI_HAPPY,
            Kantei.KUDASI_BUNRI,
            Kantei.KUDASI_SONKI,
            Kantei.KUDASI_JINKAKU9,
            Kantei.KUDASI_TIGYOU9,
            Kantei.KUDASI_TIKAKU9,

        ]
    ); 


    public static readonly SCORE = new KanteiCategory(
        'score', 
        '点数',
        [
            Kantei.SCORE_FULL,
            Kantei.SCORE_OK,
            Kantei.SCORE_NG,
            Kantei.SCORE_KYOU_OR_KIPOU,
            Kantei.SCORE_MAX,
            Kantei.SCORE_MIN,
            Kantei.SCORE_BEGIN,
        ]
    );

    public static readonly KAKUSU0 = new KanteiCategory(
        'kakusu0', 
        '画数1～9',
        Kantei.rangeKakusu(1,9)
    );

    public static readonly KAKUSU1 = new KanteiCategory(
        'kakusu1', 
        '画数10～19',
        Kantei.rangeKakusu(10,19)
    );
    
    public static readonly KAKUSU2 = new KanteiCategory(
        'kakusu2', 
        '画数20～29',
        Kantei.rangeKakusu(20,29)
    );

    public static readonly KAKUSU3 = new KanteiCategory(
        'kakusu3', 
        '画数30～39',
        Kantei.rangeKakusu(30,39)
    );

    public static readonly KAKUSU4 = new KanteiCategory(
        'kakusu4', 
        '画数40～49',
        Kantei.rangeKakusu(40,49)
    );

    
    public static readonly KAKUSU5 = new KanteiCategory(
        'kakusu5', 
        '画数50～59',
        Kantei.rangeKakusu(50,59)
    );

        
    public static readonly KAKUSU6 = new KanteiCategory(
        'kakusu6', 
        '画数60～69',
        Kantei.rangeKakusu(60,69)
    );

           
    public static readonly KAKUSU7 = new KanteiCategory(
        'kakusu7', 
        '画数70～81',
        Kantei.rangeKakusu(70,81)
    );




    public static readonly ITEMS = [
        KanteiCategory.GOGYOU,    
        KanteiCategory.GOGYOU_KA,    
        KanteiCategory.GOGYOU_SUI,    
        KanteiCategory.GOGYOU_MOKU,    
        KanteiCategory.GOGYOU_DO,    
        KanteiCategory.GOGYOU_KIN,    
        KanteiCategory.INYOU,
        KanteiCategory.TENTI,
        KanteiCategory.YOMIKUDASI,
        KanteiCategory.SCORE,
        KanteiCategory.KAKUSU0,
        KanteiCategory.KAKUSU1,
        KanteiCategory.KAKUSU2,
        KanteiCategory.KAKUSU3,
        KanteiCategory.KAKUSU4,
        KanteiCategory.KAKUSU5,
        KanteiCategory.KAKUSU6,
        KanteiCategory.KAKUSU7,
    ];


    public static static_constructor()
    {
        KanteiCategory.ITEMS.forEach((category)=>{
            category.subs.forEach((sub)=>{
                Kantei.addItem(sub);                
            });            
        });        
    }
}

KanteiCategory.static_constructor();