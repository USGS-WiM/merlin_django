///<reference path="Scripts/typings/requirejs/require.d.ts" />
///<reference path="Scripts/typings/knockout/knockout.d.ts" />
///<reference path="Scripts/typings/knockout/myknockout.d.ts" />
require.config({
    // Base URL for scripts is the 'js' folder
    baseUrl: "",
    /*
    * You can specify 'fallback' paths for external dependencies, in case
    * they fail to load (i.e. you're developing and don't have internet).
    *
    * http://requirejs.org/docs/api.html#pathsfallbacks
    */
    paths: {
        'jquery': "Scripts/jquery-2.1.1",
        'knockout': "Scripts/knockout-3.2.0",
        'modernizr': "Scripts/modernizr-2.8.3",
        'bootstrap': "Scripts/bootstrap",
        'knockstrap': "Scripts/knockstrap",
        'datepicker': "Scripts/bootstrap-datepicker",
        //messaging
        'toastr': "Scripts/toastr",
        'MainViewModel': "ViewModels/MainViewModel"
    },
    shim: {
        'jquery': {
            exports: '$'
        },
        'toastr': {
            exports: 'toastr'
        },
        'bootstrap': {
            deps: ["jquery"]
        },
        'datepicker': {
            deps: ["bootstrap"]
        },
        'knockout': {
            deps: ["jquery"],
            exports: 'ko'
        },
        'MainViewModel': { deps: ['knockout'] }
    }
});
define([
    'knockout',
    'MainViewModel', 'toastr', 'bootstrap', 'datepicker'], function (koo, vm, toastr) {
    window.ko = koo;
    window.toastr = toastr;

    ko.extenders.nullValidation = function (target, option) {
        //add some sub-observables to our observable
        target.hasWarning = ko.observable();
        target.validationMessage = ko.observable();

        //define a function to do validation
        function validate(value, param) {
            var warn = false;
            var msg = '';
            if (value === null || value === '') {
                warn = true;
                msg = "Item Cannot be null";
                toastr.error(msg);
            }

            target.hasWarning(warn);
            target.validationMessage(msg);
        }

        //initial validation
        validate(target(), option);

        //validate whenever the value changes
        target.subscribe(validate);

        //return the original observable
        return target;
    };
    ko.extenders.validUserName = function (target, option) {
        //add some sub-observables to our observable
        target.IsValid = ko.observable();

        //define a function to do validation
        function validate(value, param) {
            var warn = true;
            if (value == null || value == '') {
                warn = false;
            }

            target.IsValid(warn);
        }

        //initial validation
        validate(target(), option);

        //validate whenever the value changes
        target.subscribe(validate);

        //return the original observable
        return target;
    };
    ko.extenders.validPassword = function (target, option) {
        //add some sub-observables to our observable
        target.IsValid = ko.observable();

        //define a function to do validation
        function validate(value, param) {
            var warn = true;
            if (value == null || value == '') {
                warn = false;
            }
            target.IsValid(warn);
        }

        //initial validation
        validate(target(), option);

        //validate whenever the value changes
        target.subscribe(validate);

        //return the original observable
        return target;
    };
    ko.extenders.detectionLimitValidation = function (target, option) {
        //add some sub-observables to our observable
        target.hasWarning = ko.observable();
        target.validationMessage = ko.observable();
        target.Method = option.method;
        target.value = option.value;

        //define a function to do validation
        function validate() {
            var warn = false;
            var msg = '';
            if (target.Method() == null) {
                warn = true;
                msg = "Warning: Choose a method";
            } else {
                var detectionFlag = '';
                if (target() < target.Method().method_detection_limit)
                    detectionFlag = '<';
                else if (target.detection_limit < target() && target.value() > target.Method().method_detection_limit)
                    detectionFlag = 'e';
                else
                    detectionFlag = 'none';
                warn = true;
                msg = "Detection limit flag: " + detectionFlag;
            }

            target.hasWarning(warn);
            target.validationMessage(msg);
        }

        //initial validation
        validate();

        //validate whenever the value changes
        target.subscribe(validate);
        target.Method.subscribe(validate);
        target.value.subscribe(validate);

        //return the original observable
        return target;
    };
    ko.extenders.unitValidation = function (target, option) {
        //add some sub-observables to our observable
        target.hasWarning = ko.observable();
        target.validationMessage = ko.observable();
        target.Method = option.method;

        //define a function to do validation
        function validate() {
            var warn = false;
            var msg = '';
            if (target.Method() == null) {
                warn = true;
                msg = "Warning: Choose a method";
            } else if (target() == null) {
                warn = true;
                msg = "Item Cannot be null";
            } else {
                var detectionFlag = '';

                if (target().unit !== target.Method().final_value_unit) {
                    warn = true;
                    msg = "Unit does not match method unit: " + target.Method().final_value_unit;
                }
            }

            target.hasWarning(warn);
            target.validationMessage(msg);
        }

        //initial validation
        validate();

        //validate whenever the value changes
        target.subscribe(validate);
        target.Method.subscribe(validate);

        //return the original observable
        return target;
    };

    ko.bindingHandlers.fadeVisible = {
        init: function (element, valueAccessor) {
            // Initially set the element to be instantly visible/hidden depending on the value
            var value = valueAccessor();
            $(element).toggle(ko.unwrap(value)); // Use "unwrapObservable" so we can handle values that may or may not be observable
        },
        update: function (element, valueAccessor) {
            // Whenever the value subsequently changes, slowly fade the element in or out
            var value = valueAccessor();
            ko.unwrap(value) ? $(element).fadeIn() : $(element).fadeOut();
        }
    };
    ko.bindingHandlers.numeric = {
        init: function (element) {
            $(element).on("keydown", function (event) {
                // Allow: backspace, delete, tab, escape, and enter
                if (event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 9 || event.keyCode == 27 || event.keyCode == 13 || (event.keyCode == 65 && event.ctrlKey === true) || (event.keyCode == 188 || event.keyCode == 190 || event.keyCode == 110) || (event.keyCode >= 35 && event.keyCode <= 39)) {
                    // let it happen, don't do anything
                    return;
                } else {
                    // Ensure that it is a number and stop the keypress
                    if (event.shiftKey || (event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105)) {
                        event.preventDefault();
                    }
                }
            });
        }
    };
    ko.bindingHandlers.loading = {
        update: function (element, valueAccessor, allBindingsAccessor) {
            var value = valueAccessor(), allBindings = allBindingsAccessor();
            var valueUnwrapped = ko.utils.unwrapObservable(value);

            if (valueUnwrapped == true)
                $(element).show(); // Make the element visible
            else
                $(element).hide(); // Make the element invisible
        }
    };
    ko.bindingHandlers.modal = {
        init: function (element, valueAccessor) {
            $(element).modal({
                backdrop: 'static',
                show: false
            });

            var value = valueAccessor();
            if (typeof value === 'function') {
                $(element).on('hidden.bs.modal', function () {
                    value(false);
                });
            }
            ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                $(element).modal("destroy");
            });
        },
        update: function (element, valueAccessor) {
            var value = valueAccessor();
            if (ko.utils.unwrapObservable(value)) {
                $(element).modal('show');
            } else {
                $(element).modal('hide');
            }
        }
    };
    ko.bindingHandlers.datepicker = {
        init: function (element, valueAccessor, allBindingsAccessor) {
            var $el = $(element);

            //initialize datepicker with some optional options
            var options = allBindingsAccessor().datepickerOptions || {};
            $el.datepicker(options);

            //handle the field changing
            ko.utils.registerEventHandler(element, "change", function () {
                var observable = valueAccessor();
                observable($el.datepicker("getDate"));
            });

            //handle disposal (if KO removes by the template binding)
            ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                $el.datepicker("remove");
            });
        },
        update: function (element, valueAccessor) {
            var value = ko.utils.unwrapObservable(valueAccessor());

            //handle date data coming via json from Microsoft
            if (String(value).indexOf('/Date(') == 0) {
                value = new Date(parseInt(value.replace(/\/Date\((.*?)\)\//gi, "$1")));
            }

            var current = $(element).datepicker("getDate");

            if (value - current !== 0) {
                $(element).datepicker("setDate", value);
            }
        }
    };

    // Viewmodel applybindings
    var viewmodel = new vm.MainViewModel();
    ko.applyBindings(viewmodel);

    //Navigate list on shift + up/down keystroke
    $(window).keyup(function (evt) {
        if (evt.shiftKey && evt.keyCode == 38) {
            viewmodel.SelectPreviousSample();
        } else if (evt.shiftKey && evt.keyCode == 40) {
            viewmodel.SelectNextSample();
        }
    });

    //show page after load complete
    $(document).ready(function () {
        $('#MainApp').show();
    });
});
//# sourceMappingURL=configuration.js.map
