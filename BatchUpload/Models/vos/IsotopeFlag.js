define(["require", "exports"], function (require, exports) {
    // Class
    var IsotopeFlag = (function () {
        // Constructor
        function IsotopeFlag() {
            this.id = -999;
            this.isotope_flag = "";
            this.description = "";
        }
        //Methods
        IsotopeFlag.prototype.Deserialize = function (json) {
            this.id = json.hasOwnProperty("id") ? json["id"] : -9999;
            this.isotope_flag = json.hasOwnProperty("isotope_flag") ? json["isotope_flag"] : "";
            this.description = json.hasOwnProperty("description") ? json["description"] : "";
            return this;
        };
        return IsotopeFlag;
    })();
    return IsotopeFlag;
});
//# sourceMappingURL=IsotopeFlag.js.map