//represents samplebottles
define(["require", "exports", "../vos/Project", "../vos/Site"], function (require, exports, Project, Site) {
    // Class
    var Sample = (function () {
        // Constructor
        function Sample() {
            this.id = -999;
            this.sample = -999;
            this.bottle = null;
            this.filter_type = -999;
            this.volume_filtered = -999;
            this.preservation_type = -999;
            this.preservation_volume = 999;
            this.preservation_acid = -999;
            this.preservation_comment = '';
            this.project = new Project();
            ;
            this.site = new Site();
            this.depth = -999;
            this.length = -999;
            this.mediumType = '---';
            this.sampling_date = '---';
            this.sampling_time = '---';
            this.Result = ko.observable(null);
        }
        //Methods
        Sample.prototype.LoadSamplingInfo = function (json) {
            this.project.name = json.hasOwnProperty("project_string") ? json["project_string"] : "---";
            this.site.name = json.hasOwnProperty("site_string") ? json["site_string"] : "---";
            this.site.usgs_sid = json.hasOwnProperty("site_usgs_scode") ? json["site_usgs_scode"] : "---";
            this.depth = json.hasOwnProperty("depth") ? json["depth"] : -999;
            this.length = json.hasOwnProperty("length") ? json["length"] : -999;
            this.mediumType = json.hasOwnProperty("medium_type_string") ? json["medium_type_string"] : '---';
            this.sampling_date = json.hasOwnProperty("sample_date") ? json["sample_date"] : '---';
            this.sampling_time = json.hasOwnProperty("sample_time") ? json["sample_time"] : '---';
        };
        Sample.prototype.Deserialize = function (json) {
            try {
                if (json.hasOwnProperty("results"))
                    json = json['results'][0];
                this.id = (json.hasOwnProperty("id")) ? Number(json["id"]) : null;
                this.sample = (json.hasOwnProperty("sample")) ? Number(json["sample"]) : null;
                this.filter_type = (json.hasOwnProperty("filter_type")) ? Number(json["filter_type"]) : null;
                this.volume_filtered = (json.hasOwnProperty("volume_filtered")) ? Number(json["volume_filtered"]) : null;
                this.preservation_type = (json.hasOwnProperty("preservation_type")) ? Number(json["preservation_type"]) : null;
                this.preservation_volume = (json.hasOwnProperty("preservation_volume")) ? Number(json["preservation_volume"]) : null;
                this.preservation_acid = (json.hasOwnProperty("preservation_acid")) ? Number(json["preservation_acid"]) : null;
                this.preservation_comment = (json.hasOwnProperty("preservation_comment")) ? json["preservation_comment"] : "---";
            }
            catch (e) {
            }
            return this;
        };
        return Sample;
    })(); //end class
    return Sample;
});
//# sourceMappingURL=Sample.js.map