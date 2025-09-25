import Vue from 'vue'
import TopComponent from "./components/TopComponent";
import BirthdayComponent from './components/BirthdayComponent';
import LightBirthdayComponent from './components/LightBirthdayComponent';
import KipouComponent from './components/KipouComponent';
import ListComponent from './components/ListComponent';
import BirthdayDetailComponent from './components/BirthdayDetailComponent';
import TestUruuComponent from './test-components/TestUruuComponent';
import TestSetuComponent from './test-components/TestSetuComponent';


require('../../css/jquery-ui.min.css');




//ここは絶対変えない
window.onload = () => {
 
    new Vue({
        el: '#app',
        components: {
            TestUruuComponent:TestUruuComponent,
            TestSetuComponent:TestSetuComponent,            
            LightBirthdayComponent:LightBirthdayComponent,    
            BirthdayDetailComponent:BirthdayDetailComponent,    
            TopComponent: TopComponent,
            BirthdayComponent:BirthdayComponent,            
            KipouComponent:KipouComponent,
            ListComponent:ListComponent
        }
    });
}

