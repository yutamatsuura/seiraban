import { Component, Vue} from 'vue-property-decorator';

interface OldMapJson
{
    lost_count:string;
    moji:string;
}

interface OldMap
{
    lost_count:number;
    moji:string;
}



@Component(
{
    template: require('./htmls/AdminLostListComponent.html'),
})
export default class AdminLostListComponent extends Vue {
    protected items = new Array<OldMap>();

    public created()
    {
        
        let url = "https://kigaku-navi.com/qsei/api/select_lost.php";
        console.log(url);
        $.ajax(url,
            {
                type: 'get',
                dataType: 'json',
                crossDomain: true
            }).done((results: Array<OldMapJson>) => {
                this.items = new Array<OldMap>();
                results.forEach((map)=>{
                    this.items.push({
                        lost_count:Number(map.lost_count),
                        moji:map.moji                    
                    });
                });
            }).fail((error) => {
                alert("取得に失敗しました。" + error.responseText);
            });
    }

    
    public getNewLink(item:OldMap)
    {
        return `/qsei/admin/seimei_moji.php?moji=${item.moji}`;
    }
  
 

}    


    