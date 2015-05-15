define(["require", "exports"], function (require, exports) {
    // Class
    var ServiceAgent = (function () {
        // Constructor
        function ServiceAgent(urlbase) {
            this.BaseURL = urlbase;
        }
        //Method
        ServiceAgent.prototype.Execute = function (request, callBackOnSuccess, callBackOnFail) {
            //loads the referance stations from NWIS
            var _this = this;
            $.ajax({
                context: this,
                type: request.Type,
                contentType: "application/json",
                data: request.Data,
                url: this.BaseURL + request.URL,
                processData: request.ProcessData,
                dataType: request.DataType,
                beforeSend: function (xhr) {
                    if (_this.authentication)
                        xhr.setRequestHeader('authorization', _this.authentication);
                },
                async: request.IsAsync,
                success: callBackOnSuccess,
                error: callBackOnFail
            });
        };
        ServiceAgent.prototype.SetTokenAuthentication = function (token) {
            this.authentication = "token " + token;
        };
        ServiceAgent.prototype.TransformDictionary = function (item) {
            var dictionary = {};
            for (var key in item) {
                dictionary[item[key]] = key;
            }
            return dictionary;
        };
        ServiceAgent.prototype.HandleOnSerializableComplete = function (type, list, container) {
            list.forEach(function (l) { return container.push(new type().Deserialize(l)); });
        };
        ServiceAgent.prototype.HandleOnError = function (err) {
            //do something
            console.log(err);
        };
        return ServiceAgent;
    })();
    return ServiceAgent;
});
//# sourceMappingURL=ServiceAgent.js.map