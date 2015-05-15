//------------------------------------------------------------------------------
//----- QualityAssuranceViewModel -----------------------------------------
//------------------------------------------------------------------------------
define(["require", "exports"], function (require, exports) {
    //-------1---------2---------3---------4---------5---------6---------7---------8
    //       01234567890123456789012345678901234567890123456789012345678901234567890
    //-------+---------+---------+---------+---------+---------+---------+---------+
    // copyright:   2015 WiM - USGS
    //    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
    //   purpose:  
    //discussion:   This is where the majority of your code-behind goes: data access, click events, complex calculations, 
    //              business rules validation, etc. ViewModels are typically built to reflect a View. 
    //              For example, if a View contains a ListBox of objects, a Selected object, and a Save button, the ViewModel will have an ObservableCollection ObectList, 
    //              Model SelectedObject, and SaveCommand.
    //Comments
    //03.6.2015 jkn - Created
    //Imports"
    // Class
    var QualityAssuranceViewModel = (function () {
        //Constructor
        //-+-+-+-+-+-+-+-+-+-+-+-
        function QualityAssuranceViewModel() {
            this.Show = ko.observable(false);
            this.QualityAssuranceList = ko.observableArray([]);
            this.SelectedQualityAssurance = ko.observable(null);
        }
        return QualityAssuranceViewModel;
    })(); //end class
    return QualityAssuranceViewModel;
});
//# sourceMappingURL=QualityAssuranceViewModel.js.map