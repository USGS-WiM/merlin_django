//------------------------------------------------------------------------------
//----- Notification ---------------------------------------------------------------
//------------------------------------------------------------------------------
define(["require", "exports"], function(require, exports) {
    //-------1---------2---------3---------4---------5---------6---------7---------8
    //       01234567890123456789012345678901234567890123456789012345678901234567890
    //-------+---------+---------+---------+---------+---------+---------+---------+
    // copyright:   2015 WiM - USGS
    //    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
    //
    //
    //   purpose:  Represents the Message
    //
    //discussion:
    //
    //Comments
    //08.14.2014 jkn - Created
    //10.01.2014 jkn - changed to notification and added notification properties
    //Imports"
    // Class
    var NotificationArgs = (function () {
        //Constructor
        function NotificationArgs(m, t, waitLevel, toggleAction) {
            if (typeof t === "undefined") { t = 0; }
            if (typeof waitLevel === "undefined") { waitLevel = 1; }
            if (typeof toggleAction === "undefined") { toggleAction = undefined; }
            this.msg = m;
            this.type = (t != null) ? this.getNotificationString(t) : 'info';
            this.dismissTime = (waitLevel < 0.2 || waitLevel == null) ? 10000 : waitLevel * 10000;
            this.ShowWaitCursor = (toggleAction != undefined) ? toggleAction : undefined;
        }
        NotificationArgs.MessageEventArgs = function (m, t, waitLevel, toggleAction) {
            if (typeof t === "undefined") { t = 0; }
            if (typeof waitLevel === "undefined") { waitLevel = 1; }
            if (typeof toggleAction === "undefined") { toggleAction = undefined; }
            return new NotificationArgs(m, t, waitLevel, toggleAction);
        };

        //Helper methods
        NotificationArgs.prototype.getNotificationString = function (n) {
            switch (n) {
                case 1 /* SUCCESS */:
                    return "success";
                case 3 /* ERROR */:
                    return "error";
                case 2 /* WARNING */:
                    return "warning";
                case 0 /* INFORMATION */:
                    return "info";
            }
        };
        return NotificationArgs;
    })();
    exports.NotificationArgs = NotificationArgs;
    (function (NotificationType) {
        NotificationType[NotificationType["INFORMATION"] = 0] = "INFORMATION";
        NotificationType[NotificationType["SUCCESS"] = 1] = "SUCCESS";
        NotificationType[NotificationType["WARNING"] = 2] = "WARNING";
        NotificationType[NotificationType["ERROR"] = 3] = "ERROR";
    })(exports.NotificationType || (exports.NotificationType = {}));
    var NotificationType = exports.NotificationType;
});
//# sourceMappingURL=Notification.js.map
