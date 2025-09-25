import Vue from 'vue'
import Component from 'vue-class-component'
import OptionComponent from './OptionComponent';
import LocalDate from '../../times/LocalDate';
import HtmlUtils from '../../utils/HtmlUtils';
import CanvasComponent from './CanvasComponent';
import { Watch } from 'vue-property-decorator';
import Config from '../Config';
import BirthdayQseiGroup from '../qseis/BirthdayQseiGroup';
import CurrentQseiGroup from '../qseis/CurrentQseiGroup';

require("jquery-ui");


@Component(
    {
        template: require('./htmls/KipouComponent.html'),
        components: {
            CanvasComponent:CanvasComponent,
            OptionComponent: OptionComponent,
        }
    })
export default class KipouComponent extends Vue
{
    private $datePick: JQuery<HTMLElement>;
    public birth =  BirthdayQseiGroup.of(LocalDate.now(),true);   //監視のためのデフォルト値
    public current =  CurrentQseiGroup.of(LocalDate.now()); //監視のためのデフォルト値
    public gotoYearLink = `/qsei/ban_list.php?type=year&target=${LocalDate.now().getTime()}`;    
     

   
    protected created()
    {
        HtmlUtils.setLocalJPDate();
        this.birth = BirthdayQseiGroup.of(
            Config.getBirthDate(),
            Config.getMan()
        );
        this.current = CurrentQseiGroup.of(LocalDate.now());
    }

    protected mounted()
    {       
        let month = screen.width < 480?1 :3;
        this.$datePick = $("#currentday_cal");        
        this.$datePick.datepicker({
            changeMonth: true,
            numberOfMonths: month,
            changeYear: true,
            defaultDate:LocalDate.now().getDate(),
            onSelect: () => {
                let current = LocalDate.ofDate(
                    this.$datePick.datepicker('getDate')
                );
                this.current = CurrentQseiGroup.of(current);
            }
        });
    }
       
    @Watch('current')
    protected updateCurrnet()
    {
        this.gotoYearLink = `/qsei/ban_list.php?type=year&target=${this.current.date.getTime()}`;    
    }

    public getCurrentDate(): LocalDate {
        return LocalDate.ofDate(this.$datePick.datepicker('getDate'));
    }

    public openCalendar()
    {
        this.$datePick.slideToggle("slow");
    }

    public setDatePickDate(date: LocalDate) {
        this.$datePick.datepicker('setDate', date.getRaw());
    }

    public nextYear()
    {   
        let nextDate = this.current.date.plusYears(1);
        this.current = CurrentQseiGroup.of(nextDate);
        this.setDatePickDate(this.current.date);
    }

    public beforeYear()
    {
        let beforeDate = this.current.date.minusYears(1);            
        this.current = CurrentQseiGroup.of(beforeDate);
        this.setDatePickDate(this.current.date);
    }

    public nextMonth()
    {
        let nextDate = this.current.date.plusMonths(1);    
        this.current = CurrentQseiGroup.of(nextDate)
        this.setDatePickDate(this.current.date);
    }

    public beforeMonth()
    {
        let beforeDate = this.current.date.minusMonths(1);                    
        this.current = CurrentQseiGroup.of(beforeDate)
        this.setDatePickDate(this.current.date);
    }

    public nextDay()
    {
        let nextDate = this.current.date.plusDays(1);                    
        this.current = CurrentQseiGroup.of(nextDate)
        this.setDatePickDate(this.current.date);
    }

    public beforeDay()
    {
        let beforeDate = this.current.date.minusDays(1);                    
        this.current = CurrentQseiGroup.of(beforeDate);
        this.setDatePickDate(this.current.date);
    }
}
