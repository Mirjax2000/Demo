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
    const formsetContainer = $('#article-formset-container');
    const totalFormsInput = $('#id_article_set-TOTAL_FORMS');
    const emptyFormHtml = $('#empty-form-template');

    // prechod pri nahrani stranky
    window.addEventListener("load", () => {
        P_main.classList.add("visible");
    });
    // messages
    if (messages && messages.length > 0) {
        messages.each(function (index, element) {
            // Převod elementu na jQuery objekt
            $(element).hide();
            $(element).slideDown(250);

            // Po 5 sekundách efekt zmizení + odstranění elementu
            setTimeout(function () {
                $(element).slideUp(250, function () {
                    $(this).remove();
                });
            }, 5000);
        });
    }
    // articles

    // form cleaning
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

    // ------ article formset 
    if (emptyFormHtml.length) {
        emptyFormHtml.html().trim()
    }

    // Přidání nového formuláře
    $('#add-article-button').on('click', function () {
        const formIndex = parseInt(totalFormsInput.val(), 10);
        const newFormHtml = emptyFormHtml.replace(/__prefix__/g, formIndex);
        formsetContainer.append(newFormHtml);
        totalFormsInput.val(formIndex + 1);
    });

    // Odebrání formuláře
    formsetContainer.on('click', '.remove-article-button', function () {
        const formDiv = $(this).closest('.L-form__article-form');

        // Pokud je ve formuláři delete checkbox (can_delete), zaškrtneme ho a skryjeme formulář
        const deleteInput = formDiv.find('input[type="checkbox"][name$="-DELETE"]');
        if (deleteInput.length) {
            deleteInput.prop('checked', true);
            formDiv.hide();
        } else {
            // Jinak rovnou odstraníme z DOM
            formDiv.remove();

            // Snížení počtu TOTAL_FORMS není nutné pro backend, ale můžeme ho udělat:
            const newTotal = formsetContainer.find('.L-form__article-form').length;
            totalFormsInput.val(newTotal);
        }
    });
})();
