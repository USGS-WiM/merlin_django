define(["require", "exports"], function (require, exports) {
    var RequestInfo = (function () {
        function RequestInfo(url, isAsync, type, data, dType, doProcess) {
            if (isAsync === void 0) { isAsync = true; }
            if (type === void 0) { type = "GET"; }
            if (data === void 0) { data = null; }
            if (dType === void 0) { dType = "json"; }
            if (doProcess === void 0) { doProcess = false; }
            this.URL = url;
            this.Type = type;
            this.DataType = dType;
            this.ProcessData = doProcess;
            this.IsAsync = isAsync;
            this.Data = data;
        }
        return RequestInfo;
    })();
    return RequestInfo;
});
//# sourceMappingURL=RequestInfo.js.map