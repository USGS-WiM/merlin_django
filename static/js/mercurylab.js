function getRange(limit) {
    var values = [];
    for (var i = 0; i < limit; i++){
        if (i < 10) {
            values.push("0"+String(i));
        }
        else {
            values.push(String(i));
        }
    }
    return values;
}
function getIdDom(domDataObject, key, value) {
    var objectID = 0;
    for (var item in domDataObject) {
        if (value == item[key]) {
            objectID = item['id'];
        }
    }
    return objectID;
}
function getValuesDom(domDataObject,attribute) {
    var values = [];
    // var dom_data_object = JSON.parse(grid.attr(domDataObject));
    // var dom_data_object = domDataObject;
    for (var i = 0; i < domDataObject.length; i++){
        values.push(String(domDataObject[i][attribute]))
    }
    return values;
}
function getValuesAjax(url, arg, query, process) {
    $.ajax({
        url: url,
        dataType: 'json',
        data: arg + "=" + query,
        success: function (response) {
            console.log("success: getValuesAjax");
            var values = [];
            for (var i = 0; i < response.length; i++) {
                values.push(String(response[i][arg]));
            }
            process(values);
        },
        error: function (response) {
            console.log("error: getValuesAjax");
        }
    });
}
function updateValueAjax(url, arg, newKey, changedVal) {
    var newValue;
    $.ajax({
        async: false,
        url: url,
        dataType: 'json',
        data: arg + "=" + changedVal,
        success: function (response) {
            console.log("success: updateValueAjax");
            newValue = response[0][newKey];
        },
        error: function (response) {
            console.log("error: updateValueAjax");
        }
    });
    return newValue;
}
// this function never really worked
function updateDomDataObjectAjax(url, arg, domDataObject, changedValue) {
    $.ajax({
        url: url,
        dataType: 'json',
        data: arg + "=" + changedValue,
        success: function (response) {
            console.log("success: updateDomDataObjectAjax");
            // update the local full object collection
            domDataObject = response;
        },
        error: function (response) {
            console.log("error: updateDomDataObjectAjax");
        }
    });
}
// this function never really worked
function updateListDom(domDataObject, newKey, changedRow, colToChange) {
    var values = getValuesDom(domDataObject, newKey);
    var cellProperties = grid.handsontable('getInstance').getCellMeta(changedRow, colToChange);
    cellProperties.source = values;
}