import { Component, Vue } from 'vue-property-decorator';
import { EVENT_HUB } from '../units/EventHub';
import Kaku from '../units/Kaku';
import YouinKantei from '../kantei/youins/YouinKantei';
import InnerGogyouKantei from '../kantei/gogyous/InnnerGogyouKantei';
import Seimei from '../units/Seimei';
import SeimeiDousuuKantei from '../kantei/tentis/SeimeiDousuuKantei';
import TentiDousuuKantei from '../kantei/tentis/TentiDousuuKantei';
import TentiShoutotuKantei from '../kantei/tentis/TentiShoutotuKantei';
import KanteiTableComponent from './KanteiTableComponent';
import YomikudasiKantei from '../kantei/yomikudasi/YomikudasiViewKantei';
import OneCharaKantei from '../kantei/yomikudasi/OneCharaKantei';
import Tigyou9Kantei from '../kantei/yomikudasi/Tigyou9Kantei';
import KanteiResult from '../kantei/KanteiResult';
import Kantei from '../kantei/Kantei';
import KanteiCategory from '../kantei/KanteiCategory';
import JinkakuGogyouKantei from '../kantei/gogyous/JinkakuGogyou';
import TikakuGogyouKantei from '../kantei/gogyous/TikakuGogyou';
import BunriKantei from '../kantei/yomikudasi/BunriKantei';
import SoukakuKantei from '../kantei/kakusus/SoukakuKantei';
import KanteiViewBase from '../kantei/KanteiViewBase';
import KakusuKantei from '../kantei/kakusus/KakusuKantei';
import TigyouSuiKantei from '../kantei/yomikudasi/TigyouSuiKantei';
import Msg1KanteiView from '../kantei/Msg1KanteiView';


interface JsonMessage
{
    msg1:string;
    msg2:string;
    score:string;
    date:string;
}

interface JsonResult
{
    messages:{[key:string]:JsonMessage};
}



@Component(
    {
        template: require('./htmls/ResultKanteiComponent.html'),
        components: {
            KanteiTableComponent: KanteiTableComponent,
        }
    })
export default class ResultKanteiComponent extends Vue {
    public view = false;
    public youins = new Array<KanteiViewBase>();
    public gogyous = new Array<KanteiViewBase>();
    public kakusus = new Array<KanteiViewBase>();
    public tentis = new Array<KanteiViewBase>();
    public yomikudashis = new Array<KanteiViewBase>();
    public messages:{[key:string]:KanteiResult} = {};
    public totalScore = 0;
    protected totalTitle = "";
    protected totalMessage = "";

    public created() {
        EVENT_HUB.$on('kantei', (seimei: Seimei) => {
            this.refresh(seimei);
        });

        EVENT_HUB.$on('clear_kantei',() => {
            this.view = false;
        });
    }

    private filter(kanteis: Array<KanteiViewBase>): Array<KanteiViewBase> {
        let result = new Array<KanteiViewBase>();
        kanteis.forEach((view) => {
            if (view !== null) {
                result.push(view);
            }
        });

        return result;
    }

    private getScore(kantei:Kantei):number
    {
        if(this.messages[kantei.eng] == undefined)
        {
            return 0;    
        }
        else
        {
            return this.messages[kantei.eng].score;        
        }
    }

    private addMap(map:Map<KanteiViewBase,Array<KanteiViewBase>>,views:Array<KanteiViewBase>,stores:Array<KanteiViewBase>)    
    {        
        views.forEach((view)=>{
            map.set(view,stores);            
        });
    }

    private mergeSub(a:KanteiViewBase,b:KanteiViewBase)
    {
        let target = a.target;
        if(a.target.indexOf(b.target) < 0)        
        {
            target += "・" + b.target;
        }

        let merged = new Msg1KanteiView(target,a.kantei);
        merged.messages = a.messages;
        merged.result = {
            score:Number(a.score) + Number(b.score),
            msg1:a.message(),
            msg2:null
        };

        return merged;
    }



    private merge(arr:Array<KanteiViewBase>):Array<KanteiViewBase>
    {
        if(arr.length <= 1)
        {
            return arr;    
        }
        
        let sortArr = arr.sort((a,b)=>{
            if(a.message()<b.message())
            {
                return 1;    
            }
            else if(a.message() > b.message())
            {
                return -1;    
            }
            else
            {
                return 0;    
            }
        });

        let result = new Array<KanteiViewBase>();        
        result.push(sortArr[0]);
        for(let i = 1; i < sortArr.length;i++)
        {
            let merge = result[result.length - 1];
            let current = sortArr[i];
            if(merge.message() == current.message())
            {
                //merge実行
                result[result.length - 1] = this.mergeSub(merge,current);
            }
            else
            {
                result.push(current);
            }                        
        }

        return result;                
    }

    

