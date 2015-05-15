define(["require", "exports"], function (require, exports) {
    var EventArgs = (function () {
        function EventArgs() {
        }
        Object.defineProperty(EventArgs, "Empty", {
            get: function () {
                return new EventArgs();
            },
            enumerable: true,
            configurable: true
        });
        return EventArgs;
    })();
    return EventArgs;
});
//# sourceMappingURL=EventArgs.js.map