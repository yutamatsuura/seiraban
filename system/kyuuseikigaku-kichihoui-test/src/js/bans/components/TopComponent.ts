import Vue from 'vue'
import Component from 'vue-class-component'
import KibanConfig from '../Config';


@Component(
{
    template:require('./htmls/TopComponent.html')
})
export default class TopComponent  extends Vue {
    //v-model
    public selectYear = "2000";
    public years = new Array<string>();
    public selectMonth = "1";
    public months = new Array<string>();
    public selectDay = "1";
    public days = new Array<string>();
    public sexs = ["男","女"];
    public selectSex = this.sexs[0];


    private static readonly YEAR_BEGIN = 1900;
    private static readonly YEAR_END = 2100;
    private static readonly MONTH_BEGIN = 1;
    private static readonly MONTH_END = 12;
    private static readonly DAY_BEGIN = 1;
    private static readonly DAY_END = 31;
    
    private static readonly BEGIN_YEAR = "2000";
    private static readonly BEGIN_SEX = "男";
    private static readonly BEGIN_MONTH = "1";
    private static readonly BEGIN_DAY = "1";

    private createList(begin: number, end: number): Array<string> {
        let result = new Array<string>();
        for (let i = begin; i <= end; i++) {
            result.push(String(i));
        }

        return result;
    }

    public created()
    {
        this.years = this.createList(TopComponent.YEAR_BEGIN, TopComponent.YEAR_END);    
        this.months = this.createList(TopComponent.MONTH_BEGIN, TopComponent.MONTH_END);    
        this.days = this.createList(TopComponent.DAY_BEGIN, TopComponent.DAY_END);    
        
        this.selectYear = localStorage.getItem(KibanConfig.YEAR) === null ? TopComponent.BEGIN_YEAR : localStorage.getItem(KibanConfig.YEAR);
        this.selectMonth = localStorage.getItem(KibanConfig.MONTH) === null ? TopComponent.BEGIN_MONTH : localStorage.getItem(KibanConfig.MONTH);
        this.selectDay = localStorage.getItem(KibanConfig.DAY) === null ? TopComponent.BEGIN_DAY : localStorage.getItem(KibanConfig.DAY);
        this.selectSex = localStorage.getItem(KibanConfig.SEX) === null ? TopComponent.BEGIN_SEX : localStorage.getItem(KibanConfig.SEX);
    }

    public submitBirthday()
    {
        localStorage.setItem(KibanConfig.YEAR, this.selectYear);
        localStorage.setItem(KibanConfig.MONTH, this.selectMonth);
        localStorage.setItem(KibanConfig.DAY, this.selectDay);
        localStorage.setItem(KibanConfig.SEX, this.selectSex);

        location.href = `ban_birthday.html`;
    }

    public submitKipou()
    {
        localStorage.setItem(KibanConfig.YEAR, this.selectYear);
        localStorage.setItem(KibanConfig.MONTH, this.selectMonth);
        localStorage.setItem(KibanConfig.DAY, this.selectDay);
        localStorage.setItem(KibanConfig.SEX, this.selectSex);

        location.href = `ban_kipou.html`;
    }
}