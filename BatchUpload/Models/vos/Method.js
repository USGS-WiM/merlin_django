define(["require", "exports"], function(require, exports) {
    var Method = (function () {
        // Constructor
        function Method() {
            this.id = -999;
            this.method = "";
            this.method_code = "";
            this.description = "";
            this.preparation = "";
            this.method_detection_limit = -999;
            this.method_detection_limit_unit = -999;
            this.final_value_unit = "";
        }
        //Methods
        Method.prototype.Deserialize = function (json) {
            this.id = json.hasOwnProperty("id") ? Number(json["id"]) : null;
            this.method = json.hasOwnProperty("method") ? json["method"] : null;
            this.method_code = json.hasOwnProperty("id") ? String(json["id"]) : null;
            this.preparation = json.hasOwnProperty("preparation") ? json["preparation"] : null;
            this.description = json.hasOwnProperty("description") ? json["description"] : null;
            this.method_detection_limit = json.hasOwnProperty("method_detection_limit") && json["method_detection_limit"] != null ? Number(json["method_detection_limit"]) : null;
            this.method_detection_limit_unit = json.hasOwnProperty("method_detection_limit_unit") ? Number(json["method_detection_limit_unit"]) : null;
            this.final_value_unit = json.hasOwnProperty("final_value_unit") ? String(json["final_value_unit"]) : null;
            this.displayMethod = "[" + this.method_code + "] " + this.method;
            return this;
        };
        return Method;
    })();

    
    return Method;
});
//# sourceMappingURL=Method.js.map
