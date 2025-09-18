import { Component, Vue, Ref} from 'vue-property-decorator';
import { EVENT_HUB } from '../../units/EventHub';
import AdminMojiResult from './AdminMojiResult';
import AdminMojiOldMapComponent from './AdminMojiOldMapComponent';
import AdminNgWordComponent from '../word/AdminNgWordComponent';
import AdminMojiBasicComponent from './AdminMojiBasicComponent';




interface MojiOption {
    moji: string;
    kakusu?: number;
    kana?: string;
    type?: string;
    oldmoji?: string;
    oldoverride?: boolean;
    isBunri?: boolean;
    ngwords?:string;
}


@Component(
    {
        template: require('./htmls/AdminMojiResultComponent.html'),
        components:{
            AdminMojiBasicComponent:AdminMojiBasicComponent,
            AdminMojiOldMapComponent: AdminMojiOldMapComponent,
            AdminNgWordComponent:AdminNgWordComponent,
        }
    })
export default class AdminMojiResultComponent extends Vue {
    protected info:AdminMojiResult = null;
    protected view = false;



    @Ref()
    adminNgWordComponent:AdminNgWordComponent;


    public created() {
        EVENT_HUB.$on('admin_info', (info: AdminMojiResult) => {
            this.view = true;
            this.info = info;  
        });

        EVENT_HUB.$on('clear_info', () => {
            this.view = false;
        });
    }

    public registButton()
    {
        AdminMojiResultComponent.submit({
            moji:this.info.moji,    
            kakusu:this.info.kakusu,    
            kana:this.info.kana,    
            type:this.info.type,    
            oldmoji:this.info.oldmoji,   
            oldoverride:this.info.oldOverride,   
            isBunri:this.info.isBunri,
            ngwords:this.adminNgWordComponent.getNgwordsJson()
        });
    }

    public deleteButton()
    {
        if (window.confirm(`「${this.info.moji}」を削除してもよろしいでしょうか？`) == false) {
            return;
        }


        let url = `https://kigaku-navi.com/qsei/api/delete_word.php?word=${this.info.moji}`;
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




    public static submit(option: MojiOption) {
        if (option.kana != undefined) {
            if(option.kana == "")
            {
                alert("必ず一文字以上の読みを入力してください");
                return;
            }
            let match = option.kana.match('^[ァ-ヴ]+$');
            if (match == null) {
                alert("文字の読みはカタカナのみで入力してください");
                return;
            }
        }

        let data:{[key:string]:string} = {};
        data['moji'] = option.moji;
        if(option.isBunri != undefined)        
        {
            data["isbunri"] = String(option.isBunri);
        }

        if(option.kakusu != undefined)        
        {
            data["kakusu"] = String(option.kakusu);
        }

        if(option.kana != undefined)        
        {
            data["kana"] = option.kana;    
        }

        if(option.oldmoji != undefined)        
        {
            data["oldmoji"] = option.oldmoji;
        }
        
        if(option.oldoverride != undefined)        
        {
            data["oldoverride"] = String(option.oldoverride);
        }        

        if(option.type != undefined)        
        {
            data["type"] = option.type;
        }        

        if(option.ngwords != undefined)        
        {
            data['ngwords'] = option.ngwords;
        }    
        
        console.log(data);
        let url = `https://kigaku-navi.com/qsei/api/modify_moji.php`;
        console.log(url);
        $.ajax(url,
            {
                type: 'post',
                dataType: 'json',
                data: data,
                crossDomain: true
            }
        ).done(() => {
            alert("登録に成功しました");
        }).fail((errorText) => {
            alert("登録に失敗しました。" + errorText.responseText);
        });
    }
}

