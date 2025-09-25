import * as d3 from 'd3';
import IPoint from '../../2d/IPoint';
import ILine from '../../2d/ILine';
import Qsei from '../qseis/Qsei';
import Kipou from '../units/Kipou';
import Modify from './Modify';
import ISize from '../../2d/ISize';
import CanvasOption from './CanvasOption';
import Config from '../Config';



const TO_RADIAN = 2 * Math.PI / 360;


interface IModify {
    scale: number;
    point: IPoint;
    modX: number;
    modY: number;
}



export default class Canvas {
    private _id: string;
    private _qsei: Qsei;
    private _kipous: Array<Array<Kipou>>;
    private _option: CanvasOption;

    private static readonly LINE = d3.line()
        .x((d: any) => { return d.x; })
        .y((d: any) => { return d.y; });

    public static readonly POINT_RADIANS = [285, 255, 195, 165, 105, 75, 15, 345];

    public static readonly BAN_TEXT_SRCS = [
        { deg: 270, addX: -0.5, addY: 0.5 },
        { deg: (270 + 180) / 2, addX: -0.5, addY: 0.25 },
        { deg: 180, addX: -0.75, addY: 0.25 },
        { deg: (180 + 90) / 2, addX: -0.5, addY: 0 },
        { deg: 90, addX: -0.5, addY: 0 },
        { deg: (90 + 0) / 2, addX: -0.4, addY: 0 },
        { deg: 0, addX: 0.25, addY: 0.25 },
        { deg: (360 + 270) / 2, addX: -0.4, addY: 0.25 }
    ];

    public static readonly KIPOU_TEXT_SRCS = [
        { deg: 270, modX: Modify.CENTER, modY: Modify.TOP, addX: 0, addY: 0.4 },
        { deg: (270 + 180) / 2, modX: Modify.RIGHT, modY: Modify.TOP, addX: 0.75, addY: -0.5 },
        { deg: 180, modX: Modify.RIGHT, modY: Modify.CENTER, addX: 0, addY: 0.5 },
        { deg: (180 + 90) / 2, modX: Modify.RIGHT, modY: Modify.BOTTTOM, addX: 0.75, addY: 0.75 },
        { deg: 90, modX: Modify.CENTER, modY: Modify.BOTTTOM, addX: 0, addY: 0.1 },
        { deg: (90 + 0) / 2, modX: Modify.LEFT, modY: Modify.BOTTTOM, addX: -0.75, addY: 0.75 },
        { deg: 0, modX: Modify.LEFT, modY: Modify.CENTER, addX: 0, addY: 0.5 },
        { deg: (360 + 270) / 2, modX: Modify.LEFT, modY: Modify.TOP, addX: -0.75, addY: -0.5 }
    ];
    public static readonly HOUI_TEXT_SRCS = [
        { deg: 270, addX: -0.5, addY: 0.5 },
        { deg: 180, addX: -1, addY: 0 },
        { deg: 90, addX: -0.5, addY: 0 },
        { deg: 0, addX: 0, addY: 0 },
    ];

    public static readonly HOUI_TEXTS = ["北", "東", "南", "西"];
    public static readonly QSEI_SRC_POS = { x: 0, y: 0, addX: -0.5, addY: 0.25 };

    public static readonly KIPOU_MAX = 4;
   
    constructor(id: string, qsei: Qsei, kipous: Array<Array<Kipou>>, option: CanvasOption) {
        this._qsei = qsei;
        this._id = id;
        this._kipous = kipous;
        this._option = option;
    }

    set qsei(qsei: Qsei) {
        this._qsei = qsei;
    }

    set option(option: CanvasOption) {
        this._option = option;
    }

    set kipous(kipous: Array<Array<Kipou>>) {
        this._kipous = kipous;
    }



    private static getCharaSize(className: string): ISize {
        let text = d3.select("html")
            .append("text")
            .attr("class", className)
            .text("六")
            ;

        let bb = text.node().getBoundingClientRect();

        text.remove();

        return { width: bb.width, height: bb.height };
    }

    private mySort(values: Array<Kipou>): Array<Kipou> {
        let copy = values.slice();
        copy.sort((a, b) => {
            let alevel = this._option.kipouLevels.get(a.id);
            let blevel = this._option.kipouLevels.get(b.id);
            if (alevel - blevel == 0) {
                //同一レベルだったら    
                return b.type - a.type;
            }
            else {
                return blevel - alevel;
            }
        });

        return copy;
    }

