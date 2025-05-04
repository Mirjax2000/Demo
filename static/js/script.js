(function () {
    console.log("script.js");
    const html = document.documentElement;
    const themeToggler = document.getElementById("themeToggler");
    const orderTable = document.getElementById("orderTable");
    const teamTable = document.getElementById("teamTable");
    const articleTable = document.getElementById("articleTable");
    const numberInputs = document.querySelectorAll(".number");
    const deleteBtns = document.querySelectorAll(".form__delete");
    const P_main = document.querySelector(".P-main");
    const messages = $(".C-messages");
    const arcticleBtns = $('.toggle-btn');
    // prechod pri nahrani stranky
    window.addEventListener("load", () => {
        P_main.classList.add("visible");
    });
    // messages
    messages.each(function (index, element) {
        setTimeout(function () {
            $(element).fadeOut(1000, function () {
                $(this).remove();
            });
        }, 5000);
    });
    // articles
    arcticleBtns.on('click', function () {
        const target = $(this).next('.L-form__articles');
        const addBtn = $(this).find('i');

        // pokud už je otevřená, zavři ji
        if (target.is(':visible')) {
            target.slideUp();
            addBtn.removeClass('fa-minus').addClass('fa-plus');
        } else {
            // zavři ostatní sekce
            $('.L-form__articles').slideUp();
            $('.toggle-btn i').removeClass('fa-minus').addClass('fa-plus');

            // otevři právě tuhle
            target.slideDown();
            addBtn.removeClass('fa-plus').addClass('fa-minus');
        }
    });

    // articl form cleaning
    deleteBtns.forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const fieldset = this.closest("fieldset");

            fieldset.querySelectorAll("input, textarea, select").forEach(function (field) {
                if (
                    field.type !== "hidden" &&
                    field.type !== "submit" &&
                    field.type !== "button"
                ) {
                    if (field.tagName === "SELECT" && field.name === "team_type") {
                        field.value = "By_assembly_crew";
                    }
                    else if (field.tagName === "SELECT" && field.name === "status") {
                        field.value = "New";
                    }
                    else {
                        field.value = "";
                    }
                }
            });

            fieldset.querySelectorAll(".L-form__error").forEach(function (errorDiv) {
                errorDiv.innerHTML = "";  // Vyčistění chybových hlášení
            });
        });
    });

    // validace tel num v inputech
    numberInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    });

    // theme control
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
            columnDefs: [],
            language: {
                emptyTable: "Žádné objednávky"
            },
        });
    }

    if (teamTable) {
        $(teamTable).DataTable({
            order: [[3, 'asc']],
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
                { orderable: false, targets: [6] },
                { targets: [4, 5], type: 'num-fmt' }
            ],
            language: {
                emptyTable: "Žádné Teamy",
                decimal: ","
            },
        });
    }

    if (articleTable) {
        $(articleTable).DataTable({
            rowReorder: false,
            fixedColumns: true,
            searching: false,
            paging: false,

            columnDefs: [
                { orderable: false, targets: [3] },
            ],
            language: {
                emptyTable: "Žádné Artikly !!!",
            },
        });
    }

})();




