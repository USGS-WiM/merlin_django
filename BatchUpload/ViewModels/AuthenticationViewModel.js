//------------------------------------------------------------------------------
//----- AuthenticationVM ---------------------------------------------------------------
//------------------------------------------------------------------------------
define(["require", "exports", "Models/vos/User", "Models/Utilities/ServiceAgent/AuthenticationAgent", "Scripts/events/EventArgs", "Scripts/events/Delegate"], function (require, exports, User, AuthenticationAgent, EventArgs, Delegate) {
    // Class
    var AuthenticationViewModel = (function () {
        //Constructor
        //-+-+-+-+-+-+-+-+-+-+-+-
        function AuthenticationViewModel() {
            this.User = new User();
            this.AuthenticationString = ko.observable(null);
            this.ShowLogin = ko.observable(false);
            this.LoginMSG = ko.observable("");
            this.isInitialized = false;
            this._onAuthenicated = new Delegate();
        }
        Object.defineProperty(AuthenticationViewModel.prototype, "onAuthenticated", {
            get: function () {
                return this._onAuthenicated;
            },
            enumerable: true,
            configurable: true
        });
        //Methods
        //-+-+-+-+-+-+-+-+-+-+-+-
        AuthenticationViewModel.prototype.Init = function () {
            this.isInitialized = true;
        };
        AuthenticationViewModel.prototype.Login = function () {
            if (this.isInitialized)
                this.ShowLogin(true);
        };
        AuthenticationViewModel.prototype.AuthenticateUser = function () {
            var aAgent = null;
            var tokn = null;
            try {
                this.LoginMSG("");
                if (this.User.UserName() == null || this.User.Password() == null)
                    return;
                aAgent = new AuthenticationAgent(this.User);
                tokn = aAgent.GetBasicAuthentication();
                if (tokn != undefined && tokn != null && tokn != '') {
                    this.AuthenticationString(tokn);
                    this.ShowLogin(false);
                    this.onAuthenticated.raise(this, EventArgs.Empty);
                }
            }
            catch (e) {
                this.LoginMSG('Authentication failed. Please try again');
            }
            finally {
                this.User.Password(null);
                this.User.UserName(null);
                aAgent = null;
            }
        };
        return AuthenticationViewModel;
    })(); //end class
    return AuthenticationViewModel;
});
//# sourceMappingURL=AuthenticationViewModel.js.map