    private getDeleteType(kipous: Array<Kipou>): number {
        if (kipous.length == 0) {
            return Kipou.TYPE_NORMAL;
        }
        let first = kipous[0];
        let firstLevel = this._option.kipouLevels.get(first.id);
        if (firstLevel < 2) {
            //取り消しなし    
            return Kipou.TYPE_NORMAL;
        }
        else {
            let firstType = first.type;
            if (firstType === Kipou.TYPE_KYOU) {
                return Kipou.TYPE_KIPOU;
            }
            else {
                //return Kipou.TYPE_KYOU;
                return Kipou.TYPE_NORMAL;
            }
        }
    }


    private filterKipous(): Array<Array<Kipou>> {
        let result = new Array<Array<Kipou>>();
        this._kipous.forEach((kipous) => {
            let newKipous = kipous.filter((d) => {
                return this._option.kipouEnables.get(d.enableId);
            });

            newKipous = this.mySort(newKipous);

            if (this._option.viewTorikeshi === false) {
                let deleteType = this.getDeleteType(newKipous);
                newKipous = newKipous.filter((d) => {
                    return d.type != deleteType;
                });
            }

            newKipous = newKipous.slice(0, Canvas.KIPOU_MAX);
            result.push(newKipous);
        });
        return result;
    }



