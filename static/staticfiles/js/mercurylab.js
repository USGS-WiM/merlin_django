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
    var objectID = -1;
    for (var index in domDataObject) {
        if (value == domDataObject[index][key]) {
            objectID = domDataObject[index]['id'];
        }
    }
    return objectID;
}
function getValuesDom(domDataObject,attribute) {
    var values = [];
    // var dom_data_object = JSON.parse(grid.attr(domDataObject));
    // var dom_data_object = domDataObject;
    for (var i = 0; i < domDataObject.length; i++) {
        values.push(String(domDataObject[i][attribute]))
    }
    return values;
}
function getValuesAjax(url, arg, query, process, filterParam) {
    var dataParams;
    if (filterParam) {dataParams = filterParam + "&" + arg + "=" + query}
    else {dataParams = arg + "=" + query}
    $.ajax({
        url: url,
        dataType: 'json',
        data: dataParams,
        success: function (response) {
            //console.log("success: getValuesAjax");
            var values = [];
            // check for paginated response
            if ("results" in response) {
                for (var i = 0; i < response.results.length; i++) {
                    values.push(String(response.results[i][arg]));
                }
            }
            else {
                for (var i = 0; i < response.length; i++) {
                    values.push(String(response[i][arg]));
                }
            }
            process(values);
        },
        error: function (response) {
            console.log("ERROR during request by function getValuesAjax to " + url + "?" + arg + "=" + query);
        }
    });
}
function updateValueDom(domDataObject, searchKey, resultKey, searchVal) {
    var returnVal = "";
    for (var i = 0; i < domDataObject.length; i++) {
        if (domDataObject[i][searchKey] == searchVal) {
            returnVal = domDataObject[i][resultKey];
        }
    }
    return returnVal;
}
function updateValueAjax(url, arg, newKey, searchVal, filterParam) {
    var newValue;
    var dataParams;
    if (filterParam) {dataParams = filterParam + "&" + arg + "=" + searchVal}
    else {dataParams = arg + "=" + searchVal}
    $.ajax({
        async: false,
        url: url,
        dataType: 'json',
        data: dataParams,
        success: function (response) {
            //console.log("success: updateValueAjax");
            if ("results" in response) {
                newValue = response['results'][0][newKey];
            }
            else {
                newValue = response[0][newKey];
            }
        },
        error: function (response) {
            console.log("ERROR during request to " + url + "?" + arg + "=" + searchVal + " by function updateValueAjax()");
        }
    });
    return newValue;
}
// this function never really worked
function updateDomDataObjectAjax(url, arg, domDataObject, changedVal) {
    $.ajax({
        url: url,
        dataType: 'json',
        data: arg + "=" + changedVal,
        success: function (response) {
            //console.log("success: updateDomDataObjectAjax");
            // update the local full object collection
            domDataObject = response;
        },
        error: function (response) {
            console.log("ERROR during request by function updateDomDataObjectAjax to " + url + "?" + arg + "=" + changedVal);
        }
    });
}
// this function never really worked
function updateListDom(domDataObject, newKey, changedRow, colToChange) {
    var values = getValuesDom(domDataObject, newKey);
    var cellProperties = grid.handsontable('getInstance').getCellMeta(changedRow, colToChange);
    cellProperties.source = values;
}