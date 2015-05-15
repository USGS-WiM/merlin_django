//https://github.com/knockout/knockout/wiki/Asynchronous-Dependent-Observables
define(["require", "exports"], function (require, exports) {
    // Class
    var Result = (function () {
        // Constructor
        function Result(c, m, u, vFinal, ddl, mp, dt, comment, i, qa, cmethods) {
            var _this = this;
            this.id = -999;
            this.constituent = ko.observable(c).extend({ nullValidation: {} });
            this.method = ko.observable(m).extend({ nullValidation: {} });
            this.reported_value = ko.observable(vFinal).extend({ nullValidation: {} });
            this.isotope_flag = ko.observable(i).extend({ nullValidation: {} });
            this.daily_detection_limit = ko.observable(ddl).extend({ nullValidation: {} });
            this.unit = ko.observable(u).extend({ unitValidation: { method: this.method } });
            this.massProcess = ko.observable(mp).extend({ massProcessValidation: { constituent: this.constituent } });
            this.analyzed_date = ko.observable(dt).extend({ nullValidation: {} });
            this.analysis_comment = ko.observable(comment);
            this.qualityAssuranceList = ko.observableArray(qa);
            this.constituentMethods = ko.observableArray(cmethods);
            //methods for knockout to work with
            this.RemoveQA = function (item) {
                _this.qualityAssuranceList.remove(item);
            };
            this.HasErrors = ko.computed({
                owner: this,
                read: function () {
                    var c = _this.constituent.hasWarning();
                    var m = _this.method.hasWarning();
                    var u = _this.unit.hasWarning();
                    var r = _this.reported_value.hasWarning();
                    var d = _this.daily_detection_limit.hasWarning();
                    var i = _this.isotope_flag.hasWarning();
                    var mp = _this.massProcess.hasWarning();
                    return c || m || u || r || i || mp;
                }
            });
        }
        //Methods
        Result.prototype.ToSimpleResult = function (bottleID) {
            return this.Replacer(bottleID);
        };
        //Helper methods
        Result.prototype.Replacer = function (bottleID) {
            return {
                "bottle_unique_name": bottleID,
                "constituent": this.constituent().constituent,
                "method_id": this.method().id,
                "raw_value": this.reported_value,
                "isotope_flag_id": this.isotope_flag().id,
                "analyzed_date": (this.analyzed_date().getMonth() + 1) + '/' + this.analyzed_date().getDate() + '/' + this.analyzed_date().getFullYear(),
                "daily_detection_limit": this.daily_detection_limit,
                "quality_assurance": $.map(this.qualityAssuranceList(), function (obj) {
                    return obj.quality_assurance;
                }),
                "analysis_comment": this.analysis_comment
            };
        };
        return Result;
    })();
    return Result;
});
//# sourceMappingURL=Result.js.map