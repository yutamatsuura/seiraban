

declare namespace Y
{
    class LatLng
    {
        constructor(lat:number,lng:number);
        constructor(lat:number,lng:number,)
        lat():number;//緯度
        lng():number;//軽度
        distance(other:LatLng):number;
    }

    class Point
    {
        public x:number;
        public y:number;    
        constructor(x:number,y:number);        
    }

    class Size
    {
        width:number;
        height:number;
        constructor(x:number,y:number);
    }

    class Style
    {
        constructor(color:string,width:number|string,alpha:number);        
    }   
    
    //Control系
    abstract class Control
    {        
    }

    class LayerSetControl extends Control
    {        
    }

    class ZoomControl extends Control
    {
    }
    
    class CenterMarkControl extends Control
    {        
    }   

    //Feature系
    abstract class Feature
    {
        bind(type:string, func:()=>void, object?:any):void;
    }

    class Polyline extends Feature
    {
        constructor(latlngs:Array<LatLng>,options:PolylineOption);        
    }

    class Circle extends Feature
    {
        constructor(latlng:LatLng, radius:number, options:CircleOption);
    }

    class Icon extends Feature
    {
        constructor(image:string,options:IconOption);
    }

    class Marker extends Feature
    {
        constructor(latlng:LatLng,options:MarkerOption);
    }
    
    interface MarkerOption
    {
        icon?:Icon
    }

    interface PolylineOption
    {
        clickable?:boolean;
        draggable?:boolean;
        clipping?:boolean;
        strokeStyle?:Style;
    }

    interface CircleOption
    {
        unit:string;
        strokeStyle?:Style;
        fillStyle?:Style;
    }

    interface IconOption
    {
        iconSize:Size
    }

    class Projection
    {
        fromLatLngToPixel(latlng:LatLng, zoom:number):Point;
        getWrapWidth(zoom:number):number
        fromLatLngToTile(latlng:LatLng,zoom:number):Tile;
    }

    interface Tile
    {
        tx:number;
        ty:number;
        x:number;
        y:number;
    }


    class Layer
    {

    }

    class LayerSet
    {
        layers:Array<Layer>;
        projection:Projection;
    }


    class LayerSetId
    {
        static NORMAL:number;
    }


    class Map
    {
        public currentLayerSet:LayerSet;
        constructor(id:string);
        addControl(control:Control):void;
        addFeature(fea:Feature):void;
        getCenter():LatLng;
        removeFeature(fea:Feature):void;
        drawMap(center:LatLng,scale:number,style?:number):void;
        bind(name:string,func:(param:void)=>void):void;
        panTo(center:LatLng,animation:boolean):void;
        fromLatLngToPixel(latlng:LatLng,zoom:number):Point;
        fromLatLngToContainerPixel(latlng:LatLng,unbounded?:boolean):Point;
        getZoom():number;
        fromLatLngToDivPixel(latLng:LatLng):Point;
        getSize():Size;
        updateSize():void;
    }
}
