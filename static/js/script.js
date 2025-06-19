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

    window.addEventListener("load", () => {
        syncHeight();
        checkZona();
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


    // ---- article formset
    // Přidání nového formuláře
    $('#add-article-button').on('click', function () {
        const formIndex = parseInt(totalFormsInput.val(), 10);
        const newFormHtml = emptyFormHtml.html().trim().replace(/__prefix__/g, formIndex);
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
    // ----
    function syncHeight() {
        const left = document.querySelector('.left');
        const right = document.querySelector('.right');
        if (left && right) {
            console.log(left, right)
            right.style.maxHeight = left.offsetHeight + 50 + 'px';
        }
    }
    // ---
    function checkZona() {
        const pdf_form_radios = document.querySelectorAll('input[name=zona]');
        const kmWrapper = document.getElementById('km-wrapper');
        const defaultPdfBtn = document.getElementById('default_pdf_btn');
        const zonaKmInput = document.getElementById('zona_km'); // input, co chceme dělat required

        if (!pdf_form_radios.length || !kmWrapper || !defaultPdfBtn || !zonaKmInput) {
            return;
        }

        pdf_form_radios.forEach(radio => {
            radio.addEventListener('change', () => {
                if (radio.value === '4' && radio.checked) {
                    kmWrapper.classList.remove('u-opacity-0');
                    kmWrapper.classList.add('u-opacity-1');
                    zonaKmInput.required = true;
                } else if (radio.checked) {
                    kmWrapper.classList.remove('u-opacity-1');
                    kmWrapper.classList.add('u-opacity-0');
                    zonaKmInput.required = false;
                }

                const someChecked = Array.from(pdf_form_radios).some(r => r.checked);
                if (someChecked) {
                    defaultPdfBtn.classList.remove('disabled');
                } else {
                    defaultPdfBtn.classList.add('disabled');
                }
            });
        });
    }

    // --- autocomplete orderNumber ---
    const orderNumberInput = document.getElementById("orderNumber");
    const orderSuggestions = document.getElementById("orderSuggestions");

    if (orderNumberInput && orderSuggestions) {
        orderNumberInput.addEventListener("input", function () {
            const query = this.value;

            if (query.length < 2) {
                orderSuggestions.innerHTML = "";
                return;
            }

            $.ajax({
                url: "/autocomplete-orders/",
                data: { term: query },
                success: function (data) {
                    let html = "";
                    data.orders.forEach(function (item) {
                        html += `<div class="suggestion-item">${item}</div>`;
                    });
                    orderSuggestions.innerHTML = html;
                }
            });
        });

        document.addEventListener("click", function (e) {
            if (!e.target.closest("#orderNumber") && !e.target.closest("#orderSuggestions")) {
                orderSuggestions.innerHTML = "";
            }
        });

        orderSuggestions.addEventListener("click", function (e) {
            if (e.target.classList.contains("suggestion-item")) {
                orderNumberInput.value = e.target.textContent;
                orderSuggestions.innerHTML = "";
            }
        });
    }


})();
