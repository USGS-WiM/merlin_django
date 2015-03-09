define(["require", "exports"], function(require, exports) {
    // Class
    var Bottle = (function () {
        // Constructor
        function Bottle() {
            this.id = -99;
            this.bottle_unique_name = "---";
            this.created_date = "---";
            this.description = "";
            this.tare_weight = -99;
            this.bottle_type = -999;
            this.bottle_prefix = null;
            this.HasError = true;
        }
        Bottle.prototype.LoadDeserializePrefix = function (json) {
            try  {
                if (json.hasOwnProperty("results"))
                    json = json['results'][0];
                this.tare_weight = json.hasOwnProperty("tare_weight") ? json["tare_weight"] : -999;
                this.bottle_type = json.hasOwnProperty("bottle_type") ? json["bottle_type"] : -999;
            } catch (e) {
                this.HasError = true;
            }
        };
        Bottle.prototype.Deserialize = function (json) {
            try  {
                if (json.hasOwnProperty("results"))
                    json = json['results'];
                if (json.length > 1)
                    throw new Error();
                json = json[0];
                this.id = json.hasOwnProperty("id") ? json["id"] : -9999;
                this.bottle_unique_name = json.hasOwnProperty("bottle_unique_name") ? json["bottle_unique_name"] : "---";
                this.bottle_prefix = json.hasOwnProperty("bottle_prefix") ? json["bottle_prefix"] : null;
                this.description = json.hasOwnProperty("description") ? json["description"] : "---";
                this.created_date = json.hasOwnProperty("created_date") ? json["created_date"] : "---";
                this.HasError = false;
                return this;
            } catch (e) {
                this.HasError = true;
            }
        };
        return Bottle;
    })();

    
    return Bottle;
});
//# sourceMappingURL=Bottle.js.map
