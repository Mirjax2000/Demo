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

    // File input validation
    document.addEventListener("DOMContentLoaded", function () {
        const fileInput = document.getElementById("fileInput");
        const fileError = document.getElementById("fileError");
        // ---
        const fileInputProtocol = document.getElementById("fileInputProtocol");
        const errorMessageProtocolfile = document.getElementById("errorMessageProtocolfile");

        const allowedImageTypes = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
            "image/bmp",
            "image/gif",
        ];

        if (fileInput && fileError) {
            fileInput.addEventListener("change", function () {
                const file = fileInput.files[0];
                fileError.textContent = "";

                if (file) {

                    if (file.size > 5 * 1024 * 1024) { // 5 MB
                        const sizeMB = (file.size / 1024 / 1024).toFixed(2);
                        fileError.innerHTML = `Soubor je příliš velký <strong class="u-txt-error">${sizeMB} MB</strong>.<br> Max. velikost je 5 MB.`;
                        fileInput.value = "";
                        return;
                    }


                    if (!allowedImageTypes.includes(file.type)) {
                        fileError.innerHTML = `Soubor musí být ve formátu obrázku (např. JPG, PNG, WebP).<br> Nepovolený typ souboru: <strong class="u-txt-error">${file.type}</strong>.`;
                        fileInput.value = "";
                        return;
                    }

                    if (fileInput.form) {
                        fileInput.form.submit();
                    }
                }
            });
        }
        //  ---
        if (fileInputProtocol && errorMessageProtocolfile) {
            fileInputProtocol.addEventListener("change", function () {
                const file_from_fallback = fileInputProtocol.files[0];
                errorMessageProtocolfile.textContent = "";

                if (file_from_fallback) {

                    if (file_from_fallback.size > 5 * 1024 * 1024) { // 5 MB
                        const sizeMB = (file_from_fallback.size / 1024 / 1024).toFixed(2);
                        errorMessageProtocolfile.innerHTML = `Soubor je příliš velký <strong>${sizeMB} MB</strong>.<br> Max. velikost je 5 MB.`;
                        fileInputProtocol.value = "";
                        return;
                    }


                    if (!allowedImageTypes.includes(file_from_fallback.type)) {
                        errorMessageProtocolfile.innerHTML = `Soubor musí být ve formátu obrázku (např. JPG, PNG, WebP).<br> Nepovolený typ souboru: ${file_from_fallback.type}</strong>.`;
                        fileInputProtocol.value = "";
                        return;
                    }

                    if (fileInputProtocol.form) {
                        fileInputProtocol.form.submit();
                    }
                }
            });
        }

    });

    window.addEventListener("load", () => {
        syncHeight();
        checkZona();
        P_main.classList.add("visible");
    });

    // Messages
    if (messages && messages.length > 0) {
        messages.each(function (index, element) {
            $(element).hide();
            $(element).slideDown(250);

            setTimeout(function () {
                $(element).slideUp(250, function () {
                    $(this).remove();
                });
            }, 5000);
        });
    }

    // Form cleaning
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
                    } else if (field.tagName === "SELECT" && field.name === "status") {
                        field.value = "New";
                    } else {
                        field.value = "";
                    }
                }
            });

            fieldset.querySelectorAll(".L-form__error").forEach(function (errorDiv) {
                errorDiv.innerHTML = "";
            });
        });
    });

    // Validate phone numbers in inputs
    numberInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    });

    // Theme control
    function toggleTheme() {
        const current = html.dataset.theme;
        const newTheme = current === "light" ? "dark" : "light";

        html.dataset.theme = newTheme;
        localStorage.setItem("theme", newTheme);
        html.classList.remove(current);
        html.classList.add(newTheme);
    }

    if (themeToggler) { // Ensure themeToggler exists
        themeToggler.addEventListener("click", toggleTheme);
    }

    // DataTable for orders
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

    // DataTable for teams
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

    // DataTable for articles
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

    // Article formset
    if (formsetContainer.length && totalFormsInput.length && emptyFormHtml.length) {
        $('#add-article-button').on('click', function () {
            const formIndex = parseInt(totalFormsInput.val(), 10);
            const newFormHtml = emptyFormHtml.html().trim().replace(/__prefix__/g, formIndex);
            formsetContainer.append(newFormHtml);
            totalFormsInput.val(formIndex + 1);
        });

        formsetContainer.on('click', '.remove-article-button', function () {
            const formDiv = $(this).closest('.L-form__article-form');
            const deleteInput = formDiv.find('input[type="checkbox"][name$="-DELETE"]');
            if (deleteInput.length) {
                deleteInput.prop('checked', true);
                formDiv.hide();
            } else {
                formDiv.remove();
                const newTotal = formsetContainer.find('.L-form__article-form').length;
                totalFormsInput.val(newTotal);
            }
        });
    }

    // Synchronize height of left and right elements
    function syncHeight() {
        const left = document.querySelector('.left');
        const right = document.querySelector('.right');
        if (left && right) {
            console.log(left, right)
            right.style.maxHeight = left.offsetHeight + 50 + 'px';
        }
    }

    // Check "zona" radio buttons and manage 'km-wrapper' visibility and 'zona_km' required attribute
    function checkZona() {
        const pdf_form_radios = document.querySelectorAll('input[name=zona]');
        const $kmWrapper = $('#km-wrapper');
        const $defaultPdfBtn = $('#default_pdf_btn');
        const zonaKmInput = document.getElementById('zona_km');

        if (!pdf_form_radios.length || !$kmWrapper.length || !$defaultPdfBtn.length || !zonaKmInput) {
            return;
        }

        $kmWrapper.hide();
        zonaKmInput.required = false;

        pdf_form_radios.forEach(radio => {
            radio.addEventListener('change', () => {
                if (radio.value === '4' && radio.checked) {
                    $kmWrapper.stop(true, true).slideDown("fast");
                    zonaKmInput.required = true;
                } else if (radio.checked) {
                    $kmWrapper.stop(true, true).slideUp("fast");
                    zonaKmInput.required = false;
                }

                const someChecked = Array.from(pdf_form_radios).some(r => r.checked);
                if (someChecked) {
                    $defaultPdfBtn.removeClass('disabled');
                } else {
                    $defaultPdfBtn.addClass('disabled');
                }
            });
        });
    }


    // Autocomplete order number
    document.addEventListener("DOMContentLoaded", function () {
        const orderNumberInput = document.getElementById("orderNumber");
        const orderSuggestions = document.getElementById("orderSuggestions");
        const statusZakazky = document.getElementById("StatusZakazky");
        const switchWrapper = document.getElementById("realizovanoSwitch");
        const flexSwitch = document.getElementById("flexSwitchCheckChecked");
        const statusWarning = document.getElementById("statusSwitchWarning");

        // Hide switch and reset checkbox on initial load
        if (switchWrapper && flexSwitch) {
            switchWrapper.style.display = "none";
            flexSwitch.checked = false;
        }

        // Event listener for order number input (autocomplete)
        if (orderNumberInput && orderSuggestions && statusZakazky) {
            orderNumberInput.addEventListener("input", function () {
                const query = this.value.trim();

                if (query.length < 2) {
                    orderSuggestions.innerHTML = "";
                    setStatus("nezjištěno");
                    return;
                }

                $.ajax({
                    url: "/autocomp-orders/",
                    data: { term: query },
                    success: function (data) {
                        orderSuggestions.innerHTML = data.orders.map(order =>
                            `<div class="suggestion-item">${order}</div>`
                        ).join('');
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        console.error("Autocomplete AJAX error:", textStatus, errorThrown);
                        orderSuggestions.innerHTML = "";
                    }
                });
            });

            orderNumberInput.addEventListener("blur", function () {
                const enteredOrderNumber = this.value.trim();
                if (enteredOrderNumber.length > 0 && orderSuggestions.innerHTML === "") {
                    fetchStatus(enteredOrderNumber);
                }
            });

            document.addEventListener("click", function (e) {
                if (!e.target.closest("#orderNumber") && !e.target.closest("#orderSuggestions")) {
                    orderSuggestions.innerHTML = "";
                }
            });

            orderSuggestions.addEventListener("click", function (e) {
                if (e.target.classList.contains("suggestion-item")) {
                    const selected = e.target.textContent.trim();
                    orderNumberInput.value = selected;
                    orderSuggestions.innerHTML = "";
                    fetchStatus(selected);
                }
            });
        }

        // Event listener for switch change
        if (flexSwitch && statusWarning) {
            flexSwitch.addEventListener("change", function () {
                statusWarning.style.visibility = this.checked ? "visible" : "hidden";
            });
        }

        // Fetch status from backend
        function fetchStatus(orderNumber) {
            $.ajax({
                url: "/order-status/",
                data: { order_number: orderNumber },
                success: function (data) {
                    setStatus(data.status);
                },
                error: function () {
                    setStatus("Neznámé číslo zakázky");
                }
            });
        }

        // Set status and display switch/warning
        function setStatus(status) {
            if (!statusZakazky || !switchWrapper || !flexSwitch || !statusWarning) return;

            statusZakazky.textContent = status;
            statusZakazky.classList.remove("u-txt-muted", "u-txt-success", "u-txt-warning");
            statusWarning.style.visibility = "hidden";

            const lower = status.toLowerCase().trim();

            switch (lower) {
                case "nezjištěno":
                    statusZakazky.classList.add("u-txt-muted");
                    switchWrapper.style.display = "none";
                    flexSwitch.checked = false;
                    break;
                case "realizováno":
                    statusZakazky.classList.add("u-txt-success");
                    switchWrapper.style.display = "none";
                    flexSwitch.checked = false;
                    break;
                case "vyúčtovaný":
                    statusZakazky.classList.add("u-txt-warning");
                    switchWrapper.style.display = "block";
                    flexSwitch.checked = false;
                    break;
                default:
                    statusZakazky.classList.add("u-txt-warning");
                    switchWrapper.style.display = "block";
                    flexSwitch.checked = true;
                    statusWarning.style.visibility = "visible";
                    break;
            }
        }
    });
})();