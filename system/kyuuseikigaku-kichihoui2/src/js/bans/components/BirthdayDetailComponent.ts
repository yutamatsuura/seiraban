import Vue from 'vue'
import Component from 'vue-class-component'
import Eto60 from '../units/Eto60';
import Config from '../Config';
import LocalDate from '../../times/LocalDate';
import ChronoUnit from '../../times/ChronoUnit';
import JikanEto from '../units/JikanEto';
import Qsei from '../qseis/Qsei';
import BirthdayQseiGroup from '../qseis/BirthdayQseiGroup';

@Component(
    {
        template: require('./htmls/BirthdayDetailComponent.html'),        
    })
export default class BirthdayDetailComponent extends Vue {
    //v-model
    public yearEto = "";
    public monthEto = "";
    public dayEto = "";
    public age = 0;
    public maxKipou = "";
    public bigKipou = "";
    public keisha = "";
    public doukai = "";
    public nattin = "";
    public eto60:Eto60 = null;
    public birth:BirthdayQseiGroup =null;

    created() {
        let birthDate = Config.getBirthDate();
        let man = Config.getMan();
        this.birth = BirthdayQseiGroup.of(birthDate,man);
        this.age = ChronoUnit.YEARS.between(birthDate, LocalDate.now());
        this.yearEto = JikanEto.ofYear(birthDate).name;
        this.monthEto = JikanEto.ofMonth(birthDate).name;
        this.dayEto = JikanEto.ofDay(birthDate).name;
        this.maxKipou = Qsei.toText(this.birth.maxKipous());
        this.bigKipou = Qsei.toText(this.birth.bigKipous());
        this.keisha = this.birth.keisha(man).name;
        this.doukai = this.birth.doukai(man).name;
        this.eto60 = JikanEto.ofYear(birthDate).toEto60();        
        this.nattin = JikanEto.ofDay(birthDate).toNattin().name;
    }
}
