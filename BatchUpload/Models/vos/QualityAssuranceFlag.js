define(["require", "exports"], function (require, exports) {
    // Class
    var QualityAssuranceFlag = (function () {
        // Constructor
        function QualityAssuranceFlag() {
            this.id = -999;
            this.quality_assurance_flag = "";
            this.description = "";
        }
        //Methods
        QualityAssuranceFlag.prototype.Deserialize = function (json) {
            this.id = json.hasOwnProperty("id") ? json["id"] : -9999;
            this.quality_assurance_flag = json.hasOwnProperty("quality_assurance_flag") ? json["quality_assurance_flag"] : "";
            this.description = json.hasOwnProperty("description") ? json["description"] : "";
            return this;
        };
        return QualityAssuranceFlag;
    })();
    return QualityAssuranceFlag;
});
//# sourceMappingURL=QualityAssuranceFlag.js.map
