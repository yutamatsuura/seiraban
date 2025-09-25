import Vue from 'vue'
import Component from 'vue-class-component'
import LocalDate from '../../times/LocalDate';
import QseiDate from '../dates/QseiDate';
import Setu from '../units/Setu';


@Component(
    {
        template: require('./htmls/TestSetuComponent.html')
    })
export default class TestSetuComponent extends Vue {
    public dates = new Array<QseiDate>();

    public created()
    {
        for(let year = 1900; year < 2100; year++)    
        {
            this.dates.push(QseiDate.of(LocalDate.of(year,1,1)));
        }     
    }    

    public getDoyou(year:number,index:number)
    {
        return Setu.getDoyouBegin(year,index);        
    }

    public toDM(date:LocalDate)
    {
        return `${date.getMonthValue()}-${date.getDayOfMonth()}`;        
    }

}    