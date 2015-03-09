//------------------------------------------------------------------------------
//----- XLSXReader--------------------------------------------------------------
//------------------------------------------------------------------------------
define(["require", "exports", "Scripts/events/Delegate", "Scripts/events/EventArgs"], function(require, exports, Delegate, EventArgs) {
    // Class
    var XLSXReader = (function () {
        // Constructor
        function XLSXReader(file) {
            this._onLoadComplete = new Delegate();
            this.File = file;
        }
        Object.defineProperty(XLSXReader.prototype, "onLoadComplete", {
            get: function () {
                return this._onLoadComplete;
            },
            enumerable: true,
            configurable: true
        });

        // Methods
        XLSXReader.prototype.LoadFile = function () {
            var _this = this;
            var reader = new FileReader();
            var name = this.File.name;
            reader.onload = function (event) {
                return _this.readerOnload(event);
            };
            reader.readAsArrayBuffer(this.File);
        };

        XLSXReader.prototype.GetData = function (SheetName) {
            var results = [];
            var currentRow = 0;
            var thisRow = 0;
            var index = -1;

            var data = this.WorkBook.Sheets.hasOwnProperty(SheetName) ? this.WorkBook.Sheets[SheetName] : null;

            if (!data)
                return results;

            for (var z in data) {
                if (z[0] === '!')
                    continue;
                thisRow = Number(z.match(/[0-9]+/)[0]);

                if (currentRow != thisRow) {
                    index++;
                    currentRow = thisRow;
                    results.push({});
                }

                results[index][z.match(/[A-Za-z]/)[0]] = (data[z].v);
            }

            return results;
        };

        //Helper Methods
        XLSXReader.prototype.readerOnload = function (e) {
            var data = e.target.result;

            this.WorkBook = XLSX.read(data, { type: 'binary' });
            this.Worksheets = this.WorkBook.SheetNames;

            this._onLoadComplete.raise(this, EventArgs.Empty);
        };
        XLSXReader.prototype.GetWorksheetIndex = function (itemSelected) {
            if (!itemSelected)
                return -1;
            var count = 0;
            for (var worksheet in this.WorkBook.Sheets) {
                count++;
                if (worksheet === itemSelected)
                    return count;
            }
            return -1;
        };
        return XLSXReader;
    })();

    
    return XLSXReader;
});
//# sourceMappingURL=XLSXReader.js.map
