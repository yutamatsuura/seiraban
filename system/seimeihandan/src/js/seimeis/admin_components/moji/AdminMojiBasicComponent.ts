import { Component, Vue, Prop} from 'vue-property-decorator';
import AdminMojiResult from './AdminMojiResult';
import Gogyou from '../../units/Gogyou';



@Component(
{
    template: require('./htmls/AdminMojiBasicComponent.html'),
})
export default class AdminMojiBasicComponent extends Vue {
    @Prop
    ({
        default:null
    })    
    protected info:AdminMojiResult;

    public static TYPES = {
        kanji: "漢字",
        katakana: "カタカナ",
        hiragana: "ひらがな",
        eng: "英字、英数字",
        etc: "その他",
    };

    public static GOGYOUS = {
        moku: "木",
        sui: "水",
        ka: "火",
        do: "土",
        kin: "金",
    };

    public types = AdminMojiBasicComponent.TYPES;


  
    get getGogyou() {
        if (this.info.kana == "") {
            return "";
        }
        else {
            let gogyou = Gogyou.ofKana(this.info.kana);
            if (gogyou == null) {
                return "";
            }
            else {
                return gogyou.jp;
            }
        }
    }
}        