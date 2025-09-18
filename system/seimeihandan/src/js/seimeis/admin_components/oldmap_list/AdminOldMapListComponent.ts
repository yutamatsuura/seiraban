import { Component, Vue, Watch} from 'vue-property-decorator';
import StorageUtils from '../../../utils/StorageUtils';
import AdminMojiResultComponent from '../moji/AdminMojiResultComponent';
import AdminMojiBasicComponent from '../moji/AdminMojiBasicComponent';

interface OldMapJson
{
    override:string;
    new_moji:string;
    new_kakusu:string;
    new_kana:string;
    new_type:string;
    isbunri:string;
    old_moji:string;
    old_kakusu:string;
    old_kana:string;   
    old_type:string;   
}

interface OldMap
{
    override:boolean;
    new_moji:string;
    new_kakusu:string;
    new_kana:string;
    new_type:string;
    isBunri:boolean;
    old_moji:string;
    old_kakusu:string;
    old_kana:string;
    old_type:string;   
}


const OLD_KEY = 'seimei_filter_oldkakusu';
const NEW_KEY = 'seimei_filter_newkakusu';

@Component(
{
    template: require('./htmls/AdminOldmapListComponent.html'),
})
export default class AdminOldMapListComponent extends Vue {
    protected all = new Array<OldMap>();
    protected items = new Array<OldMap>();
    protected newkakusu = "";
    protected oldkakusu = "";
    protected types =  AdminMojiBasicComponent.TYPES;

    public created()
    {
        this.newkakusu = StorageUtils.getStringDefault(NEW_KEY,"");
        this.oldkakusu = StorageUtils.getStringDefault(OLD_KEY,"");
        
        let url = "https://kigaku-navi.com/qsei/api/select_oldmap_list.php";
        console.log(url);
        $.ajax(url,
            {
                type: 'get',
                dataType: 'json',
                crossDomain: true
            }).done((results: Array<OldMapJson>) => {
                this.all = new Array<OldMap>();
                results.forEach((map)=>{
                    this.all.push({
                        override:map.override === "1" ? true : false,
                        new_moji:map.new_moji,
                        new_kakusu:map.new_kakusu,
                        new_kana:map.new_kana,
                        new_type:map.new_type,
                        isBunri:map.isbunri === "1" ? true : false,
                        old_moji:map.old_moji,
                        old_kakusu:map.old_kakusu,
                        old_kana:map.old_kana,
                        old_type:map.old_type,                        
                    });
                });

                this.filter();
            }).fail((error) => {
                alert("取得に失敗しました。" + error.responseText);
            });
    }

    
    @Watch('oldkakusu')
    @Watch('newkakusu')
    public filter()
    {
        this.items = this.all.filter((item)=>{
            return this.filterSub(item);                    
        });        

        StorageUtils.setString(OLD_KEY,this.oldkakusu);
        StorageUtils.setString(NEW_KEY,this.newkakusu);
    }

    private filterSub(item:OldMap):boolean
    {
        if(this.oldkakusu != "")    
        {
            if(item.old_kakusu !== this.oldkakusu)
            {
                return false;    
            }            
        }

        if(this.newkakusu != "")        
        {
            if(item.new_kakusu !== this.newkakusu)
            {
                return false;    
            }                    
        }
    
        return true;                
    }

    public modifyNew(item:OldMap)
    {
        AdminMojiResultComponent.submit({
            moji:item.new_moji,
            kakusu:parseInt(item.new_kakusu),
            kana:item.new_kana,
            type:item.new_type,
            oldmoji:item.old_moji,
            oldoverride:item.override,
            isBunri:item.isBunri
        });
    }

    public modifyOld(item:OldMap)
    {
        AdminMojiResultComponent.submit({
            moji:item.old_moji,
            kakusu:parseInt(item.old_kakusu),
            kana:item.old_kana,
            type:item.old_type
        });
    }

    public getOldLink(item:OldMap)
    {
        return `/qsei/admin/seimei_moji.php?moji=${item.old_moji}`;
    }

    
    public getNewLink(item:OldMap)
    {
        return `/qsei/admin/seimei_moji.php?moji=${item.new_moji}`;
    }
  
 

}    


    