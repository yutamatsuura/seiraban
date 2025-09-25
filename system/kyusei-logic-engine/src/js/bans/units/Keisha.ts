




export default class Keisha
{
    private static readonly VALUES = [
        null,
        [null,6,4,3,2,1,9,8,7,6],//1
        [null,6,1,4,3,2,1,9,8,7],//2
        [null,7,6,4,4,3,2,1,9,8],//3
        [null,8,7,6,6,4,3,2,1,9],//4
        [null,9,8,7,6,-1,4,3,2,1],//5
        [null,1,9,8,7,6,9,4,3,2],//6
        [null,2,1,9,8,7,6,4,4,3],//7
        [null,3,2,1,9,8,7,6,6,4],//8
        [null,4,3,2,1,9,8,7,6,4],//9     
    ]

    public static of(year:number,month:number,man:boolean):number
    {
        let val = Keisha.VALUES[year][month];
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