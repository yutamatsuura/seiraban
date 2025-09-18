import { Component, Vue } from 'vue-property-decorator';
import KanteiCategory from '../../kantei/KanteiCategory';

interface EngJp {
    eng: string;
    jp: string;
}

interface SubMessage extends EngJp {
    msg1: string;
    msg2: string;
    score: number;
    viewscore:boolean;
    viewmsg1:boolean;
    viewmsg2:boolean;
    titlemsg1:string;
    titlemsg2:string;
}


interface MainMessage extends EngJp {
    view: boolean;
    subs: Array<SubMessage>;
}

interface KanteiResult {
    name: string;
    msg1: string;
    msg2: string;
    score: number;
}


@Component(
    {
        template: require('./htmls/AdminMessageComponent.html')
    })
export default class AdminMessageComponent extends Vue {
    protected categorys = new Array<MainMessage>();
    protected edit = false;

    public created() {
        this.categorys = new Array<MainMessage>();

        let map = new Map<string, SubMessage>();
        KanteiCategory.ITEMS.forEach((category) => {
            let subs = new Array<SubMessage>();
            category.subs.forEach((sub) => {
                let addSub:SubMessage = {
                    eng: sub.eng,
                    jp: sub.jp,
                    msg1:"",
                    msg2:"",
                    score:0,
                    viewscore:sub.viewscore,
                    viewmsg1:sub.viewmsg1,
                    viewmsg2:sub.viewmsg2,
                    titlemsg1:sub.titlemsg1,
                    titlemsg2:sub.titlemsg2,                    
                };

                map.set(sub.eng, addSub);

                subs.push(addSub);
            });

            this.categorys.push({
                eng: category.eng,
                jp: category.jp,
                view: false,
                subs: subs
            })

        });


        let url = "https://kigaku-navi.com/qsei/api/select_kantei_results.php";
        console.log(url);
        $.ajax(url,
            {
                type: 'get',
                dataType: 'json',
                crossDomain: true
            }).done((results: Array<KanteiResult>) => {
                results.forEach((result) => {
                    let key = result.name;
                    if (map.has(key)) {
                        map.get(key).msg1 = result.msg1;
                        map.get(key).msg2 = result.msg2;
                        map.get(key).score = result.score;
                    }
                });
                this.edit = true;
            }).fail((error) => {
                alert("取得に失敗しました。" + error.responseText);
            });
    }

    public submitModify(sub: SubMessage) {
        if(this.edit == false)    
        {
            alert("現在は編集不可能な状態です。") ;
            return;
        }

        
        let url = `https://kigaku-navi.com/qsei/api/modify_kantei_result.php`;
        console.log(url);
        $.ajax(url,
            {
                type: 'post',
                dataType: 'json',
                crossDomain: true,
                data: {
                    name: sub.eng,
                    msg1: sub.msg1,
                    msg2: sub.msg2,
                    score: sub.score
                }
            }).done(() => {
                alert("登録に成功しました");
            }).fail((error) => {
                alert("登録に失敗しました。" + error.responseText);
            });
    }

    public toggleShow(index: number) {
        let category = this.categorys[index];
        category.view = !category.view;
    }

    public toggleText(index:number){
        let category = this.categorys[index];
        return category.view ? "非表示" : "表示";                
    }
}



