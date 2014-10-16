$(document).ready(function() {

    var $container = $('#grid');
    $container.handsontable({
        rowHeaders: true,
        colHeaders: true,
        colWidths: [40,120,120,120,120,120,120,120,40,80,60,120],
        minSpareRows: 1,
        contextMenu: true,
        columnSorting: { column: 0 }/*,
        beforeRender: function () {
            $container.hide();
        },
        afterChange: function (changes, source) {
            $container.show();
        }*/
    });

    function getCooperator(){
        var pk = $container.attr("data-pk");
        $.ajax({
            url: '/mercurylab/cooperators/'+pk,
            dataType: 'json',
            type: 'GET',
            success: function (res) {
               $container.data('handsontable').loadData(res);
               $("#console").text('Data loaded');
               //$container.show();  // this, combined with duplicate call in the grid's afterChange callback, is the only way I could get this to work without first rendering an empty 5x5 grid
            }
        });
    }

    getCooperator();

});


/*
    var data = [
        ["", "Kia", "Nissan", "Toyota", "Honda"],
        ["2008", 10, 11, 12, 13],
        ["2009", 20, 11, 14, 13],
        ["2010", 30, 15, 12, 13]
    ];
    $("#dataTable").handsontable({
        data: data,
        startRows: 6,
        startCols: 8
    });
*/

/*
    var $container = $("#grid");
    var $console = $("#console");
    var $parent = $container.parent();
    var autosaveNotification;
    $container.handsontable({
        startRows: 8,
        startCols: 6,
        rowHeaders: true,
        colHeaders: true,
        minSpareRows: 1,
        contextMenu: true,
        columnSorting: true,
        afterChange: function (change, source) {
            if (source === 'loadData') {
                return; //don't save this change
            }
            if ($parent.find('input[name=autosave]').is(':checked')) {
                clearTimeout(autosaveNotification);
                $.ajax({
                    url: "json/save.json",
                    dataType: "json",
                    type: "POST",
                    data: JSON.stringify({data: change}), //contains changed cells' data
                    complete: function (data) {
                        $console.text('Autosaved (' + change.length + ' ' +
                            'cell' + (change.length > 1 ? 's' : '') + ')');
                        autosaveNotification = setTimeout(function () {
                            $console.text('Changes will be autosaved');
                        }, 1000);
                    }
                });
            }
        }
    });
    var handsontable = $container.data('handsontable');

    $parent.find('button[name=load]').click(function () {
        $.ajax({
            //url: '/static/json/load.json',
            url: '/mercuryservices/cooperators',
            dataType: 'json',
            type: 'GET',
            success: function (res) {
                handsontable.loadData(res);
                $console.text('Data loaded');
            }
        });
    });

    $parent.find('button[name=save]').click(function () {
        $.ajax({
            url: "json/save.json",
            data: JSON.stringify({"data": handsontable.getData()}), //returns all cells' data
            dataType: 'json',
            type: 'POST',
            success: function (res) {
                if (res.result === 'ok') {
                    $console.text('Data saved');
                }
                else {
                    $console.text('Save error');
                }
            },
            error: function () {
                $console.text('Save error. POST method is not enabled yet.');
            }
        });
    });

    $parent.find('input[name=autosave]').click(function () {
        if ($(this).is(':checked')) {
            $console.text('Changes will be autosaved');
        }
        else {
            $console.text('Changes will not be autosaved');
        }
    });
*/