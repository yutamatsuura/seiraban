
import {Prop, Component, Vue} from 'vue-property-decorator';
import KanteiViewBase from '../kantei/KanteiViewBase';
    

@Component(
    {
        template: require('./htmls/KanteiTableComponent.html'),
    })
export default class KanteiTableComponent extends Vue {
    @Prop
    ({
        default:null
    })
    protected kanteis:Array<KanteiViewBase>;


    @Prop
    ({
        default:""        
    })    
    protected title:string;
}    
