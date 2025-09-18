
export default class ArrayUtils
{
    static compare<T>(a:Array<T>,b:Array<T>):boolean
    {
        for(let i = 0; i < a.length;i++)    
        {
            for(let j = 0; j < b.length;j++)    
            {
                if(a[i] === b[j])
                {
                    return true;    
                }
            }
        }

        return false;        
    }
}