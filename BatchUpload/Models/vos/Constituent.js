define(["require", "exports"], function (require, exports) {
    // Class
    var Constituent = (function () {
        // Constructor
        function Constituent() {
            this.id = -999;
            this.constituent = "";
            this.description = "";
        }
        //Methods
        Constituent.prototype.Deserialize = function (json) {
            this.id = json.hasOwnProperty("id") ? json["id"] : -9999;
            this.constituent = json.hasOwnProperty("constituent") ? json["constituent"] : "";
            this.description = json.hasOwnProperty("description") ? json["description"] : "";
            return this;
        };
        return Constituent;
    })();
    return Constituent;
});
//# sourceMappingURL=Constituent.js.map