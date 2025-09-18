import { Component, Vue, Watch } from 'vue-property-decorator';
import { EVENT_HUB } from '../../units/EventHub';
import StorageUtils from '../../../utils/StorageUtils';
import HtmlUtils from '../../../utils/HtmlUtils';
import AdminMojiResult from './AdminMojiResult';



interface InfoJson {
    kakusu: string;
    moji: string;
    kana: string;
    is_old:string;
    type:string;
    isbunri:string;
    ngwords: Array<Ngword>;
    oldmoji: string;
    oldoverride:string;
}

const ADMIN_SEARCH_MOJI = "seimei_search_moji";

@Component(
    {
        template: require('./htmls/AdminMojiJoukenComponent.html'),
    })
export default class AdminMojiJoukenComponent extends Vue {
    public moji = "";
    public error = "";
    public code = "";


    public created() {
        let paramList = HtmlUtils.paramList();    
        if(paramList.has('moji'))
        {
            let moji =  paramList.get('moji');   
            this.moji = decodeURI(moji);
        }
        else
        {
            this.moji = StorageUtils.getStringDefault(ADMIN_SEARCH_MOJI, "梅");
        }
    }


    @Watch('moji')
    public onchangeMoji() {
        if(1 < this.moji.length)
        {
            this.moji = [...this.moji][0];
        }

        if(this.moji == " " || this.moji == "　")
        {
            this.moji = "";    
        }

        if (this.moji == "") {
            this.code = "";
            EVENT_HUB.$emit('clear_info');
            return;
        }
        
     
        this.code = HtmlUtils.toHex(this.moji);              

        
        let url = `https://kigaku-navi.com/qsei/api/select_moji.php?moji=${this.moji}`;
        console.log(url);
        $.ajax(url,
            {
                type: 'get',
                dataType: 'json',
                crossDomain: true
            }).done((json: InfoJson) => {
                StorageUtils.setString(ADMIN_SEARCH_MOJI, this.moji);
                let path = `${location.pathname}?moji=${this.moji}`
                history.replaceState('', '', path)

                let submit:AdminMojiResult = {
                    kakusu: Number(json.kakusu),
                    moji: this.moji,
                    kana: json.kana,
                    type:json.type,
                    isOld:json.is_old == "1",
                    ngwords: json.ngwords,
                    oldmoji: json.oldmoji,
                    isBunri:json.isbunri == "1",
                    oldOverride:json.oldoverride == "1"
                };

                EVENT_HUB.$emit('admin_info', submit);            
        }).fail((response) => {
            alert("取得に失敗しました。" + response.responseText);
        });
    }
}    