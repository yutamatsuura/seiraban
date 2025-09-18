import Vue from 'vue'
import TopComponent from './components/TopComponent';
import ResultKouseiComponent from './components/ResultKouseiComponent';
import SearchComponent from './components/SearchComponent';
import ResultKanteiComponent from './components/ResultKanteiComponent';
import AdminMojiResultComponent from './admin_components/moji/AdminMojiResultComponent';
import AdminMojiJoukenComponent from './admin_components/moji/AdminMojiJoukenComponent';
import AdminMessageComponent from './admin_components/messages/AdminMessageComponent';
import AdminWordResultComponent from './admin_components/word/AdminWordResultComponent';
import AdminOldMapListComponent from './admin_components/oldmap_list/AdminOldMapListComponent';
import AdminWordJoukenComponent from './admin_components/word/AdminWordJoukenComponent';
import AdminSearchJoukenComponent from './admin_components/search/AdminSearchJoukenComponent';
import AdminSearchResultComponent from './admin_components/search/AdminSearchResultComponent';
import AdminLostListComponent from './admin_components/lost/AdminLostListComponent';
import TestYouinComponent from './test-components/TestYouinComponent';


require('../../css/jquery-ui.min.css');




//ここは絶対変えない
window.onload = () => {
 
    new Vue({
        el: '#app',
        components: {
            SearchComponent:SearchComponent,
            TopComponent:TopComponent,
            ResultKouseiComponent:ResultKouseiComponent,
            ResultKanteiComponent:ResultKanteiComponent,            
            AdminMojiJoukenComponent:AdminMojiJoukenComponent,
            AdminMojiResultComponent:AdminMojiResultComponent,
            AdminWordJoukenComponent:AdminWordJoukenComponent,
            AdminWordResultComponent:AdminWordResultComponent,
            AdminSearchJoukenComponent:AdminSearchJoukenComponent,
            AdminSearchResultComponent:AdminSearchResultComponent,
            AdminMessageComponent:AdminMessageComponent,
            AdminLostListComponent:AdminLostListComponent,
            AdminOldMapListComponent:AdminOldMapListComponent,
            TestYouinComponent:TestYouinComponent,
        }
    });
}

