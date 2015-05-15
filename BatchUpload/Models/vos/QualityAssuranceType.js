define(["require", "exports"], function (require, exports) {
    // Class
    var QualityAssuranceType = (function () {
        // Constructor
        function QualityAssuranceType() {
            this.id = -999;
            this.quality_assurance = "";
            this.description = "";
        }
        //Methods
        QualityAssuranceType.prototype.Deserialize = function (json) {
            this.id = json.hasOwnProperty("id") ? json["id"] : -9999;
            this.quality_assurance = json.hasOwnProperty("quality_assurance") ? json["quality_assurance"] : "";
            this.description = json.hasOwnProperty("description") ? json["description"] : "";
            return this;
        };
        return QualityAssuranceType;
    })();
    return QualityAssuranceType;
});
//# sourceMappingURL=QualityAssuranceType.js.map