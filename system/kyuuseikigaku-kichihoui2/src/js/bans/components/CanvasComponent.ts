import { Component, Prop, Vue, Watch } from 'vue-property-decorator';
import LocalDate from '../../times/LocalDate';
import { EVENT_HUB } from '../EventHub';
import Canvas from '../canvases/Canvas';
import Qsei from '../qseis/Qsei';
import Kipou from '../units/Kipou';
import DateUtils from '../../utils/DateUtils';
import JikanEto from '../units/JikanEto';
import QseiDate from '../dates/QseiDate';
import KibanConfig from '../Config';
import QseiGroupBase from '../qseis/QseiGroupBase';
import Config from '../Config';
import Eto from '../units/Eto';

const SENRO147 = new Set<number>(
    [
        Eto.NE.index,
        Eto.USA.index,
        Eto.UMA.index,
        Eto.TORI.index,
    ]);

const SENRO369 = new Set<number>(
    [
        Eto.USHI.index,
        Eto.TATU.index,
        Eto.HITUJI.index,
        Eto.INU.index,
    ]);

const SENRO258 = new Set<number>(
        [
            Eto.TORA.index,
            Eto.MI.index,
            Eto.SARU.index,
            Eto.INO.index,
        ]);

interface SenroImg
{
    senros:Set<number> ;
    img:string;   
}

const SENRO_IMG147 ={
    senros:SENRO147,
    img:`/qsei/img/rosen/sphere.png`    
}

const SENRO_IMG369 ={
    senros:SENRO369,
    img:`/qsei/img/rosen/sikaku.png`    
}

const SENRO_IMG258 ={
    senros:SENRO258,
    img:`/qsei/img/rosen/rokaku.png`    
}



const SENRO_MAP = new Map<number,SenroImg>([
    [1,SENRO_IMG147],
    [4,SENRO_IMG147],
    [7,SENRO_IMG147],

    [3,SENRO_IMG369],
    [6,SENRO_IMG369],
    [9,SENRO_IMG369],

    [2,SENRO_IMG258],
    [5,SENRO_IMG258],
    [8,SENRO_IMG258],
]);




@Component(
    {
        template: require('./htmls/CanvasComponent.html'),
    })
export default class CanvasComponent extends Vue {
    @Prop({ default: null })
    public current: QseiGroupBase;

    @Prop({ default: null })
    public birth: QseiGroupBase;

    @Prop({
        default: "year"
    })
    public type: string;
    public gotoLink: string;

    @Prop({
        default: null,
        required: false
    })
    public overrideTitle: string;

    @Prop({
        default: null,
        required: false
    })
    public overrideHosoku: string;

    @Prop({
        default: true,
        required: false
    })
    public viewLink: boolean;

    public id = CanvasComponent.getUniqueStr();
    public canvasId = "canvas" + this.id;

    private canvas: Canvas;
    private listener: any;



    public static getUniqueStr(myStrong?: number): string {
        let strong = 1000;
        if (myStrong) strong = myStrong;
        return new Date().getTime().toString(16) + Math.floor(strong * Math.random()).toString(16)
    }

    private sub: DateRenderBase;

    public created() {
        if (this.type == "year") {
            this.sub = new YearDateRender();
        }
        else if (this.type == "month") {
            this.sub = new MonthDateRender();
        }
        else {
            this.sub = new DayDateRender();
        }


        EVENT_HUB.$on('changeOption', () => {
            this.refresh();
        });

        this.canvas = new Canvas(
            this.canvasId,
            this.sub.getQsei(this.current),
            this.sub.getKipous(this.birth, this.current),
            Config.getCanvasOption()
        );

        this.gotoLink = this.sub.getLink(this.current);

        let resizeTimer: any;
        let interval = Math.floor(1000 / 60 * 10);

        this.listener = window.addEventListener('resize', (event) => {
            if (resizeTimer !== false) {
                clearTimeout(resizeTimer);
            }
            resizeTimer = setTimeout(() => {
                this.refresh();
            }, interval);
        });
    }


    public mounted() {
        this.refresh();
    }

    public destroyed() {
        window.removeEventListener('resize', this.listener);
    }

    @Watch('current')
    public refresh() {
        this.canvas.option = KibanConfig.getCanvasOption();
        this.canvas.kipous = this.sub.getKipous(this.birth, this.current);
        this.canvas.qsei = this.sub.getQsei(this.current);
        this.canvas.draw();

        this.gotoLink = this.sub.getLink(this.current);
    }

    get title() {
        if (this.overrideTitle === null) {
            let eto = this.sub.getEto(this.current.date);
            return this.sub.getTitle(this.current.date) + " " + eto.toJikan().name + " " + eto.toEto().name;
        }
        else {
            return this.overrideTitle;
        }
    }

    get hosoku() {
        if (this.overrideHosoku === null) {
            return this.sub.getHosoku(this.current);
        }
        else {
            return this.overrideHosoku;
        }
    }

    get ban() {
        return this.sub.getBan();
    }

    get childBan() {
        let childBan = this.sub.getChildBan();
        if (childBan == "") {
            return "";
        }
        else {
            return `${childBan}一覧へ`;
        }
    }

