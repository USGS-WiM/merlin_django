define(["require", "exports"], function(require, exports) {
    // Class
    var Site = (function () {
        // Constructor
        function Site() {
            this.id = -99;
            this.name = "---";
            this.usgs_sid = "";
            this.description = "";
            this.latitude = NaN;
            this.longitude = NaN;
        }
        Site.Deserialize = function (json) {
            try  {
                if (json.hasOwnProperty("results"))
                    json = json['results'][0];

                var s = new Site();
                s.id = json.hasOwnProperty("id") ? json["id"] : -9999;
                s.name = json.hasOwnProperty("name") ? json["name"] : "---";
                s.usgs_sid = json.hasOwnProperty("usgs_sid") ? json["usgs_sid"] : "";
                s.description = json.hasOwnProperty("description") ? json["description"] : "---";
                s.latitude = json.hasOwnProperty("latitude") ? json["latitude"] : NaN;
                s.longitude = json.hasOwnProperty("longitude") ? json["longitude"] : NaN;
                return s;
            } catch (e) {
                return null;
            }
        };
        return Site;
    })();

    
    return Site;
});
//# sourceMappingURL=Site.js.map
