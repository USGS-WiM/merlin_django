//------------------------------------------------------------------------------
//----- AuthenticationAgent ---------------------------------------------------------------
//------------------------------------------------------------------------------
var __extends = this.__extends || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    __.prototype = b.prototype;
    d.prototype = new __();
};
define(["require", "exports", "./ServiceAgent", "./RequestInfo"], function (require, exports, ServiceAgent, RequestInfo) {
    // Class
    var AuthenticationAgent = (function (_super) {
        __extends(AuthenticationAgent, _super);
        // Constructor
        function AuthenticationAgent(user) {
            _super.call(this, configuration.appSettings['MercuryAuth']);
            this.user = user;
            this.init();
        }
        //Methods
        AuthenticationAgent.prototype.GetTokenAuthentication = function () {
            var json;
            var token = '';
            this.Execute(new RequestInfo("/login", false, "POST", this.user.ToJSON(), "json"), function (x) { return json = x; }, this.HandleOnError);
            token = json.hasOwnProperty("auth_token") ? json["auth_token"] : "";
            return token;
        };
        //Helper Methods
        AuthenticationAgent.prototype.init = function () {
        }; //end init       
        return AuthenticationAgent;
    })(ServiceAgent); //end class
    return AuthenticationAgent;
});
//# sourceMappingURL=AuthenticationAgent.js.map