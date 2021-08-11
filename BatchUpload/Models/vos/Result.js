//https://github.com/knockout/knockout/wiki/Asynchronous-Dependent-Observables
define(["require", "exports"], function (require, exports) {
    // Class
    var Result = (function () {
        // Constructor
        function Result(c, m, u, vFinal, ddl, pm, mp, dt, comment, i, qa, cmethods) {
            var _this = this;
            this.id = -999;
            this.constituent = ko.observable(c).extend({ nullValidation: {} });
            this.method = ko.observable(m).extend({ nullValidation: {} });
            this.reported_value = ko.observable(vFinal).extend({ nullValidation: {} });
            this.isotope_flag = ko.observable(i).extend({ nullValidation: {} });
            this.daily_detection_limit = ko.observable(ddl).extend({ nullValidation: { msg: "Are you sure you do not want to specify a detection limit?" } });
            this.percent_matching = ko.observable(pm).extend({ nullValidation: {} });
            this.unit = ko.observable(u).extend({ unitValidation: { method: this.method } });
            this.massProcess = ko.observable(mp).extend({ massProcessValidation: { method: this.method } });
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
                    try {
                        var c = _this.constituent.hasWarning();
                        var m = _this.method.hasWarning();
                        var u = _this.unit.hasWarning();
                        var r = _this.reported_value.hasWarning();
                        var i = _this.isotope_flag.hasWarning();
                        var mp = _this.massProcess.hasWarning();
                        var ad = _this.analyzed_date.hasWarning();
                        var pm = _this.percent_matching.hasWarning();
                        return c || m || u || r || i || mp || ad || pm;
                    }
                    catch (e) {
                        return true;
                    }
                }
            });
        }
        //Methods
        Result.prototype.ToSimpleResult = function (bottleID) {
            return this.Replacer(bottleID);
        };
        //Helper methods
        Result.prototype.Replacer = function (bottleID) {
            var result = {
                "bottle_unique_name": bottleID,
                "constituent": this.constituent().constituent,
                "method_id": this.method().id,
                "raw_value": this.reported_value,
                "isotope_flag_id": this.isotope_flag().id,
                "analyzed_date": (this.analyzed_date().getMonth() + 1) + '/' + this.analyzed_date().getDate() + '/' + this.analyzed_date().getFullYear(),
                "daily_detection_limit": this.daily_detection_limit,
                "percent_matching": this.percent_matching,
                "quality_assurance": $.map(this.qualityAssuranceList(), function (obj) {
                    return obj.quality_assurance;
                }),
                "analysis_comment": this.analysis_comment,
                "sample_mass_processed": this.massProcess()
            };
            if (result.sample_mass_processed == null)
                delete result.sample_mass_processed;
            return result;
        };
        return Result;
    })();
    return Result;
});
//# sourceMappingURL=Result.js.map