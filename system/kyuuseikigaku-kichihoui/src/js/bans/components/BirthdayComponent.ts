import Vue from 'vue'
import Component from 'vue-class-component'
import LocalDate from '../../times/LocalDate';
import DateUtils from '../../utils/DateUtils';
import ChronoUnit from '../../times/ChronoUnit';
import JikanEto from '../units/JikanEto';
import OptionComponent from './OptionComponent';
import Config from '../Config';
import Eto60 from '../units/Eto60';
import CanvasComponent from './CanvasComponent';
import BirthdayQseiGroup from '../qseis/BirthdayQseiGroup';



@Component(
    {
        template: require('./htmls/BirthdayComponent.html'),
        components: {
            CanvasComponent:CanvasComponent,
            OptionComponent: OptionComponent
        }
    })
    export default class BirthdayComponent extends Vue {
    //v-model
    public yearQseiName = "";
    public monthQseiName = "";
    public dayQseiName = "";
    public age = 0;
    public birthday = "";
    public eto60:Eto60 = null;
    public birth:BirthdayQseiGroup = null;

    created() {
        let birthDate = Config.getBirthDate();
        let man = Config.getMan();
        this.birth = BirthdayQseiGroup.of(birthDate,man);
        this.yearQseiName = this.birth.year.name;
        this.monthQseiName = this.birth.month.name;
        this.dayQseiName = this.birth.day.name;
        this.birthday = DateUtils.jpText(birthDate);
        this.age = ChronoUnit.YEARS.between(birthDate, LocalDate.now());
        this.eto60 = JikanEto.ofYear(birthDate).toEto60();        
    }
}
