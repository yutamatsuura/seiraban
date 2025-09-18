import { Component, Vue} from 'vue-property-decorator';
import { EVENT_HUB } from '../../units/EventHub';
import AdminSearchResult from './AdminSearchResult';
import Gogyou from '../../units/Gogyou';
import AdminMojiResultComponent from '../moji/AdminMojiResultComponent';
import AdminMojiBasicComponent from '../moji/AdminMojiBasicComponent';



@Component(
    {
        template: require('./htmls/AdminSearchResultComponent.html')
    })
export default class AdminSearchResultComponent extends Vue {
    protected items = new Array<AdminSearchResult>();
    protected view = false;
    protected types:{[key:string]:string} = AdminMojiBasicComponent.TYPES;  
    
    public created() {
        EVENT_HUB.$on('admin_info', (items: Array<AdminSearchResult>) => {
            this.items = items; 
        });

        EVENT_HUB.$on('clear_info', (items: Array<AdminSearchResult>) => {
            this.items = [];
        });        
    }

    public gogyou(item:AdminSearchResult)    
    {
        let gogyou =  Gogyou.ofKana(item.kana);
        if(gogyou == null)
        {
            return "";    
        }
        else
        {
            return gogyou.jp;    
        }
    }

    public getLink(item:AdminSearchResult):string
    {
        return `/qsei/admin/seimei_moji.php?moji=${item.moji}`;
    }


    public submitModify(item:AdminSearchResult)
    {
        AdminMojiResultComponent.submit({
            moji:item.moji,
            kakusu:item.kakusu,
            kana:item.kana,
            type:item.type,
            isBunri:item.isBunri
        });   
    }

    public getOldLink(item:AdminSearchResult):string
    {
        return `/qsei/admin/seimei_moji.php?moji=${item.oldmoji}`;        
    }
}