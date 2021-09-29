//------------------------------------------------------------------------------
//----- QualityAssuranceFlagViewModel -----------------------------------------
//------------------------------------------------------------------------------
define(["require", "exports"], function (require, exports) {
    //-------1---------2---------3---------4---------5---------6---------7---------8
    //       01234567890123456789012345678901234567890123456789012345678901234567890
    //-------+---------+---------+---------+---------+---------+---------+---------+
    // copyright:   2015 WiM - USGS
    //    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
    //   purpose:  
    //discussion:   This is where the majority of your code-behind goes: data access, click events, complex calculations, 
    //              business rules validation, etc. ViewModels are typically built to reflect a View. 
    //              For example, if a View contains a ListBox of objects, a Selected object, and a Save button, the ViewModel will have an ObservableCollection ObectList, 
    //              Model SelectedObject, and SaveCommand.
    //Comments
    //03.6.2015 jkn - Created
    //Imports"
    // Class
    var QualityAssuranceFlagViewModel = (function () {
        //Constructor
        //-+-+-+-+-+-+-+-+-+-+-+-
        function QualityAssuranceFlagViewModel() {
            this.Show = ko.observable(false);
            this.QualityAssuranceFlagList = ko.observableArray([]);
            this.SelectedQualityAssuranceFlag = ko.observable(null);
        }
        return QualityAssuranceFlagViewModel;
    })(); //end class
    return QualityAssuranceFlagViewModel;
});
//# sourceMappingURL=QualityAssuranceFlagViewModel.js.map
