define(["require", "exports"], function(require, exports) {
    var RequestInfo = (function () {
        function RequestInfo(url, isAsync, type, data, dType, doProcess) {
            if (typeof isAsync === "undefined") { isAsync = true; }
            if (typeof type === "undefined") { type = "GET"; }
            if (typeof data === "undefined") { data = null; }
            if (typeof dType === "undefined") { dType = "json"; }
            if (typeof doProcess === "undefined") { doProcess = false; }
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