    private refresh(seimei: Seimei) {
        let jinkaku = Kaku.ofJinkaku(seimei);
        let tikaku = Kaku.ofTikaku(seimei);
        let soukaku = Kaku.ofSoukaku(seimei);
        let tigyou = Kaku.ofTigyou(seimei);

        this.yomikudashis = [];
        this.youins = [];
        this.gogyous = [];
        this.kakusus = [];
        this.tentis = [];
        let map = new Map<KanteiViewBase,Array<KanteiViewBase>>();        
        let newYomis = this.filter([
            OneCharaKantei.of(seimei),
            TigyouSuiKantei.of(seimei),
            Tigyou9Kantei.ofKaku(tigyou,Kantei.KUDASI_TIGYOU9),
            Tigyou9Kantei.ofKaku(tikaku,Kantei.KUDASI_TIKAKU9),
            Tigyou9Kantei.ofKaku(jinkaku,Kantei.KUDASI_JINKAKU9),
            BunriKantei.of(seimei)
        ]).concat(YomikudasiKantei.of(seimei));
        this.addMap(map,newYomis,this.yomikudashis);



        let youins = this.filter([
            YouinKantei.of(seimei),
        ]);
        this.addMap(map,youins,this.youins);

        let newGogyous = this.filter([
            JinkakuGogyouKantei.of(seimei),
            TikakuGogyouKantei.of(seimei),
            InnerGogyouKantei.of(seimei)
        ]);
        this.addMap(map,newGogyous,this.gogyous);

        let newKakusus = this.filter([
            KakusuKantei.of(jinkaku),
            KakusuKantei.of(tikaku),
            KakusuKantei.of(tigyou),
            SoukakuKantei.of(soukaku)
        ]);
        this.addMap(map,newKakusus,this.kakusus);


        let newTentis = this.filter([
            TentiDousuuKantei.of(seimei),
            TentiShoutotuKantei.of(seimei),
            SeimeiDousuuKantei.of(Kaku.ofTenkaku(seimei), Kaku.ofTikaku(seimei)),
        ]);
        this.addMap(map,newTentis,this.tentis);
        
        let all = newYomis.slice();
        all = all.concat(youins);
        all = all.concat(newGogyous);
        all = all.concat(newKakusus);
        all = all.concat(newTentis);
        all = all.sort((a,b)=>{
            return b.getOrder() - a.getOrder();            
        });

        let set = new Set<string>();
        all.forEach((kantei)=>{
            if(kantei.kantei != null && set.has(kantei.kantei.eng) == false)
            {
                set.add(kantei.kantei.eng);
            }
        });

        
        let arr = Array.from(set);
        KanteiCategory.SCORE.subs.forEach((sub)=>{
            arr.push(sub.eng);            
        });

        this.totalTitle = seimei.allNameWithSpace();            

        let url = `https://kigaku-navi.com/qsei/api/select_kantei_result.php?names=${arr.join(',')}`;
        console.log(url);
        $.ajax(url,
            {
                type: 'get',
                cache:true,
                dataType: 'json',
                crossDomain: true
            }).done((json:JsonResult) => {
                this.messages = {};    
                           
                for(let key in json.messages)
                {   
                    let val = json.messages[key];
                    this.messages[key] =                    
                    {
                        msg1:val.msg1.replace(/\n/g, '<br/>'),
                        msg2:val.msg2.replace(/\n/g, '<br/>'),
                        score:Number(val.score),
                    };                 
                }


                let minScore = this.getScore(Kantei.SCORE_MIN);
                let maxScore = this.getScore(Kantei.SCORE_MAX);
                this.totalScore = this.getScore(Kantei.SCORE_BEGIN);
                all.forEach((view)=>{
                    view.result = this.messages[view.kantei.eng]; 
                    view.messages = this.messages;                 
                    if(view.isView(this.totalScore))                    
                    {
                        this.totalScore += this.getScore(view.kantei); 
                        this.totalScore = Math.max(minScore,this.totalScore);
                        this.totalScore = Math.min(maxScore,this.totalScore);
                        map.get(view).push(view);
                    }            
                });

                if(this.totalScore == 100)
                {
                    this.totalMessage = this.messages[Kantei.SCORE_FULL.eng].msg1;
                }
                else if(this.getScore(Kantei.SCORE_OK) < this.totalScore)
                {
                    this.totalMessage = this.messages[Kantei.SCORE_OK.eng].msg1;
                }
                else
                {
                    this.totalMessage = this.messages[Kantei.SCORE_NG.eng].msg1;
                }

                this.yomikudashis = this.merge(this.yomikudashis);
                this.youins = this.merge(this.youins);
                this.gogyous = this.merge(this.gogyous);
                this.kakusus = this.merge(this.kakusus);
                this.tentis = this.merge(this.tentis);

                this.view = true;
        });
    }
}    