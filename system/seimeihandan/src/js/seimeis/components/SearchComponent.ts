import { Component, Vue } from 'vue-property-decorator';
import HtmlUtils from '../../utils/HtmlUtils';

import { EVENT_HUB } from '../units/EventHub';
import Chara from '../units/Chara';
import Seimei from '../units/Seimei';
import Ngwords from './Ngwords';



interface JsonMoji {
    code: string;
    kakusu: string;
    kana: string;
    isbunri:string;
}

interface JsonMojis {
    name: string;
    new: JsonMoji;
    old: JsonMoji;
}

interface JsonResult
{
    sei:Array<JsonMojis>
    mei:Array<JsonMojis>
    ng:Array<Ngwords>;
    last_date:string;    
}


@Component(
{
    template: require('./htmls/SearchComponent.html')
})
export default class SearchComponent extends Vue
 {
    protected sei = "";
    protected mei = "";
    protected error = "";
    
    public created()
    {
        let map = HtmlUtils.paramList();
        let sei = map.get('sei');
        let mei = map.get('mei');

        if(sei != null && mei != null)
        {
            this.sei =  decodeURI(sei);
            this.mei =  decodeURI(mei);    
            this.kakusu(this.sei,this.mei);
        }
    }    



    private kakusu(sei: string, mei: string) {
        let url = `https://kigaku-navi.com/qsei/api/select_seimei.php?sei=${sei}&mei=${mei}`;
        console.log(url);
        $.ajax(url,
            {
                type: 'get',
                dataType: 'json',
                crossDomain: true
            }).done((json:JsonResult) => {
                let meis = json["mei"];
                let seis = json["sei"];
                this.send(seis, meis,json.ng,json.last_date);
            }).fail((errorText)=>{
                alert("検索に失敗しました。" + errorText.responseText);
            });
    }


    private toInputData(newJson:JsonMoji,oldJson:JsonMoji):JsonMoji
    {
        let val = newJson;
        //基本は旧字体優先
        if (oldJson != null) {
            val = oldJson
        }

        return val;
    }

    public send(jsonSeis: Array<JsonMojis>, jsonMeis: Array<JsonMojis>,ng:Array<Ngwords>,lastDate:string)    
    {
        try
        {
            let charaSeis = new Array<Chara>();
            jsonSeis.forEach((sei) => {
                let val = this.toInputData(sei.new,sei.old);

                if(val === null)
                {
                    throw new Error(`「${sei.name}」判定できない文字です。申し訳ございませんが、このサイトでは鑑定を行えません。`);
                }

                charaSeis.push(Chara.of(sei.name, Number(val.kakusu), val.kana,val.isbunri == "1"));                
            });

    
            let charaMeis = new Array<Chara>();
            jsonMeis.forEach((mei) => {
                let val = this.toInputData(mei.new,mei.old);

                if(val === null)
                {
                    throw new Error(`「${mei.name}」判定できない文字です。申し訳ございませんが、このサイトでは鑑定を行えません。`);
                }
                charaMeis.push(Chara.of(mei.name, Number(val.kakusu), val.kana,val.isbunri == "1"));
            });

                    
            EVENT_HUB.$emit('kantei',new Seimei(charaSeis,charaMeis,ng));
        

            this.error = "";
        }
        catch(errorText)
        {
            this.error = errorText.message;
            EVENT_HUB.$emit('clear_kantei');
        }
    }


    
    public submitKantei()
    {
        let path = `${location.pathname}?sei=${this.sei}&mei=${this.mei}`;
        history.replaceState('', '', path)

        this.kakusu(this.sei,this.mei);
    }
}






