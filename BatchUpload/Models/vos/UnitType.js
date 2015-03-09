define(["require", "exports"], function(require, exports) {
    // Class
    var UnitType = (function () {
        // Constructor
        function UnitType() {
            this.id = -999;
            this.unit = "";
            this.description = "";
        }
        //Methods
        UnitType.prototype.Deserialize = function (json) {
            this.id = json.hasOwnProperty("id") ? json["id"] : -9999;
            this.unit = json.hasOwnProperty("unit") ? json["unit"] : "";
            this.description = json.hasOwnProperty("description") ? json["description"] : "";

            return this;
        };
        return UnitType;
    })();
    
    return UnitType;
});
//# sourceMappingURL=UnitType.js.map
