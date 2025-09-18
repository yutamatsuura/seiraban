
import { Component, Vue, Watch } from 'vue-property-decorator';
import AdminSearchResult from './AdminSearchResult';
import { EVENT_HUB } from '../../units/EventHub';
import StorageUtils from '../../../utils/StorageUtils';
import AdminMojiBasicComponent from '../moji/AdminMojiBasicComponent';


interface SearchResultJson {
    moji: string;
    kakusu: string;
    kana: string;
    type: string;
    gogyou:string;
    isbunri:string;
    oldmoji:string;
    old_kakusu:string;
    old_type:string;
}

const KAKUSU_KEY = "seimei_search_kakusu";
const GOGYOU_KEY = "seimei_search_gogyou";
const TYPE_KEY = "seimei_search_type";
const KANA_KEY = "seimei_search_kana";
const NEED_KANA_KEY = "seimei_search_need_kana";
const OLD_KAKUSU_KEY = "seimei_search_old_kana";



@Component(
    {
        template: require('./htmls/AdminSearchJoukenComponent.html'),
    })
export default class AdminSearchJoukenComponent extends Vue {
    public kakusu = "";
    public moji = "";
    public selectType = "all";
    public selectGogyou = "all";
    public types:{[key:string]:string} = {};
    public gogyous:{[key:string]:string} = {};
    public count = 0;
    public needKana = true;
    public kana = "";
    public oldKakusu = true;




    public created() {
        Object.assign(this.types , AdminMojiBasicComponent.TYPES);
        this.types["all"] = "全て";
        Object.assign(this.gogyous , AdminMojiBasicComponent.GOGYOUS);
        this.gogyous["all"] = "全て";

        this.kakusu = StorageUtils.getStringDefault(KAKUSU_KEY,"");        
        this.selectGogyou = StorageUtils.getStringDefault(GOGYOU_KEY,'all');
        this.selectType = StorageUtils.getStringDefault(TYPE_KEY,'all');
        this.kana = StorageUtils.getStringDefault(KANA_KEY,'');
        this.needKana = StorageUtils.getBooleanDefault(NEED_KANA_KEY,true);
        this.oldKakusu = StorageUtils.getBooleanDefault(OLD_KAKUSU_KEY,false);
        this.onchangeJouken();
    }


    private add(option:string,label:string,value:string):string
    {
        if(option == "")    
        {
            return label +"=" +value;
        }
        else
        {
            return "&"  + label +"=" +value;
        }
    }


    @Watch('kakusu')
    @Watch('selectType')
    @Watch('selectGogyou')
    @Watch('kana')
    @Watch('need_kana')
    @Watch('oldKakusu')
    public onchangeJouken() {
        StorageUtils.setString(KAKUSU_KEY,this.kakusu);
        StorageUtils.setString(GOGYOU_KEY,this.selectGogyou);
        StorageUtils.setString(TYPE_KEY,this.selectType);
        StorageUtils.setString(KANA_KEY,this.kana);
        StorageUtils.setBoolean(NEED_KANA_KEY,this.needKana);
        StorageUtils.setBoolean(OLD_KAKUSU_KEY,this.oldKakusu);
            

        let option = "";
        if(this.moji != "")
        {
            option += this.add(option,"moji",this.moji);                
        }

        if(this.kakusu != "")
        {
            option += this.add(option,"kakusu",this.kakusu);                
        }

        if(this.selectType != "all")
        {
            option += this.add(option,"type",this.selectType);                
        }

        if(this.selectGogyou != "all")
        {
            option += this.add(option,"gogyou",this.selectGogyou);                
        }

        if(this.needKana)
        {
            option += this.add(option,"need_kana","true");                            
        }

        if(this.kana)
        {
            option += this.add(option,"kana",this.kana);
        }        

        if(this.oldKakusu)
        {
            option += this.add(option,"old_kakusu","true");                            
        }
        

        let url = `https://kigaku-navi.com/qsei/api/search_moji.php?${option}`;        
        console.log(url);
        $.ajax(url,
            {
                type: 'get',
                dataType: 'json',
                crossDomain: true
            }).done((json: Array<SearchResultJson>) => {
                let data = new Array<AdminSearchResult>();
                json.forEach((result)=>{
                    data.push({
                        moji:result.moji,
                        kakusu:Number(result.kakusu),
                        kana:result.kana,
                        type:result.type,
                        oldmoji:result.oldmoji,
                        gogyou:result.gogyou,
                        oldType:result.old_type,
                        oldKakusu:Number(result.old_kakusu),
                        isBunri:result.isbunri == "1"
                    });
                });
                this.count = data.length;

                EVENT_HUB.$emit('admin_info', data); 
            }).fail((response) => {
                alert("取得に失敗しました。" + response.responseText);
            });
    }
}    