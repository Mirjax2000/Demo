(function () {

    console.log("modules.js loaded");

    const orderTable = document.getElementById("orderTable");
    const teamTable = document.getElementById("teamTable");
    const clientOrderTable = document.getElementById("clientOrderTable");

    // DataTable for orders
    if (orderTable) {
        $(orderTable).DataTable({
            // zapiname server side proccesing
            processing: true,
            serverSide: true,
            // ajax mi posle do requestu json s pozadavky na strankovani
            // odpoved bude qs s aplikovanyma filtrama 
            ajax: {
                url: window.location.href,
                type: "GET",
            },

            order: [[3, 'desc']],
            rowReorder: false,
            fixedColumns: false,
            pageLength: 15,
            lengthMenu: [[15, 20, 30], [15, 20, 30]],
            layout: {
                topStart: {
                    search: {
                        placeholder: "Hledej ..."
                    }
                },
                topEnd: 'pageLength',
                bottomStart: 'info',
                bottomEnd: 'paging'
            },
            columns: [
                { data: 'order_number', orderable: false, searchable: true },
                { data: 'distrib_hub', orderable: true, searchable: true },
                { data: 'mandant', orderable: true, searchable: true },
                { data: 'evidence_termin', orderable: true, searchable: true },
                { data: 'delivery_termin', orderable: true, searchable: true },
                { data: 'client', orderable: true, searchable: true },
                { data: 'team_type', orderable: true, searchable: false },
                { data: 'team', orderable: true, searchable: true },
                { data: 'montage_termin', orderable: true, searchable: true },
                { data: 'status', orderable: true, searchable: false },
                { data: 'articles', orderable: false, searchable: false },
                { data: 'notes', orderable: false, searchable: false },
            ],
            language: {
                emptyTable: "Žádné objednávky",
                info: "<small>od <strong>_START_</strong> do <strong>_END_</strong> z <strong>_TOTAL_</strong> záznamů (filtr z <strong>_MAX_</strong> záznamů)</small>",
                infoFiltered: "",
                infoEmpty: "",
                lengthMenu: "<small>_MENU_ zakázek na stránku</small>",
                search: "Vyhledávání: "
            },
        });
        // Delegace - nasloucháme klikům na odkazy v tabulce
        orderTable.addEventListener("click", function (e) {
            const link = e.target.closest(".copy_link_order_number");

            if (link) {
                const text = link.innerText.trim();

                navigator.clipboard.writeText(text).then(() => {
                }).catch(() => {
                    console.log("❌ Kopírování selhalo.");
                });
            }
        });
    }

    // datatables for client orders
    if (clientOrderTable) {
        $(clientOrderTable).DataTable({
            order: [[3, 'desc']],
            rowReorder: false,
            fixedColumns: false,
            pageLength: 5,
            lengthMenu: [[5, 10, 15, -1], [5, 10, 15, "Vše"]],
            layout: {
                topStart: {
                    search: {
                        placeholder: "Hledej ..."
                    }
                },
                topEnd: 'pageLength',
                bottomStart: 'info',
                bottomEnd: 'paging'
            },
            columnDefs: [
                { targets: [3, 4, 7], type: 'date' },
                { targets: [0, 9, 10], orderable: false }],
            language: {
                emptyTable: "Žádné objednávky",
                decimal: ",",
                info: "Zobrazuji _START_ až _END_ z _TOTAL_ záznamů (filtr z _MAX_ záznamů)",
                infoFiltered: "",
                infoEmpty: "",
                search: "Vyhledávání: ",
                lengthMenu: "_MENU_ zakázek na stránku",
            },
        });
    }

    // DataTable for teams
    if (teamTable) {
        $(teamTable).DataTable({
            order: [[3, 'asc']],
            rowReorder: false,
            fixedColumns: false,
            pageLength: 15,
            lengthMenu: [[15, 20, 30, -1], [15, 20, 30, "Vše"]],
            layout: {
                topStart: {
                    search: {
                        placeholder: "Hledej ..."
                    }
                },
                topEnd: 'pageLength',
                bottomStart: 'info',
                bottomEnd: 'paging'
            },
            columnDefs: [
                { orderable: false, targets: [6] },
                { targets: [4, 5], type: 'num-fmt' }
            ],
            language: {
                emptyTable: "Žádné Teamy",
                decimal: ",",
                info: "Zobrazuji _START_ až _END_ z _TOTAL_ záznamů (filtr z _MAX_ záznamů)",
                infoFiltered: "",
                infoEmpty: "",
                lengthMenu: "_MENU_ zakázek na stránku",
                search: "Vyhledávání: "
            },
        });
    }

    // galerie lightbox
    lightbox.option({
        'resizeDuration': 200,
        'imageFadeDuration': 200,
        'wrapAround': true,
        "fitImagesInViewport": true,
    })

    document.addEventListener("DOMContentLoaded", function () {
        const ctx = document.querySelector("#openOrders"); // tvůj canvas
        const openOrders = parseInt(ctx.dataset.openOrders);
        const closedOrders = parseInt(ctx.dataset.closedOrders);

        const data = {
            labels: ["Open Orders", "Closed Orders"],
            datasets: [{
                data: [openOrders, closedOrders],
                label: "Value",
            }]
        };

        const openOrdersChart = new Chart(ctx, {
            type: 'polarArea',
            data: data
        });
    });

})();