    public draw() {
        //ポイント系        
        let sepLines = new Array<ILine>();
        let banPathFill = new Array<Array<IPoint>>();
        let svg = d3.select(`#${this._id}`);
        let node = (<any>svg.node());
        if(node == null)
        {
            return;    
        }
        let windowWidth = node.parentNode.clientWidth;
        let size = {
            width: windowWidth,
            height: windowWidth
        };
        
        svg.attr("width", size.width)
            .attr("height", size.height)
        svg.selectAll('*').remove();

        let outerSize = size.width * 0.28;
        let innerSize = size.width * 0.08;
        let center = { x: size.width / 2, y: size.height / 2 };
        let banTextSize = size.width * 0.15;
        let houiTextSize = outerSize;
        let charaBanSize = Canvas.getCharaSize("ban");
        let charaHouiSize = Canvas.getCharaSize("houi");
        let charaKipouSize = Canvas.getCharaSize("kipou");
        let kipouTextSize = outerSize + 1 * charaHouiSize.height;

        let outerPoints = new Array<IPoint>();
        let innerPoints = new Array<IPoint>();
        Canvas.POINT_RADIANS.forEach((deg) => {
            outerPoints.push({
                x: outerSize * Math.cos(deg * TO_RADIAN) + center.x,
                y: -outerSize * Math.sin(deg * TO_RADIAN) + center.y
            })

            innerPoints.push({
                x: innerSize * Math.cos(deg * TO_RADIAN) + center.x,
                y: -innerSize * Math.sin(deg * TO_RADIAN) + center.y
            })
        });

        for (let i = 0; i < outerPoints.length; i++) {
            let outer = outerPoints[i];
            let inner = innerPoints[i];
            sepLines.push({
                begin: { x: outer.x, y: outer.y },
                end: { x: inner.x, y: inner.y }
            });
        }

        let banTextDests = new Array<IPoint>();
        Canvas.BAN_TEXT_SRCS.forEach((d) => {
            banTextDests.push({
                x: banTextSize * Math.cos(d.deg * TO_RADIAN) + center.x + d.addX * charaBanSize.width,
                y: -banTextSize * Math.sin(d.deg * TO_RADIAN) + center.y + d.addY * charaBanSize.height
            });
        });

        let kipouTextDests = new Array<IModify>();
        Canvas.KIPOU_TEXT_SRCS.forEach((d, i) => {
            kipouTextDests.push({
                scale: (i <= 2 || i >= 6) ? 1.0 : -1.0,
                point: {
                    x: kipouTextSize * Math.cos(d.deg * TO_RADIAN) + center.x + d.addX * charaKipouSize.width,
                    y: -kipouTextSize * Math.sin(d.deg * TO_RADIAN) + center.y + d.addY * charaKipouSize.height,
                },
                modX: d.modX,
                modY: d.modY
            });
        });

        let houiTextDests = new Array<IPoint>();
        Canvas.HOUI_TEXT_SRCS.forEach((d) => {
            houiTextDests.push({
                x: houiTextSize * Math.cos(d.deg * TO_RADIAN) + center.x + d.addX * charaHouiSize.width,
                y: -houiTextSize * Math.sin(d.deg * TO_RADIAN) + center.y + d.addY * charaHouiSize.height
            });
        });

        for (let i = 0; i < outerPoints.length; i++) {
            let begin = outerPoints[i];
            let end = outerPoints[(i + 1) % outerPoints.length];
            banPathFill.push([center, begin, end]);
        }

        let qseiDestPos = {
            x: center.x + Canvas.QSEI_SRC_POS.addX * charaBanSize.width,
            y: center.y + Canvas.QSEI_SRC_POS.addY * charaBanSize.height
        };


        let filterKipous = this.filterKipous();
        banPathFill.forEach((rect, i) => {
            let index = this._option.nanbokuRev ? (i + 4) % 8 : i;
            let kipous = filterKipous[index];
            if (0 < kipous.length) {
                let first = kipous[0];
                let firstLevel = this._option.kipouLevels.get(first.id);
                let className = Config.CLASS_MAP.get(firstLevel);
                svg.append("path")
                    .datum(rect)
                    .attr("class", className)
                    .attr("d", (d: any) => {
                        return <any>Canvas.LINE(d) + "Z";
                    });
            }
        });
        ;


        svg.append("path")
            .datum(outerPoints)
            .attr("class", "border")
            .attr("d", (d: any) => {
                return <any>Canvas.LINE(d) + "Z";
            });
        ;

        svg.append("path")
            .datum(innerPoints)
            .attr("class", "border")
            .attr("d", (d: any) => {
                return <any>Canvas.LINE(d) + "Z";
            });
        ;


        svg.append("g")
            .selectAll("line")
            .data(sepLines)
            .enter()
            .append("line")
            .attr("class", "border")
            .attr("x1", function (d) { return d.begin.x })
            .attr("y1", function (d) { return d.begin.y })
            .attr("x2", function (d) { return d.end.x })
            .attr("y2", function (d) { return d.end.y })
            ;

        svg.append("path")
            .datum(innerPoints)
            .attr("class", `inner ${this._qsei.gogyou.className}`)
            .attr("d", (d: any) => {
                return <any>Canvas.LINE(d) + "Z";
            });
        ;

        svg.append("g")
            .selectAll("text")
            .data(houiTextDests)
            .enter()
            .append("text")
            .attr("class", "houi")
            .attr("x", (d) => { return d.x; })
            .attr("y", (d) => { return d.y; })
            .text((d, i) => {
                if (this._option.nanbokuRev) {
                    return Canvas.HOUI_TEXTS[(i + 2) % 4];
                }
                else {
                    return Canvas.HOUI_TEXTS[i];
                }
            });;



        svg.append("text")
            .datum(qseiDestPos)
            .attr("class", "ban")
            .attr("x", (d) => { return d.x; })
            .attr("y", (d) => { return d.y; })
            .text((d) => { return this._qsei.getHeadName(); })

        svg.append("g")
            .selectAll("text")
            .data(banTextDests)
            .enter()
            .append("text")
            .attr("class", "ban")
            .attr("x", (d) => { return d.x; })
            .attr("y", (d) => { return d.y; })
            .text((_, i) => {
                let index = this._option.nanbokuRev ? (i + 4) % 8 : i;
                return Qsei.of(this._qsei.kiban8[index]).getHeadName();
            })

        kipouTextDests.forEach((point, i) => {
            let group = svg.append("g");
            let index = this._option.nanbokuRev ? (i + 4) % 8 : i;
            let kipous = filterKipous[index];
            let torikesiType = this.getDeleteType(kipous);

            group.selectAll("text")
                .data(kipous)
                .enter()
                .append("text")
                .attr("class", "kipou")
                .attr("y", (d, j) => { return point.point.y + point.scale * j * charaKipouSize.height * 0.8; })
                .attr("x", () => { return point.point.x; })
                .attr("text-decoration", (d) => {
                    return torikesiType == d.type ? "line-through" : "";
                })
                .style("fill", (d) => { return d.fontColor })
                .text((d) => { return d.name; })
                ;

            Modify.modify(group, point.modX, point.modY);
        });
    }
}
