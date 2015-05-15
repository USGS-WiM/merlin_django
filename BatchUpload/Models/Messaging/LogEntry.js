define(["require", "exports"], function (require, exports) {
    // Class
    var LogEntry = (function () {
        // Constructor
        function LogEntry(msg, t) {
            this.dateTime = new Date();
            this.message = msg;
            this.type = t;
            this.displayedMSG = this.dateTime.toLocaleString() + " " + this.type + " " + this.message;
        }
        return LogEntry;
    })();
    return LogEntry;
});
//# sourceMappingURL=LogEntry.js.map