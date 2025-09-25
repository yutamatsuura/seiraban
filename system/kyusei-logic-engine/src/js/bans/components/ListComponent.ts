import OptionComponent from './OptionComponent'
import LocalDate from '../../times/LocalDate';
import HtmlUtils from '../../utils/HtmlUtils';
import QseiDate from '../dates/QseiDate';
import CanvasComponent from './CanvasComponent';
import { Vue, Component, Watch } from 'vue-property-decorator';
import QseiGroup from '../qseis/CurrentQseiGroup';
import Qsei from '../qseis/Qsei';
import Config from '../Config';
import BirthdayQseiGroup from '../qseis/BirthdayQseiGroup';
import CurrentQseiGroup from '../qseis/CurrentQseiGroup';
import QseiDayCreater from '../dates/QseiDayCreater';


abstract class KibanListBase {
    constructor() {
    }

    public abstract beforeButton(currentDate: QseiDate): QseiDate;
    public abstract nextButton(currentDate: QseiDate): QseiDate;
    public abstract getTitle(currentDate: LocalDate): string;
    public abstract getTargets(current: QseiGroup): Array<QseiGroup>;
    public abstract getCommons(): Array<string>;
}


class KibanListYearMain extends KibanListBase {
    public beforeButton(currentDate: QseiDate): QseiDate {
        return currentDate.minusYears(1);
    }

    public nextButton(currentDate: QseiDate): QseiDate {
        return currentDate.plusYears(1);
    }

    public getTitle(currentDate: LocalDate): string {
        return currentDate.getYear() + "年以降の年盤";
    }

    public getCommons(): Array<string> {
        return []
    }

    public getTargets(target: QseiGroup): Array<QseiGroup> {
        let result = new Array<QseiGroup>();
        let current = target.date;
        let end = current.plusYears(9);
        while (current.compareTo(end) <= 0) {
            result.push(new QseiGroup(Qsei.getYear(current),null,null,current));
            current = current.plusYears(1);
        }

        return result;
    }
}


class KibanListMonthMain extends KibanListBase {
    public beforeButton(currentDate: QseiDate): QseiDate {
        return currentDate.minusYears(1);
    }

    public nextButton(currentDate: QseiDate): QseiDate {
        return currentDate.plusYears(1);
    }

    public getTitle(currentDate: LocalDate): string {
        let qseiDate = QseiDate.of(currentDate);
        return `${qseiDate.year}年の月盤`;
    }


    public getTargets(target: QseiGroup): Array<QseiGroup> {
        let result = new Array<QseiGroup>();
        let qseiDate = QseiDate.of(target.date);
        qseiDate.getMonthBegins().forEach((current) => {
            result.push(new QseiGroup(target.year,Qsei.getMonth(current),null,current));
        });

        return result;
    }

    public getCommons(): Array<string> {
        return ['year'];
    }

}


class KibanListDayMain extends KibanListBase {
    public beforeButton(currentDate: QseiDate): QseiDate {
        return currentDate.minusMonths(1);
    }

    public nextButton(currentDate: QseiDate): QseiDate {
        return currentDate.plusMonths(1);
    }

    public getTitle(currentDate: LocalDate): string {
        return `${currentDate.getYear()}年 ${currentDate.getMonthValue()}月の日盤`;
    }


    public getTargets(target: QseiGroup): Array<QseiGroup> {
        let qseiDate = QseiDate.of(target.date);      
        let current = qseiDate.getMonthBegin();
        let end = qseiDate.getMonthEnd();
        let dates = new Array<LocalDate>();
        while (current.compareTo(end) <= 0) {
            dates.push(current);
            current = current.plusDays(1);
        }
                
        let dayInfos = QseiDayCreater.getDays(dates);
        
        let result = new Array<QseiGroup>();        
        dayInfos.forEach((info,i)=>{
            let date = dates[i];
            result.push(new QseiGroup(target.year,target.month,info,date));
        });

        return result;
    }

    public getCommons(): Array<string> {
        return ['year','month'];
    }
}


@Component(
    {
        template: require('./htmls/ListComponent.html'),
        components: {
            CanvasComponent: CanvasComponent,
            OptionComponent: OptionComponent
        }
    })
export default class ListComponent extends Vue {
    private render: KibanListBase;
    
    public current = CurrentQseiGroup.of(LocalDate.now());
    public type: string;
    public dates = new Array<QseiGroup>();
    public birth:BirthdayQseiGroup;
    public title: string;
    public created() {
        let params = HtmlUtils.paramList();
        this.type = params.get("type");
        let target = params.get("target");
        this.current = CurrentQseiGroup.of(LocalDate.now());
        if (target !== null) {
            this.current = CurrentQseiGroup.of(LocalDate.ofTime(Number(target)));
        }

        this.birth = BirthdayQseiGroup.of(Config.getBirthDate(),Config.getMan());
        if (this.type == "month") {
            this.render = new KibanListMonthMain();
        }
        else if (this.type == "year") {
            this.render = new KibanListYearMain();
        }
        else if (this.type == "day") {
            this.render = new KibanListDayMain();
        }

        this.updateTarget();
    }

    get commons()
    {
        return this.render.getCommons();    
    }

    @Watch('current')
    public updateTarget() {
        let type = HtmlUtils.paramList().get('type');
        let target = String(this.current.date.getTime());
        let path = `${location.pathname}?type=${type}&target=${target}`;

        history.replaceState('', '', path)

        this.title = this.render.getTitle(this.current.date);
        this.dates = this.render.getTargets(this.current);
    }

    public mounted() {
        $(`#before_button`).on('click', () => {
            let currentDate = this.render.beforeButton(QseiDate.of(this.current.date)).date;
            this.current = CurrentQseiGroup.of(currentDate);
        });

        $(`#next_button`).on('click', () => {
            let currentDate = this.render.nextButton(QseiDate.of(this.current.date)).date;    
            this.current = CurrentQseiGroup.of(currentDate);
        });
    }

    public onChangeOption() {
        this.updateTarget();
    }
}
