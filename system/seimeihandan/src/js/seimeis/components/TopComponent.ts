import { Component, Vue} from 'vue-property-decorator';


@Component(
    {
        template: require('./htmls/SearchComponent.html')
    })
export default class TopComponent extends Vue
{
    public sei = "";
    public mei = "";
    public created()
    {        
        
    }

    public submitKantei()
    {
        if(this.mei == "" || this.sei == "")
        {
            alert("姓名を入力してください");
        }
        else
        {
            location.href=`/qsei/seimei_result.php?sei=${this.sei}&mei=${this.mei}`;
        }
    }
}