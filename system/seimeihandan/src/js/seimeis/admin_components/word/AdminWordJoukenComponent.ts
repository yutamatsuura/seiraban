
import { Component, Vue, Watch } from 'vue-property-decorator';
import { EVENT_HUB } from '../../units/EventHub';
import StorageUtils from '../../../utils/StorageUtils';
import AdminWordResult from './AdminWordResult';


interface InfoJson {
    ngwords: Array<Ngword>;
}

const ADMIN_SEARCH_WORD = "seimei_search_word";

@Component(
    {
        template: require('./htmls/AdminWordJoukenComponent.html'),
    })
export default class AdminWordJoukenComponent extends Vue {
    public word = "";
    public error = "";


    public created() {
        this.word = StorageUtils.getStringDefault(ADMIN_SEARCH_WORD, "百合");
    }


    @Watch('word')
    public onchangeMoji() {
        if (this.word == "") {
            this.word = "";
            EVENT_HUB.$emit('clear_info');
            return;
        }
    
        
        let url = `https://kigaku-navi.com/qsei/api/select_word.php?word=${this.word}`;
        console.log(url);
        $.ajax(url,
            {
                type: 'get',
                dataType: 'json',
                crossDomain: true
            }).done((json: InfoJson) => {
                StorageUtils.setString(ADMIN_SEARCH_WORD, this.word);

                let submit:AdminWordResult = {                    
                    word: this.word,
                    ngwords: json.ngwords,
                };
                EVENT_HUB.$emit('admin_info', submit);            
        }).fail((response) => {
            alert("取得に失敗しました。" + response.responseText);
        });
    }
}    