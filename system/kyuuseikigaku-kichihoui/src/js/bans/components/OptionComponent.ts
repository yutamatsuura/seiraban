import Vue from 'vue'
import Component from 'vue-class-component'
import KibanConfig from '../Config';
import { EVENT_HUB } from '../EventHub';
import StorageUtils from '../units/StorageUtils';
import Kipou from '../units/Kipou';
import Config from '../Config';



interface IOptionCheckItem
{
   id:string;
   jp:string;
   checked:boolean;
}


interface IOptionSelectItem {
   id:string;
   checkedId:string;
   jp: string;
   value: number;
   checked:boolean;
   kipou:boolean;
}


@Component(
   {
      template: require('./htmls/OptionComponent.html'),
   })
export default class OptionComponent extends Vue {
   public checkOptions = new Array<IOptionCheckItem>();
   public selectOptions = new Array<IOptionSelectItem>();

   public KIPOU_SELECTS=[
      Config.LEVEL_KIPOU_STRONG ,  
      Config.LEVEL_KIPOU_WEAK,
      Config.LEVEL_KIPOU_NONE         
   ];

   
   public KYOU_SELECTS=[
      Config.LEVEL_KYOU_STRONG ,  
      Config.LEVEL_KYOU_WEAK,
      Config.LEVEL_KYOU_NONE         
   ]
 
   public openDetail() {
      $(`#option_detail`).slideToggle("slow");
   }

   public created() {
      this.reload();
   }

   private reload() {
      let canvasOption = KibanConfig.getCanvasOption();

      this.checkOptions = 
      [
         { 
            id: KibanConfig.NANBOKU, 
            jp: "南北反転", 
            checked: canvasOption.nanbokuRev
         },
         { 
            id: KibanConfig.TORIKESHI, 
            jp: "取消表示", 
            checked: canvasOption.viewTorikeshi
         }
      ]

      this.selectOptions = new Array<IOptionSelectItem>();
      canvasOption.kipouLevels.forEach((value,id)=>{ 
         let kipou = Kipou.of(id);
         let obj = {
            id:id,
            checkedId:kipou.enableId,
            jp:kipou.name,
            value:value,
            checked:canvasOption.kipouEnables.get(kipou.enableId),
            kipou:kipou.kipou
         }        
         this.selectOptions.push(obj);
      });
   }

   public initOption() {
      this.checkOptions.forEach((obj)=>{
         localStorage.removeItem(obj.id);         
      });
      
      this.selectOptions.forEach((obj)=>{
         localStorage.removeItem(obj.id);         
         localStorage.removeItem(Kipou.of(obj.id).enableId);         
      });

      this.reload();      
      EVENT_HUB.$emit('changeOption');            
   }

   public onCheckChange(i:number) {      
      let obj = this.checkOptions[i];      
      StorageUtils.setBoolean(obj.id,obj.checked);
      EVENT_HUB.$emit('changeOption');
   }


   public onChangeSelect(i: number) {
      let obj = this.selectOptions[i];
      StorageUtils.setNumber(obj.id,obj.value);
      EVENT_HUB.$emit('changeOption');
   } 

   public onChangeEnabled(i:number){
      let obj = this.selectOptions[i];
      let enabledId = Kipou.of(obj.id).enableId;
      StorageUtils.setBoolean(enabledId,obj.checked);
      EVENT_HUB.$emit('changeOption');
   }


}    