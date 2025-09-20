(function () {

    console.log("modules.js loaded");

    const orderTable = document.getElementById("orderTable");
    const teamTable = document.getElementById("teamTable");
    const clientOrderTable = document.getElementById("clientOrderTable");
    // chart.js - otevrene zakazky
    document.addEventListener("DOMContentLoaded", function () {
        renderOpenOrdersChart();
        renderClosedOrdersChart();
        renderAdvicedTypeOrdersChart()
    });

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
    // chart.js otevrene zakazky
    function renderOpenOrdersChart() {
        const ctx = document.querySelector("#openOrders");
        if (!ctx) return; // kdyby tam canvas nebyl

        const ordersData = JSON.parse(ctx.dataset.openOrders);

        const data = {
            labels: ["Nové", "Zatermínované", "Realizované"],
            datasets: [{
                data: [
                    ordersData.nove,
                    ordersData.zaterminovane,
                    ordersData.realizovane
                ],
            }]
        };

        const centerTextPlugin = {
            id: 'centerText',
            afterDraw(chart) {
                const { ctx, chartArea: { left, right, top, bottom } } = chart;
                const centerX = (left + right) / 2;
                const centerY = (top + bottom) / 2;
                const total = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);

                const getTextColor = () => {
                    const html = document.documentElement;
                    return html.dataset.theme === 'dark' ? '#ffffff' : '#000000';
                };

                ctx.save();
                ctx.font = 'bold 36px Arial';
                ctx.fillStyle = getTextColor();
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(total, centerX, centerY);
                ctx.restore();

                if (!chart._observerSetup) {
                    const html = document.documentElement;
                    const observer = new MutationObserver(() => chart.update());
                    observer.observe(html, { attributes: true, attributeFilter: ['data-theme'] });
                    chart._observerSetup = true;
                }
            }
        };

        new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                let total = context.dataset.data.reduce((a, b) => a + b, 0);
                                let value = context.parsed;
                                let percentage = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            },
            plugins: [centerTextPlugin]
        });
    }

    // chart.js closed zakazky
    function renderClosedOrdersChart() {
        const ctx = document.querySelector("#closedOrders");
        if (!ctx) return; // kdyby tam canvas nebyl

        const ordersData = JSON.parse(ctx.dataset.closedOrders);

        const data = {
            labels: ["Vyúčtované", "Zrušené"],
            datasets: [{
                data: [
                    ordersData.vyuctovane,
                    ordersData.zrusene,
                ],
                backgroundColor: [
                    '#6c757d',
                    '#dc3545',
                ]
            }]
        };

        const centerTextPlugin = {
            id: 'centerText',
            afterDraw(chart) {
                const { ctx, chartArea: { left, right, top, bottom } } = chart;
                const centerX = (left + right) / 2;
                const centerY = (top + bottom) / 2;
                const total = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);

                const getTextColor = () => {
                    const html = document.documentElement;
                    return html.dataset.theme === 'dark' ? '#ffffff' : '#000000';
                };

                ctx.save();
                ctx.font = 'bold 36px Arial';
                ctx.fillStyle = getTextColor();
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(total, centerX, centerY);
                ctx.restore();

                if (!chart._observerSetup) {
                    const html = document.documentElement;
                    const observer = new MutationObserver(() => chart.update());
                    observer.observe(html, { attributes: true, attributeFilter: ['data-theme'] });
                    chart._observerSetup = true;
                }
            }
        };

        new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                let total = context.dataset.data.reduce((a, b) => a + b, 0);
                                let value = context.parsed;
                                let percentage = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            },
            plugins: [centerTextPlugin]
        });
    }
    // chart.js adviced type zakazky
    function renderAdvicedTypeOrdersChart() {
        const ctx = document.querySelector("#advicedOrders");
        if (!ctx) return; // kdyby tam canvas nebyl

        const ordersData = JSON.parse(ctx.dataset.advicedTypeOrders);

        const data = {
            labels: ["Montážní", "Dopravní"],
            datasets: [{
                data: [
                    ordersData.montazni,
                    ordersData.dopravni,
                ],
                backgroundColor: [
                    '#3384ff', // modrá pro Montážní
                    '#198754', // tmavě zelená pro Dopravní
                ]
            }]
        };

        const centerTextPlugin = {
            id: 'centerText',
            afterDraw(chart) {
                const { ctx, chartArea: { left, right, top, bottom } } = chart;
                const centerX = (left + right) / 2;
                const centerY = (top + bottom) / 2;
                const total = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);

                const getTextColor = () => {
                    const html = document.documentElement;
                    return html.dataset.theme === 'dark' ? '#ffffff' : '#000000';
                };

                ctx.save();
                ctx.font = 'bold 36px Arial';
                ctx.fillStyle = getTextColor();
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(total, centerX, centerY);
                ctx.restore();

                if (!chart._observerSetup) {
                    const html = document.documentElement;
                    const observer = new MutationObserver(() => chart.update());
                    observer.observe(html, { attributes: true, attributeFilter: ['data-theme'] });
                    chart._observerSetup = true;
                }
            }
        };

        new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                let total = context.dataset.data.reduce((a, b) => a + b, 0);
                                let value = context.parsed;
                                let percentage = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            },
            plugins: [centerTextPlugin]
        });
    }


})();