var handsontable2tab = {
    string: function(instance) {
        var headers = instance.getColHeader();

        //var tab = headers.join("\t") + "\n";
        var tab = "";

        for (var i = 0; i < instance.countRows(); i++) {
            var row = [];
            for (var h in headers) {
                var prop = instance.colToProp(h);
                var value = instance.getDataAtRowProp(i, prop);
                row.push(value)
            }

            tab += row.join("\t");
            tab += "\n";
        }

        return tab;
    },

    download: function(instance, filename) {
        var tab = handsontable2tab.string(instance);

        var link = document.createElement("a");
        link.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(tab));
        link.setAttribute("download", filename);

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link)
    }
};
function convert2dArrayToCsv(arr){
    return arr.reduce(function(csvString, row){
        csvString += row.join(',');
        csvString += ';';
        return csvString;
    }, '');
}
function pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}
var dateRegEx = /^(0[1-9]|1[012]|[1-9])[- /.](0[1-9]|[12][0-9]|3[01]|[1-9])[- /.]\d\d$/;
function makeYear(thisDate) {
    var indexLastSlash = thisDate.lastIndexOf('/');
    var thisYear = thisDate.substring(indexLastSlash+1,thisDate.length);
    if (thisYear.length == 2) {return "20" + thisYear;}
    else {return null;}
}
function makeMonth(thisDate) {
    var indexFirstSlash = thisDate.indexOf('/');
    var thisMonth = thisDate.substring(0,indexFirstSlash);
    if (thisMonth.length == 2) {return thisMonth;}
    else if (thisMonth.length == 1) {return "0" + thisMonth;}
    else {return null;}
}
function makeDay(thisDate) {
    var indexFirstSlash = thisDate.indexOf('/');
    var indexLastSlash = thisDate.lastIndexOf('/');
    var thisDay = thisDate.substring(indexFirstSlash+1, indexLastSlash);
    if (thisDay.length == 2) {return thisDay;}
    else if (thisDay.length == 1) {return "0" + thisDay;}
    else {return null;}
}
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
    var objectID = null;
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
    var newValue = "";
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
                if (response['count'] != 1) {
                    newValue = "";
                }
                else {
                    newValue = response['results'][0][newKey];
                }
            }
            else {
                if (response.length != 1) {
                    newValue = "";
                }
                else {
                    newValue = response[0][newKey];
                }
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