    get backClass() {
        return this.sub.backClass(this.current);
    }

    get rosenImg() {
        if(this.overrideTitle != null)
        {
            return "";    
        }

        let senro = SENRO_MAP.get(this.birth.year.index);
        let eto = this.sub.getEto(this.current.date).toEto();

        if(senro.senros.has(eto.index))
        {
            return senro.img;
        }
        else
        {
            return "";  
        }        
    }

    get rosenText() {
        let senro = SENRO_MAP.get(this.birth.year.index);
        let eto = this.sub.getEto(this.current.date).toEto();

        if(senro.senros.has(eto.index))
        {
            return eto.name;            
        }
        else
        {
            return "";  
        }
    }
};


abstract class DateRenderBase {
    public abstract getQsei(current: QseiGroupBase): Qsei;
    public abstract getKipous(birth: QseiGroupBase, current: QseiGroupBase): Array<Array<Kipou>>;
    public abstract getTitle(current: LocalDate): string;
    public abstract getEto(current: LocalDate): JikanEto;
    public abstract getHosoku(current: QseiGroupBase): string;
    public abstract getBan(): string;
    public abstract getChildBan(): string;
    public abstract getChildType(): string;
    public backClass(current: QseiGroupBase) {
        return "none_kirikae";
    }

    public getLink(current: QseiGroupBase): string {
        let type = this.getChildType();
        if (type == "") {
            return "";
        }
        else {
            return `/qsei/ban_list.php?type=${type}&target=${current.date.getTime()}`;
        }
    }
}

class YearDateRender extends DateRenderBase {
    public getQsei(current: QseiGroupBase): Qsei {
        return current.year;
    }

    public getKipous(birth: QseiGroupBase, current: QseiGroupBase): Array<Array<Kipou>> {
        return Kipou.currentOfYear(birth, current);
    }

    public getTitle(current: LocalDate): string {
        return current.getYear() + "年";
    }

    public getEto(current: LocalDate): JikanEto {
        return JikanEto.ofYear(current);
    }


    private createYearRange(current: LocalDate): Array<LocalDate> {
        let currentMonth = QseiDate.of(current);
        return [
            currentMonth.getYearBegin(),
            currentMonth.getYearEnd()
        ];
    }

    public getHosoku(current: QseiGroupBase): string {
        let range = this.createYearRange(current.date);
        let beginText = DateUtils.jpText(range[0]);
        let endText = DateUtils.jpText(range[1]);

        return "(" + beginText + "～" + endText + ")";
    }

    public getBan(): string {
        return "年盤";
    }

    public getChildBan(): string {
        return "月盤";
    }

    public getChildType(): string {
        return "month";
    }
}

class MonthDateRender extends DateRenderBase {
    public getQsei(current: QseiGroupBase): Qsei {
        return current.month;
    }

    public getKipous(birth: QseiGroupBase, current: QseiGroupBase): Array<Array<Kipou>> {
        return Kipou.currentOfMonth(birth, current);
    }

    public getTitle(current: LocalDate): string {
        let qseiDate = QseiDate.of(current);
        return qseiDate.month12 + "月";
    }

    public getEto(current: LocalDate): JikanEto {
        return JikanEto.ofMonth(current);
    }

    public createMonthRange(current: LocalDate): Array<LocalDate> {
        let qseiMonth = QseiDate.of(current);
        return [
            qseiMonth.getMonthBegin(),
            qseiMonth.getMonthEnd()
        ];
    }


    public getHosoku(current: QseiGroupBase): string {
        let range = this.createMonthRange(current.date);
        let beginText = DateUtils.jpMonthText(range[0]);
        let endText = DateUtils.jpMonthText(range[1]);

        return "(" + beginText + "～" + endText + ")";
    }



    public getBan(): string {
        return "月盤";
    }


    public getChildBan(): string {
        return "日盤";
    }

    public getChildType(): string {
        return "day";
    }
}


class DayDateRender extends DateRenderBase {
    public getQsei(current: QseiGroupBase): Qsei {
        return current.day;
    }

    public getKipous(birth: QseiGroupBase, current: QseiGroupBase): Array<Array<Kipou>> {
        return Kipou.currentOfDay(birth, current);
    }

    public getTitle(current: LocalDate): string {
        return DateUtils.jpText(current);
    }

    public getEto(current: LocalDate): JikanEto {
        return JikanEto.ofDay(current);
    }

    public getHosoku(current: QseiGroupBase): string {
        let text = new Array<string>();
        let qDate = QseiDate.of(current.date);
        if (qDate.isDoyou()) {
            text.push("土用");
        }

        let info = current.day;
        if (info.isKirikaeBefore || info.isKirikaeAfter) {
            text.push("切替日")
        }

        if (qDate.getMonthBegin().equals(current.date)) {
            text.push("節入り")
        }


        return text.join('/');
    }

    public backClass(current: QseiGroupBase) {
        let info = current.day;
        if (info.isKirikaeBefore || info.isKirikaeAfter) {
            return "kirikae";
        }
        else {
            return "none_kirikae";
        }
    }

    public getBan(): string {
        return "日盤";
    }

    public getChildBan(): string {
        return "";
    }

    public getChildType(): string {
        return "";
    }
}