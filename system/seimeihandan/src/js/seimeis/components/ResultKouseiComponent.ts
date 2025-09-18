

import { Component, Vue } from 'vue-property-decorator';
import Kaku from '../units/Kaku';
import { EVENT_HUB } from '../units/EventHub';
import Seimei from '../units/Seimei';
import Chara from '../units/Chara';





interface KakuTd {
    kakusu: string;
    colspan: number;
    backclass:string;
}

@Component(
    {
        template: require('./htmls/ResultKouseiComponent.html')
    })
export default class ResultKouseiComponent extends Vue {
    public view = false;
    public seimei:Seimei = null;
    public tenkakus = new Array<KakuTd>();
    public jinkakus = new Array<KakuTd>();
    public tikakus = new Array<KakuTd>();
    public soukakus = new Array<KakuTd>();


    public created() {    
        EVENT_HUB.$on('kantei',(seimei:Seimei)=>{
            this.refresh(seimei);
        });

        EVENT_HUB.$on('clear_kantei',(seimei:Seimei)=>{
            this.view = false;
        });
    }

    public getGogyouClass(c:Chara):string
    {
        return c.gogyou.name;        
    }

    public getYouinClass(c:Chara):string
    {
        return c.youin.name;
    }

    private kaku2Td(kaku: Kaku): Array<KakuTd> {
        //前方ダミー    
        let result = new Array<KakuTd>();

        if (kaku.beginIndex != 0) {
            result.push({
                kakusu: "",
                colspan: kaku.beginIndex,
                backclass:"not_kaku"
            });
        }


        result.push({
            kakusu: String(kaku.kakusu),
            colspan: kaku.endIndex - kaku.beginIndex + 1,
            backclass:"kaku"
        });

        //後方ダミー
        let rest = (kaku.seimei.sei.length + kaku.seimei.mei.length) - (kaku.endIndex + 1 );
        if (0 < rest) {
            result.push({
                kakusu: "",
                colspan: rest,
                backclass:"not_kaku"
            })
        }

        return result;
    }

    private refresh(seimei:Seimei) {   
        this.view = true;
        this.seimei = seimei;

        this.tenkakus = this.kaku2Td(Kaku.ofTenkaku(seimei));
        this.jinkakus = this.kaku2Td(Kaku.ofJinkaku(seimei));
        this.tikakus = this.kaku2Td(Kaku.ofTikaku(seimei));
        this.soukakus = this.kaku2Td(Kaku.ofSoukaku(seimei));
    }
}    