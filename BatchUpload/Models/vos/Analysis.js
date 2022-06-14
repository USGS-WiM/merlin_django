define(["require", "exports"], function (require, exports) {
    // Class
    var Analysis = (function () {
        // Constructor
        function Analysis() {
            this.id = -999;
            this.analysis = "";
            this.description = "";
        }
        //Methods
        Analysis.prototype.Deserialize = function (json) {
            this.id = json.hasOwnProperty("id") ? json["id"] : -9999;
            this.analysis = json.hasOwnProperty("analysis") ? json["analysis"] : "";
            this.description = json.hasOwnProperty("description") ? json["description"] : "";
            return this;
        };
        return Analysis;
    })();
    return Analysis;
});
//# sourceMappingURL=Analysis.js.map
