import { Component, Vue } from 'vue-property-decorator';
import YouinKantei from "../kantei/youins/YouinKantei";

@Component(
    {
        template: require('./htmls/TestYouinComponent.html')
    })
export default class TestYouinComponent extends Vue
{
    protected youins = new Array<string>();


    public addTest(seis:Array<boolean>,meis:Array<boolean>)
    {
        let result = YouinKantei.ofNormalize("",seis,meis,false);

        let text = "";
        seis.forEach((val)=>{
            if(val == true)    
            {
                text += "○";
            }
            else
            {
                text += "●";
            }
        });

        text += "ー";
        meis.forEach((val)=>{
            if(val == true)    
            {
                text += "○";
            }
            else
            {
                text += "●";
            }
        });

        text += `  ====> ${result.kantei.jp}`;  
        
        this.youins.push(text);
    }    
    public created()
    {
        this.addTest([true,true],[false,true,true] );
        this.addTest([true,true],[false,false,true] );
        this.addTest([true,true],[false,false,false] );
        this.addTest([true,true],[false,true,false] );
        this.addTest([true,true],[true,true,true] );
        this.addTest([true,true],[true,false,true] );
        this.addTest([true,true],[true,false,false] );
        this.addTest([true,true],[true,true,false] );
        this.addTest([],[] );
        this.addTest([true,false],[true,true,true] );
        this.addTest([true,false],[true,false,true] );
        this.addTest([true,false],[true,false,false] );
        this.addTest([true,false],[true,true,false] );
        this.addTest([true,false],[false,true,true] );
        this.addTest([true,false],[false,false,true] );
        this.addTest([true,false],[false,false,false] );
        this.addTest([true,false],[false,true,false] );
        this.addTest([],[] );
        this.addTest([true,true,true],[true,true,true] );
        this.addTest([true,true,true],[true,false,true] );
        this.addTest([true,true,true],[true,false,false] );
        this.addTest([true,true,true],[true,true,false] );
        this.addTest([true,true,true],[false,true,true] );
        this.addTest([true,true,true],[false,false,true] );
        this.addTest([true,true,true],[false,false,false] );
        this.addTest([true,true,true],[false,true,false] );
        this.addTest([],[] );
       this.addTest([true,false,true],[true,true,true] );
       this.addTest([true,false,true],[true,false,true] );
       this.addTest([true,false,true],[true,false,false] );
       this.addTest([true,false,true],[true,true,false] );
       this.addTest([true,false,true],[false,true,true] );
       this.addTest([true,false,true],[false,false,true] );
       this.addTest([true,false,true],[false,false,false] );
       this.addTest([true,false,true],[false,true,false] );
       this.addTest([],[] );
       this.addTest([true,true,false],[true,true,true] );
       this.addTest([true,true,false],[true,false,true] );
       this.addTest([true,true,false],[true,false,false] );
       this.addTest([true,true,false],[true,true,false] );
       this.addTest([true,true,false],[false,true,true] );
       this.addTest([true,true,false],[false,false,true] );
      this.addTest([true,true,false],[false,false,false] );
      this.addTest([true,true,false],[false,true,false] );
      this.addTest([],[] );
       this.addTest([true,false,false],[true,true,true] );
       this.addTest([true,false,false],[true,false,true] );
       this.addTest([true,false,false],[true,false,false] );
       this.addTest([true,false,false],[true,true,false] );
       this.addTest([true,false,false],[false,true,true] );
       this.addTest([true,false,false],[false,false,true] );
       this.addTest([true,false,false],[false,false,false] );
       this.addTest([true,false,false],[false,true,false] );
       this.addTest([],[] );
       this.addTest([true,true,true],[true,true] );
       this.addTest([true,true,true],[true,false] );
       this.addTest([true,true,true],[false,true] );
       this.addTest([true,true,true],[false,false] );
       this.addTest([true,false,true],[true,true] );
       this.addTest([true,false,true],[true,false] );
       this.addTest([true,false,true],[false,true] );
       this.addTest([true,false,true],[false,false] );
        this.addTest([],[] );
        this.addTest([true,true,false],[true,true] );
        this.addTest([true,true,false],[true,false] );
        this.addTest([true,true,false],[false,true] );
        this.addTest([true,true,false],[false,false] );
        this.addTest([true,false,false],[true,true] );
        this.addTest([true,false,false],[true,false] );
        this.addTest([true,false,false],[false,true] );
        this.addTest([true,false,false],[false,false] );
        this.addTest([],[] );
        this.addTest([true,true],[false,true] );
        this.addTest([true,true],[false,false] );
        this.addTest([true,true],[true,true] );
        this.addTest([true,true],[true,false] );
        this.addTest([true,false],[true,true] );
        this.addTest([true,false],[true,false] );
        this.addTest([true,false],[false,true] );
        this.addTest([true,false],[false,false] );





        /*
        //陰のテスト
        this.addTest([false],[false] );
        this.addTest([false],[true] );   


        //1-1
        this.addTest([true],[true] );
        this.addTest([true],[false] );

        //1-2        
        this.addTest([true],[true,true] );
        this.addTest([true],[true,false] );
        this.addTest([true],[false,true] );
        
        //2-1        
        this.addTest([true,true],[true] );
        this.addTest([true,true],[false] );
        this.addTest([true,false],[true] );
        this.addTest([true,false],[false] );

        //2-2        
        this.addTest([true,true],[true,true] );
        this.addTest([true,true],[true,false] );
        this.addTest([true,true],[false,true] );
        this.addTest([true,true],[false,false] );
        this.addTest([true,false],[true,true] );
        this.addTest([true,false],[true,false] );
        this.addTest([true,false],[false,true] );
        this.addTest([true,false],[false,false] );

        //2-3
        this.addTest([true,true],[true,true,true] );
        this.addTest([true,true],[true,true,false] );
        this.addTest([true,true],[true,false,true] );
        this.addTest([true,true],[false,true,true] );
        this.addTest([true,true],[true,false,false] );
        this.addTest([true,true],[false,true,false] );
        this.addTest([true,true],[false,false,true] );
        this.addTest([true,true],[false,false,false] );
        this.addTest([true,false],[true,true,true] );
        this.addTest([true,false],[true,true,false] );
        this.addTest([true,false],[true,false,true] );        
        this.addTest([true,false],[false,true,true] );        
        this.addTest([true,false],[true,false,false] );        
        this.addTest([true,false],[false,true,false] );        
        this.addTest([true,false],[false,false,true] );        
        this.addTest([true,false],[false,false,false] );        
        */
    }



    
}


