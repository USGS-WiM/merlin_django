define(["require", "exports"], function(require, exports) {
    // Class
    var User = (function () {
        // Constructor
        function User() {
            this.UserName = ko.observable(null).extend({ validUserName: {} });
            this.Password = ko.observable(null).extend({ validPassword: {} });
        }
        User.prototype.ToJSON = function () {
            return ko.toJSON(this.Replacer());
        };

        //Helper methods
        User.prototype.Replacer = function () {
            return {
                "username": this.UserName,
                "password": this.Password
            };
        };
        return User;
    })();

    
    return User;
});
//# sourceMappingURL=User.js.map
