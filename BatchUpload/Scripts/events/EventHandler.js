define(["require", "exports"], function(require, exports) {
    var EventHandler = (function () {
        function EventHandler(handler) {
            this._handler = handler;
        }
        EventHandler.prototype.handle = function (sender, e) {
            this._handler(sender, e);
        };
        return EventHandler;
    })();

    
    return EventHandler;
});
//# sourceMappingURL=EventHandler.js.map
