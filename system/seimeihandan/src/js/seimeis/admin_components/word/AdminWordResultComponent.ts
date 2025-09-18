import { Component, Vue, Ref} from 'vue-property-decorator';
import { EVENT_HUB } from '../../units/EventHub';
import AdminNgWordComponent from './AdminNgWordComponent';
import AdminWordResult from './AdminWordResult';



@Component(
    {
        template: require('./htmls/AdminWordResultComponent.html'),
        components:{
            AdminNgWordComponent:AdminNgWordComponent
        }
    })
export default class AdminWordResultComponent extends Vue {
    protected info:AdminWordResult = null;
    protected view = false;

    @Ref()
    adminNgWordComponent:AdminNgWordComponent;

    public created() {
        EVENT_HUB.$on('admin_info', (info: AdminWordResult) => {
            this.view = true;
            this.info = info;          
        });

        EVENT_HUB.$on('clear_info', () => {
            this.view = false;
        });
    }

    public destroyed()
    {
        EVENT_HUB.$off('admin_info');
        EVENT_HUB.$off('clear_info');
    }

  
    public registButton()
    {                     
        let ngText = this.adminNgWordComponent.getNgwordsJson();
        let url = `https://kigaku-navi.com/qsei/api/modify_word.php`;
        console.log(url);
        $.ajax(url,
            {
                type: 'post',
                dataType: 'json',
                crossDomain: true,
                data: {
                    word: this.info.word,
                    reasons: ngText
                },

            }
        ).done(() => {
            alert("登録に成功しました");
        }).fail((error) => {
            alert("登録に失敗しました。メッセージ=" + error.responseText);
        });        
    }

    public deleteButton() {
        if (window.confirm(`「${this.info.word}」を削除してもよろしいでしょうか？`) == false) {
            return;
        }

        let url = `https://kigaku-navi.com/qsei/api/delete_word.php?word=${this.info.word}`;
        console.log(url);
        $.ajax(url,
            {
                type: 'get',
                dataType: 'json',
                crossDomain: true
            }).done(() => {
                alert('削除に成功しました'); 
                location.reload();               
            }).fail((response) => {
                alert("削除に失敗しました。" + response.responseText);
            });
    }
}

