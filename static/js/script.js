(function () {
    console.log("script.js");
    const html = document.documentElement;
    const themeToggler = document.getElementById("themeToggler");
    const orderTable = document.getElementById("orderTable");
    const teamTable = document.getElementById("teamTable");


    function toggleTheme() {
        const current = html.dataset.theme;
        const newTheme = current === "light" ? "dark" : "light";

        html.dataset.theme = newTheme;

        localStorage.setItem("theme", newTheme);

        html.classList.remove(current);
        html.classList.add(newTheme);
    }

    themeToggler.addEventListener("click", toggleTheme);
    // 

    if (orderTable) {
        $(orderTable).DataTable({
            order: [[0, 'desc']],

            rowReorder: false,
            fixedColumns: true,
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
                { orderable: false, targets: [5, 12] }
            ],

            language: {
                emptyTable: "Žádné objednávky"
            },
        });
    }

    if (teamTable) {
        $(teamTable).DataTable({

            rowReorder: false,
            fixedColumns: true,
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

            language: {
                emptyTable: "Žádné objednávky"
            },
        });
    }

})();




