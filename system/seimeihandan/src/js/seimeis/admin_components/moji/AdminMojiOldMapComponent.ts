import { Component, Vue, Prop} from 'vue-property-decorator';
import HtmlUtils from '../../../utils/HtmlUtils';
import AdminMojiResult from './AdminMojiResult';

@Component(
    {
        template: require('./htmls/AdminMojiOldmapComponent.html'),
    })
export default class AdminMojiOldMapComponent extends Vue {
    @Prop({
        default:null,
        required:true   
    })
    protected info:AdminMojiResult;    
    protected oldMapEnable = false;

    public created()
    {
        this.oldMapEnable = 0 < this.info.oldmoji.length;        
    }


    get oldCode()
    {
        if(this.info.oldmoji == "")    
        {
            return "";    
        }
        else
        {
            return HtmlUtils.toHex(this.info.oldmoji);
        }        
    }    

    get oldLink()
    {
        if(this.info.oldmoji == "")    
        {
            return "";    
        }
        else
        {
            return `/qsei/admin/seimei_moji.php?moji=${this.info.oldmoji}`;    
        }   
    }    
}