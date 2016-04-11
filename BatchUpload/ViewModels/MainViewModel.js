//------------------------------------------------------------------------------
//----- MainVM ---------------------------------------------------------------
//------------------------------------------------------------------------------
define(["require", "exports", "Scripts/events/EventHandler", "Models/Utilities/ServiceAgent/MercuryServiceAgent", "Models/Messaging/Notification", "ViewModels/AuthenticationViewModel", "ViewModels/QualityAssuranceViewModel", "Models/Messaging/LogEntry", "knockout", "modernizr"], function (require, exports, EventHandler, MercuryServiceAgent, MSG, AuthenticationVM, QAViewModel, LogEntry) {
    // Class
    var MainViewModel = (function () {
        //Constructor
        //-+-+-+-+-+-+-+-+-+-+-+-
        function MainViewModel() {
            this.init();
            this.sm(new MSG.NotificationArgs("Select a valid mercury template to import"));
        }
        //Methods
        //-+-+-+-+-+-+-+-+-+-+-+-
        MainViewModel.prototype.HandleFileSelect = function (event, data) {
            var _this = this;
            // cancel event and hover styling
            this.HandleDrag(event);
            //take first only
            this.sm(new MSG.NotificationArgs("Loading File.", 0 /* INFORMATION */, 0, true));
            var files = event.target.files || event.originalEvent.dataTransfer.files;
            setTimeout(function () {
                _this.HandleFiles(files);
            }, 1000);
        };
        MainViewModel.prototype.HandleDrag = function (event) {
            event.stopPropagation();
            event.preventDefault();
            //event.target.className = (event.type == "dragover" ? "hover" : "");
        };
        MainViewModel.prototype.HandleFiles = function (files) {
            if (files.length > 0) {
                this.isInit = true;
                this.mAgent.LoadWorksheet(files.item(0));
            }
        };
        MainViewModel.prototype.SetProcedureType = function (pType) {
            if (!this.canUpdateProceedure(pType))
                return;
            this.SelectedProcedure(pType);
            switch (pType) {
                case 3 /* SUBMIT */:
                    this.Authorization.Init();
                    this.Authorization.Login();
            }
        };
        MainViewModel.prototype.SelectSample = function (sample) {
            if (this.SelectedSample() !== sample && this.fileLoaded === true) {
                this.SelectedSample(sample);
            }
        };
        MainViewModel.prototype.SetConstituentMethods = function (r) {
            try {
                if (!r.constituent())
                    throw Error();
                var mAgent = new MercuryServiceAgent(false);
                var c = mAgent.GetConstituentMethodList(r.constituent().id);
                r.constituentMethods(c);
            }
            catch (e) {
                r.constituentMethods([]);
            }
        };
        MainViewModel.prototype.SelectPreviousSample = function () {
            var index = this.SampleList.indexOf(this.SelectedSample()) - 1;
            if (index < 0)
                index = 0;
            this.SelectedSample(this.SampleList()[index]);
        };
        MainViewModel.prototype.SelectNextSample = function () {
            var index = this.SampleList.indexOf(this.SelectedSample()) + 1;
            if (index >= this.SampleList().length)
                index = 0;
            this.SelectedSample(this.SampleList()[index]);
        };
        MainViewModel.prototype.Toggle = function () {
            if (!this.CanToggle())
                return;
            $("#wrapper").toggleClass("toggled");
        };
        //Helper Methods
        //-+-+-+-+-+-+-+-+-+-+-+-
        MainViewModel.prototype.init = function () {
            var _this = this;
            //empty list
            this.fileLoaded = false;
            this.fileValid = false;
            this.SampleList = ko.observableArray([]);
            this.NotificationList = ko.observableArray([]);
            this.ConstituentList = [];
            this.UnitList = [];
            this.IsLoading = ko.observable(false);
            this.Authorization = new AuthenticationVM();
            this.QAViewModel = new QAViewModel();
            this.isInit = false;
            this.CanToggle = ko.observable(false);
            this.SelectedSample = ko.observable(null);
            this.SelectedProcedure = ko.observable(1 /* IMPORT */);
            this.AllowDrop = (Modernizr.draganddrop) ? ko.observable(true) : ko.observable(false);
            this.mAgent = new MercuryServiceAgent();
            this.subscribeToEvents();
            //methods for knockout to work with
            this.ShowQAPopup = function () {
                _this.QAViewModel.Show(true);
            };
            this.AddQAToSelectedSample = function () {
                _this.SelectedSample().Result().qualityAssuranceList.push(_this.QAViewModel.SelectedQualityAssurance());
                _this.QAViewModel.Show(false);
            };
        };
        MainViewModel.prototype.onFileLoaded = function (agent) {
            var _this = this;
            try {
                this.SampleList(agent.SampleList);
                this.ConstituentList = agent.ConstituentList;
                this.UnitList = agent.UnitList;
                this.IsotopeFlagList = agent.IsotopeList;
                this.QAViewModel.QualityAssuranceList(agent.QualityAssuranceList);
                this.fileLoaded = true;
                this.fileValid = agent.FileValid;
                if (this.fileValid) {
                    this._onAuthenticatedHandler = new EventHandler(function (sender) {
                        _this.onAuthenticated(sender);
                    });
                    this.Authorization.onAuthenticated.subscribe(this._onAuthenticatedHandler);
                    this.SetProcedureType(2 /* VALIDATE */);
                    this.CanToggle(true);
                    this.sm(new MSG.NotificationArgs("File successfully loaded", 1 /* SUCCESS */, 0, false));
                    this.sm(new MSG.NotificationArgs("Validate samples, then submit."));
                    this.unSubscribeToEvents();
                }
            }
            finally {
                agent = null;
            }
        };
        MainViewModel.prototype.canUpdateProceedure = function (pType) {
            //Project flow:
            var msg;
            try {
                if (!this.isInit)
                    return;
                switch (pType) {
                    case 1 /* IMPORT */:
                        return !this.fileLoaded || !this.fileValid;
                    case 2 /* VALIDATE */:
                        if (!this.fileLoaded || !this.fileValid)
                            this.sm(new MSG.NotificationArgs("Import a valid lab document", 2 /* WARNING */));
                        return this.fileLoaded && this.fileValid;
                    case 3 /* SUBMIT */:
                        var isOK = this.fileIsOK();
                        if (!this.fileLoaded || !this.fileValid)
                            this.sm(new MSG.NotificationArgs("Import a valid lab document", 2 /* WARNING */));
                        if (!isOK)
                            this.sm(new MSG.NotificationArgs("Samples contains invalid entries. Please fix before submitting", 2 /* WARNING */));
                        return isOK && this.fileLoaded && this.fileValid;
                    case 4 /* LOG */:
                        if (!this.fileLoaded)
                            this.sm(new MSG.NotificationArgs("Import a valid lab document", 2 /* WARNING */));
                        return this.fileLoaded;
                    default:
                        return false;
                }
            }
            catch (e) {
                this.sm(new MSG.NotificationArgs(e.message, 0 /* INFORMATION */, 1.5));
                return false;
            }
        };
        MainViewModel.prototype.fileIsOK = function () {
            try {
                for (var i = 0; i < this.SampleList().length; i++) {
                    if (this.SampleList()[i].Result().HasErrors())
                        return false;
                }
                return true;
            }
            catch (e) {
                return false;
            }
        };
        MainViewModel.prototype.onRecieveMsg = function (sender, e) {
            this.sm(e);
        };
        MainViewModel.prototype.onAuthenticated = function (agent) {
            var token = '';
            try {
                token = agent.AuthenticationString();
                if (token == '' || token == undefined || token == null)
                    throw new Error("Invalid token");
                this.mAgent.SetTokenAuthentication(token);
                this.submitSampleResults();
            }
            catch (e) {
            }
            finally {
                agent = null;
            }
        };
        MainViewModel.prototype.submitSampleResults = function () {
            var _this = this;
            this.sm(new MSG.NotificationArgs("Submitting sample results. Please wait....", 0 /* INFORMATION */, 0, true));
            //subscribe to mAgent.Onsubmit success
            this._onAgentSubmitCompleteHandler = new EventHandler(function (sender) {
                _this.onSubmitComplete(sender);
            });
            this.mAgent.onSubmitComplete.subscribe(this._onAgentSubmitCompleteHandler);
            this.mAgent.SubmitSamples(this.SampleList());
        };
        MainViewModel.prototype.onSubmitComplete = function (sender) {
            var result = this.mAgent;
            this.mAgent.onSubmitComplete.unsubscribe(this._onAgentSubmitCompleteHandler);
        };
        MainViewModel.prototype.subscribeToEvents = function () {
            var _this = this;
            this._onAgentCompleteHandler = new EventHandler(function (sender) {
                _this.onFileLoaded(sender);
            });
            this.mAgent.onLoadComplete.subscribe(this._onAgentCompleteHandler);
            this._onMsgReceivedHandler = new EventHandler(function (sender, e) {
                _this.onRecieveMsg(sender, e);
            });
            this.mAgent.onMsg.subscribe(this._onMsgReceivedHandler);
        };
        MainViewModel.prototype.unSubscribeToEvents = function () {
            this.mAgent.onLoadComplete.unsubscribe(this._onAgentCompleteHandler);
            this._onAgentCompleteHandler = null;
        };
        MainViewModel.prototype.sm = function (msg) {
            var _this = this;
            try {
                toastr.options = {
                    positionClass: "toast-bottom-right"
                };
                this.NotificationList.unshift(new LogEntry(msg.msg, msg.type));
                setTimeout(function () {
                    toastr[msg.type](msg.msg);
                    if (msg.ShowWaitCursor != undefined)
                        _this.IsLoading(msg.ShowWaitCursor);
                }, 0);
            }
            catch (e) {
            }
        };
        return MainViewModel;
    })();
    exports.MainViewModel = MainViewModel; //end class
    (function (ProcedureType) {
        ProcedureType[ProcedureType["IMPORT"] = 1] = "IMPORT";
        ProcedureType[ProcedureType["VALIDATE"] = 2] = "VALIDATE";
        ProcedureType[ProcedureType["SUBMIT"] = 3] = "SUBMIT";
        ProcedureType[ProcedureType["LOG"] = 4] = "LOG";
    })(exports.ProcedureType || (exports.ProcedureType = {}));
    var ProcedureType = exports.ProcedureType;
});
//# sourceMappingURL=MainViewModel.js.map