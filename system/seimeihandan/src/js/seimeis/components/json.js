


JSON.parseWithDate = function(str){
    function reviver(key, val){
        if (typeof(val) == "string" &&
            val.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/)){
            return new Date(Date.parse(val));
        }
        return val;
    }
    return JSON.parse(str, reviver);
};