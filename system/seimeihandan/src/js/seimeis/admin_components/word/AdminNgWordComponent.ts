import { Component, Vue,  Prop } from 'vue-property-decorator';
import KanteiCategory from '../../kantei/KanteiCategory';


interface EngJp {
    eng: string;
    jp: string;
    override: boolean;
}

interface EngJPChecked extends EngJp {
    checked?: boolean
    sp: string;
}

const UNIT_NUM = 2;


@Component(
    {
        template: require('./htmls/AdminNgWordComponent.html'),
    })
export default class AdminNgWordComponent extends Vue {
    @Prop({
        default:"",
        required:true
    })
    protected word:string;

   
    @Prop({
        default:null,
        required:true
    })
    protected ngwords:Array<Ngword>;
    protected ngChecks = new Array<EngJPChecked>();

 
    
    public created()
    {
        this.ngChecks = AdminNgWordComponent.toNgCheck(this.ngwords);    
    }

    public getNgwordsJson()
    {
        let submitReasons = this.ngChecks.filter((ng) => {
            return ng.checked;
        });    
        return JSON.stringify(submitReasons);    
    }

    get checkOnlys(): Array<Array<EngJPChecked>> {
        let result = new Array<Array<EngJPChecked>>();
        let rest = this.ngChecks.filter((ng) => {
            return ng.override == false;
        });

        while (0 < rest.length) {
            let add = rest.slice(0, UNIT_NUM);
            result.push(add);
            rest = rest.slice(add.length);
        }

        return result;
    }

    get customs(): Array<EngJPChecked> {
        let result = this.ngChecks.filter((ng) => {
            return ng.override == true;
        });
        return result;        
    }
    
    public static toNgCheck(values: Array<Ngword>): Array<EngJPChecked> {
        let map = new Map<string, EngJPChecked>();
        KanteiCategory.YOMIKUDASI.subs.forEach((ng) => {
            if (ng.checkbox) {
                map.set(ng.eng, {
                    eng: ng.eng,
                    jp: ng.jp,
                    override: ng.override,
                    checked: false,
                    sp: ""
                });
            }
        });

        values.forEach((value) => {
            if (map.has(value.reason)) {
                let ng = map.get(value.reason);
                ng.checked = true;
                ng.sp = value.sp;
            }
        });

        let result = new Array<EngJPChecked>();
        map.forEach((check) => {
            result.push(check);
        });

        return result;
    }

}