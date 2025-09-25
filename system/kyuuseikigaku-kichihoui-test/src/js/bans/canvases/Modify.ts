import * as d3 from 'd3';
import IRect from '../../2d/IRect';

export default class Modify
{
    public static readonly RIGHT = 1;    
    public static readonly LEFT = 2;
    public static readonly CENTER = 0;
    public static readonly TOP = -1;
    public static readonly BOTTTOM = -2;
    

    public static modify(node:d3.Selection<any,any,any,any>,x:number,y:number)
    {
        let val:IRect = node.node().getBoundingClientRect();
        let addX = 0;
        let addY = 0;
        if(x == Modify.LEFT)        
        {
            addX = 0;
        }
        else if(x == Modify.RIGHT)
        {
            addX =-val.width;    
        }
        else
        {
            addX = -val.width / 2.0;
        }

        if(y == Modify.TOP)        
        {
            addY = 0;//val.height;    
        }
        else if(y == Modify.BOTTTOM)
        {
            addY = 0;
        }
        else
        {
            addY = -0.5 * val.height;
        }

        node.selectAll("*")
            .attr("x",function(){
                let val2 = d3.select(this);
                return Number(val2.attr("x")) + addX;                              
            })
            .attr("y",function(){
                let val2 = d3.select(this);
                return Number(val2.attr("y")) + addY;                              
            })

    }
}
