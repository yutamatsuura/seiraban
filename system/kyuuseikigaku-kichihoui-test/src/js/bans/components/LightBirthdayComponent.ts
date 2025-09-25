import Vue from 'vue'
import Component from 'vue-class-component'
import LocalDate from '../../times/LocalDate';
import Qsei from '../qseis/Qsei';
import DateUtils from '../../utils/DateUtils';
import ChronoUnit from '../../times/ChronoUnit';
import JikanEto from '../units/JikanEto';
import Config from '../Config';
import Eto60 from '../units/Eto60';
import BirthdayQseiGroup from '../qseis/BirthdayQseiGroup';

@Component(
    {
        template: require('./htmls/LightBirthdayComponent.html'),
    })
export default class LightBirthdayComponent extends Vue {
    //v-model
    public yearQseiName = "";
    public monthQseiName = "";
    public dayQseiName = "";
    public yearEto = "";
    public monthEto = "";
    public dayEto = "";
    public age = 0;
    public birthday = "";
    public maxKipou = "";
    public bigKipou = "";    
    public eto60:Eto60 = null;
    created() {    
        let birthDate = Config.getBirthDate();                
        let birthGroup = BirthdayQseiGroup.of(birthDate,Config.getMan());
        this.yearQseiName = birthGroup.year.name;
        this.monthQseiName = birthGroup.month.name;
        this.dayQseiName = birthGroup.day.name;
        this.birthday = DateUtils.jpText(birthDate);
        this.age = ChronoUnit.YEARS.between(birthDate, LocalDate.now());
        this.yearEto = JikanEto.ofYear(birthDate).name;
        this.monthEto = JikanEto.ofMonth(birthDate).name;
        this.dayEto = JikanEto.ofDay(birthDate).name;
        this.eto60 = JikanEto.ofYear(birthDate).toEto60();
        this.maxKipou = Qsei.toText(birthGroup.maxKipous());
        this.bigKipou = Qsei.toText(birthGroup.bigKipous());
    }
}
