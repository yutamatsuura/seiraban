




export default class Doukai
{
    private static readonly VALUES = [
        null,
        [null,2,9,8,7,6,5,4,3,2],
        [null,3,7,1,9,8,7,6,5,4],
        [null,5,4,2,2,1,9,8,7,6],
        [null,7,6,5,5,3,2,1,9,8],
        [null,9,8,7,6,-1,4,3,2,1],
        [null,2,1,9,8,7,1,5,4,3],
        [null,4,3,2,1,9,8,6,6,5],
        [null,6,5,4,3,2,1,9,9,7],
        [null,8,7,6,5,4,3,2,1,8]        
    ];

    public static of(year:number,month:number,man:boolean):number
    {
        let val = Doukai.VALUES[year][month];
        if(val === -1)
        {
            if(man)    
            {
                return 3;
            }
            else
            {
                return 4;    
            }
        }
        else
        {
            return val;
        }    
    }
}