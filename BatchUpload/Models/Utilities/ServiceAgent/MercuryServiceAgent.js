//------------------------------------------------------------------------------
//----- MercuryServiceAgent ---------------------------------------------------------------
//------------------------------------------------------------------------------
var __extends = this.__extends || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    __.prototype = b.prototype;
    d.prototype = new __();
};
define(["require", "exports", "../XLSXOps/XLSXReader", "./ServiceAgent", "./RequestInfo", "../../vos/Constituent", "../../vos/IsotopeFlag", "../../vos/QualityAssuranceType", "../../vos/Bottle", "../../vos/Method", "../../vos/Result", "../../vos/UnitType", "../../vos/Sample", "Scripts/events/EventArgs", "Scripts/events/EventHandler", "Scripts/events/Delegate", "../../Messaging/Notification"], function (require, exports, XLSXReader, ServiceAgent, RequestInfo, Constituent, IsotopeFlag, QualityAssurance, Bottle, Method, Result, UnitType, Sample, EventArgs, EventHandler, Delegate, MSG) {
    // Class
    var MercuryServiceAgent = (function (_super) {
        __extends(MercuryServiceAgent, _super);
        // Constructor
        function MercuryServiceAgent(init) {
            if (init === void 0) { init = true; }
            _super.call(this, configuration.appSettings['MercuryService']);
            if (init) {
                this._onLoadComplete = new Delegate();
                this._onSubmitComplete = new Delegate();
                this._onMsg = new Delegate();
                this.init();
            } //end if
        }
        Object.defineProperty(MercuryServiceAgent.prototype, "onLoadComplete", {
            get: function () {
                return this._onLoadComplete;
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(MercuryServiceAgent.prototype, "onSubmitComplete", {
            get: function () {
                return this._onSubmitComplete;
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(MercuryServiceAgent.prototype, "onMsg", {
            get: function () {
                return this._onMsg;
            },
            enumerable: true,
            configurable: true
        });
        //Methods
        MercuryServiceAgent.prototype.LoadWorksheet = function (f) {
            var _this = this;
            var fExtension = "";
            try {
                this.sm("Loading file " + f.name);
                fExtension = f.name.split('.').pop();
                if (fExtension !== 'xlsm' && fExtension !== 'xlsx')
                    throw Error('Invalid file type. File must be xlsm or xlsx');
                var reader = new XLSXReader(f);
                this._onFileLoadedHandler = new EventHandler(function (sender, e) {
                    _this.onFileLoaded(sender, reader);
                });
                reader.onLoadComplete.subscribe(this._onFileLoadedHandler);
                reader.LoadFile();
            }
            catch (e) {
                this.sm(e.message, 3 /* ERROR */, false);
            }
        };
        MercuryServiceAgent.prototype.GetConstituentMethodList = function (c) {
            var _this = this;
            var methodList = [];
            this.Execute(new RequestInfo("/methods/?constituent=" + c, false), function (x) { return _this.HandleOnSerializableComplete(Method, x, methodList); }, this.HandleOnError);
            return methodList;
        };
        MercuryServiceAgent.prototype.SubmitSamples = function (samples) {
            var resultsArray = [];
            for (var i = 0; i < samples.length; i++) {
                var sample = samples[i];
                resultsArray.push(sample.Result().ToSimpleResult(sample.bottle.bottle_unique_name));
            }
            this.Execute(new RequestInfo("/batchupload", true, "POST", ko.toJSON(resultsArray)), this.HandleSubmitComplete, this.HandleOnSubmitError);
        };
        //Helper Methods
        MercuryServiceAgent.prototype.init = function () {
            var _this = this;
            this.ConstituentList = [];
            this.UnitList = [];
            this.SampleList = [];
            this.QualityAssuranceList = [];
            this.IsotopeList = [];
            this.FileValid = false;
            this.Execute(new RequestInfo("/constituents/", true), function (x) { return _this.HandleOnSerializableComplete(Constituent, x, _this.ConstituentList); }, this.HandleOnError);
            this.Execute(new RequestInfo("/isotopeflags/", true), function (x) { return _this.HandleOnSerializableComplete(IsotopeFlag, x, _this.IsotopeList); }, this.HandleOnError);
            this.Execute(new RequestInfo("/units/", true), function (x) { return _this.HandleOnSerializableComplete(UnitType, x, _this.UnitList); }, this.HandleOnError);
            this.Execute(new RequestInfo("/qualityassurancetypes/", true), function (x) { return _this.HandleOnSerializableComplete(QualityAssurance, x, _this.QualityAssuranceList); }, this.HandleOnError);
        }; //end init       
        MercuryServiceAgent.prototype.onFileLoaded = function (reader, e) {
            var _this = this;
            try {
                //unsubscribe from event
                reader.onLoadComplete.unsubscribe(this._onFileLoadedHandler);
                var x = reader.GetData("Results");
                if (x.length <= 0)
                    throw new Error("File is invalid. Select a valid results file.");
                this.sheetDirectory = this.TransformDictionary(x.slice(1, 2)[0]);
                this.sheetResults = x.slice(2);
                this.sheetResults.forEach(function (row) { return _this.getSample(row); });
                this.FileValid = true;
            }
            catch (e) {
                this.sm(e.message, 3 /* ERROR */, false);
            }
            finally {
                delete reader;
                this._onLoadComplete.raise(this, EventArgs.Empty);
            }
        };
        MercuryServiceAgent.prototype.getSample = function (element) {
            var _this = this;
            var sample;
            var bottle;
            var bottleID;
            try {
                bottleID = element.hasOwnProperty(this.sheetDirectory["Bottle ID *"]) ? element[this.sheetDirectory["Bottle ID *"]] : '';
                if (bottleID == '')
                    throw new Error("BottleID is empty");
                //get bottle info
                bottle = new Bottle();
                this.Execute(new RequestInfo("/bottles/?bottle_unique_name=" + bottleID, false), function (x) { return bottle.Deserialize(x); }, this.HandleOnError);
                if (bottle.bottle_prefix_string != null)
                    this.Execute(new RequestInfo("/bottleprefixes/?bottle_prefix=" + bottle.bottle_prefix_string, false), function (x) { return bottle.LoadDeserializePrefix(x); }, this.HandleOnError);
                if (bottle.HasError)
                    throw new Error("Failed to read bottle: " + bottleID + " .... Sample not included.");
                //get sample info
                sample = new Sample();
                this.Execute(new RequestInfo("/samplebottles/?bottle=" + bottle.id), function (x) { return _this.loadSample(sample, x); }, this.HandleOnError);
                sample.bottle = bottle;
                //load result
                sample.Result(this.loadResult(element));
                this.SampleList.push(sample);
            }
            catch (e) {
                this.sm(e.message, 3 /* ERROR */);
                return;
            }
        };
        MercuryServiceAgent.prototype.loadResult = function (element) {
            try {
                var c = element.hasOwnProperty(this.sheetDirectory["Constituent *"]) ? this.getConstituentByName(element[this.sheetDirectory["Constituent *"]]) : null;
                var cmethods = this.GetConstituentMethodList(c.id);
                var m = element.hasOwnProperty(this.sheetDirectory["Method Code *"]) ? this.getMethodByCode(cmethods, String(element[this.sheetDirectory["Method Code *"]])) : null;
                var dt = element.hasOwnProperty(this.sheetDirectory["Date of Analysis *"]) ? this.getExcelDate(Number(element[this.sheetDirectory["Date of Analysis *"]])) : new Date();
                var vFinal = element.hasOwnProperty(this.sheetDirectory["Raw Value *"]) ? Number(element[this.sheetDirectory["Raw Value *"]]) : null;
                var ddl = element.hasOwnProperty(this.sheetDirectory["Detection Limit"]) ? Number(element[this.sheetDirectory["Detection Limit"]]) : null;
                var mp = element.hasOwnProperty(this.sheetDirectory["Sample Mass Process"]) ? Number(element[this.sheetDirectory["Sample Mass Process"]]) : null;
                var comment = element.hasOwnProperty(this.sheetDirectory["Analysis Comments"]) ? String(element[this.sheetDirectory["Analysis Comments"]]) : "";
                var u = element.hasOwnProperty(this.sheetDirectory["Raw Value Units *"]) ? this.getUnitTypeByName(element[this.sheetDirectory["Raw Value Units *"]]) : null;
                var qa = element.hasOwnProperty(this.sheetDirectory["Quality Assurance"]) ? this.getQualityAssuranceList(element[this.sheetDirectory["Quality Assurance"]]) : [];
                ;
                var i = element.hasOwnProperty(this.sheetDirectory["Isotope Flag *"]) ? this.getIsotopeByName(String(element[this.sheetDirectory["Isotope Flag *"]])) : null;
                var result = new Result(c, m, u, vFinal, ddl, mp, dt, comment, i, qa, cmethods);
                return result;
            }
            catch (e) {
                this.sm("Error reading result. " + e.message + ". Check file format", 3 /* ERROR */);
                return null;
            }
        };
        MercuryServiceAgent.prototype.loadSample = function (sample, result) {
            sample.Deserialize(result);
            this.Execute(new RequestInfo("/samples/" + sample.sample + '/'), function (r) { return sample.LoadSamplingInfo(r); }, this.HandleOnError);
        };
        MercuryServiceAgent.prototype.getExcelDate = function (excelDate) {
            // JavaScript dates can be constructed by passing milliseconds
            // since the Unix epoch (January 1, 1970) example: new Date(12312512312);
            // 1. Subtract number of days between Jan 1, 1900 and Jan 1, 1970, plus 1 (Google "excel leap year bug")
            // 2. Convert to milliseconds.
            var d = new Date((excelDate - (25567 + 1)) * 86400 * 1000);
            //d.setHours(0, 0, 0, 0);
            return d;
        };
        MercuryServiceAgent.prototype.getConstituentByName = function (constituentName) {
            for (var i = 0; i < this.ConstituentList.length; i++) {
                var selectedConstituent = this.ConstituentList[i];
                if (selectedConstituent.constituent.trim().toUpperCase() === constituentName.trim().toUpperCase())
                    return selectedConstituent;
            }
            return null;
        };
        MercuryServiceAgent.prototype.getIsotopeByName = function (isotopeName) {
            for (var i = 0; i < this.IsotopeList.length; i++) {
                var selectedIsotope = this.IsotopeList[i];
                if (selectedIsotope.isotope_flag.trim().toUpperCase() === isotopeName.trim().toUpperCase())
                    return selectedIsotope;
            }
            return null;
        };
        MercuryServiceAgent.prototype.getMethodByCode = function (methodList, methodCode) {
            for (var i = 0; i < methodList.length; i++) {
                var selectedMethod = methodList[i];
                if (selectedMethod.method_code.trim().toUpperCase() === methodCode.trim().toUpperCase())
                    return selectedMethod;
            }
            return null;
        };
        MercuryServiceAgent.prototype.getUnitTypeByName = function (unitName) {
            for (var i = 0; i < this.UnitList.length; i++) {
                var selectedUnit = this.UnitList[i];
                if (selectedUnit.unit.trim().toUpperCase() === unitName.trim().toUpperCase())
                    return selectedUnit;
            }
            return null;
        };
        MercuryServiceAgent.prototype.getQualityAssuranceList = function (qaNames) {
            //split by char
            var qaList;
            var qualityAssuranceList = [];
            var qa;
            try {
                qaList = qaNames.split(',');
                for (var i = 0; i < qaList.length; i++) {
                    qa = this.getQAByName(qaList[i]);
                    if (qa != null)
                        qualityAssuranceList.push(qa);
                }
                return qualityAssuranceList;
            }
            catch (e) {
                return [];
            }
        };
        MercuryServiceAgent.prototype.getQAByName = function (QAName) {
            for (var i = 0; i < this.QualityAssuranceList.length; i++) {
                var selectedQA = this.QualityAssuranceList[i];
                if (selectedQA.quality_assurance.trim().toUpperCase() === QAName.trim().toUpperCase())
                    return selectedQA;
            }
            return null;
        };
        MercuryServiceAgent.prototype.HandleSubmitComplete = function (successObj) {
            this.sm("submitting results completed", 1 /* SUCCESS */, false);
            var msg = "";
            var success = false;
            for (var i = 0; i < successObj.length; i++) {
                msg = successObj[i].hasOwnProperty("message") ? successObj[i].message : "";
                success = successObj[i].hasOwnProperty("success") ? Boolean(successObj[i].success) : false;
                this.sm(msg, success ? 1 /* SUCCESS */ : 3 /* ERROR */);
            }
            this.onSubmitComplete.raise(this, EventArgs.Empty);
        };
        MercuryServiceAgent.prototype.HandleOnSubmitError = function (err) {
            this.sm("Failed submitting the results. Error status: " + err.status, 3 /* ERROR */, false);
            this.onSubmitComplete.raise(this, EventArgs.Empty);
        };
        MercuryServiceAgent.prototype.sm = function (msg, notif, toggleAction) {
            if (notif === void 0) { notif = 0; }
            if (toggleAction === void 0) { toggleAction = undefined; }
            this.onMsg.raise(this, new MSG.NotificationArgs(msg, notif, 0.1, toggleAction));
        };
        return MercuryServiceAgent;
    })(ServiceAgent); //end class
    return MercuryServiceAgent;
});
//# sourceMappingURL=MercuryServiceAgent.js.map