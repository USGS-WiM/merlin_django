define(["require", "exports"], function(require, exports) {
    // Class
    var Project = (function () {
        // Constructor
        function Project() {
            this.id = -99;
            this.name = "---";
            this.description = "";
        }
        Project.Deserialize = function (json) {
            try  {
                var p = new Project();
                if (json.hasOwnProperty("results"))
                    json = json['results'][0];

                p.id = json.hasOwnProperty("id") ? Number(json["id"]) : -9999;
                p.name = json.hasOwnProperty("name") ? json["name"] : "---";
                p.description = json.hasOwnProperty("description") ? json["description"] : "---";
                return p;
            } catch (e) {
            }
        };
        return Project;
    })();

    
    return Project;
});
//# sourceMappingURL=Project.js.map
