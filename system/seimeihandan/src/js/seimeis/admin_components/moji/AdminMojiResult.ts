
export default interface AdminMojiResult
{
    kakusu:number;    
    moji:string;        
    kana:string;
    type:string;
    isOld:boolean;
    oldmoji:string;
    isBunri:boolean;
    ngwords:Array<Ngword>;
    oldOverride:boolean;
}
