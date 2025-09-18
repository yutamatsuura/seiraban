import Vue from 'vue'
import Component from 'vue-class-component'
import QseiDay from '../dates/QseiDay';
import LocalDate from '../../times/LocalDate';
import QseiDayCreater from '../dates/QseiDayCreater';


@Component(
    {
        template: require('./htmls/TesturuuComponent.html')
    })
export default class TestUruuComponent extends Vue {
    public dayInfos = new Array<QseiDay>();    

    public created()
    {
        let begin = LocalDate.of(2000,1,1);
        let end = LocalDate.of(2050,1,1);        
        let table = new QseiDayCreater();
        table.create(begin,end);

        let key="";        
        let keys = table.getKeys();
        while((key = keys.next().value) != null)
        {
            this.dayInfos.push(table.getValue(key));
        } 
    }    



}    