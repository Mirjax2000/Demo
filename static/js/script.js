(function () {
    console.log("script.js");
    const html = document.documentElement;
    const themeToggler = document.getElementById("themeToggler");
    const orderTable = document.getElementById("orderTable");
    const clientOrderTable = document.getElementById("clientOrderTable");
    const teamTable = document.getElementById("teamTable");
    const numberInputs = document.querySelectorAll(".number");
    const deleteBtns = document.querySelectorAll(".form__delete");
    const P_main = document.querySelector(".P-main");
    const messages = $(".C-messages");
    const formsetContainer = $('#article-formset-container');
    const totalFormsInput = $('#id_article_set-TOTAL_FORMS');
    const emptyFormHtml = $('#empty-form-template');

    // detail profit
    document.addEventListener("DOMContentLoaded", detailProfit);
    // making_delivery_order
    document.addEventListener("DOMContentLoaded", making_delivery_order);
    // naklad vynos skryti
    document.addEventListener("DOMContentLoaded", input_vynos_naklad);
    // delete Order
    document.addEventListener("DOMContentLoaded", deleteOrder);
    // SCCZ filter
    document.addEventListener("DOMContentLoaded", scczFilter);
    // hiden Order
    document.addEventListener("DOMContentLoaded", hiddenOrder);
    // delete team
    document.addEventListener("DOMContentLoaded", deleteTeam);
    // delete switch na realizovano s dopravou
    document.addEventListener("DOMContentLoaded", advicedRealizedOrder);
    // copy to schranka
    document.addEventListener("DOMContentLoaded", function () {
        setupAutobotCopy();
        setupDopravniZakazka();
        setupApiBaseUrl();
    });



    // File input validation v creation page
    document.addEventListener("DOMContentLoaded", function () {
        // --- montazni protokol form na back protokolu
        const fileInput = document.getElementById("fileInput");
        const fileError = document.getElementById("fileError");

        // --- montazni img form na back protokolu
        const fileInputImg = document.getElementById("fileInputImg");
        const fileErrorImg = document.getElementById("fileErrorImg");

        // --- fallback protocol form
        const fileInputProtocol = document.getElementById("fileInputProtocol");
        const errorMessageProtocolfile = document.getElementById("errorMessageProtocolfile");

        // --- fallback image form
        const fileInputImgFallback = document.getElementById("fileInputImgFallback");
        const errorMessageImgfile = document.getElementById("errorMessageImgfile");

        // --- CSV form
        const CsvFormFile = document.getElementById("CsvFormFile");
        const csv_error_message = document.getElementById("csv_error_message");

        const allowedImageTypes = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
            "image/bmp",
            "image/gif",
        ];
        // --- montazni protokol form
        if (fileInput && fileError) {
            fileInput.addEventListener("change", function () {
                const file = fileInput.files[0];
                fileError.textContent = "";

                if (file) {

                    if (file.size > 10 * 1024 * 1024) { // 10 MB
                        const sizeMB = (file.size / 1024 / 1024).toFixed(2);
                        fileError.innerHTML = `Soubor je příliš velký <strong class="u-txt-error">${sizeMB} MB</strong>.<br> Max. velikost je 10 MB.`;
                        fileInput.value = "";
                        return;
                    }


                    if (!allowedImageTypes.includes(file.type)) {
                        fileError.innerHTML = `Soubor nemá správný formát: např. JPG, PNG, WebP.<br> Nepovolený typ souboru: <strong class="u-txt-error">${file.type}</strong>.`;
                        fileInput.value = "";
                        return;
                    }

                    if (fileInput.form) {
                        fileInput.form.submit();
                    }
                }
            });
        }
        // --- montazni images form
        if (fileInputImg && fileErrorImg) {
            fileInputImg.addEventListener("change", function () {
                const file = fileInputImg.files[0];
                fileErrorImg.textContent = "";

                if (file) {

                    if (file.size > 10 * 1024 * 1024) { // 10 MB
                        const sizeMB = (file.size / 1024 / 1024).toFixed(2);
                        fileErrorImg.innerHTML = `Soubor je příliš velký <strong class="u-txt-error">${sizeMB} MB</strong>.<br> Max. velikost je 10 MB.`;
                        fileInputImg.value = "";
                        return;
                    }

                    if (!allowedImageTypes.includes(file.type)) {
                        fileErrorImg.innerHTML = `Soubor nemá spravný formát: např. JPG, PNG, WebP.<br> Nepovolený typ souboru: <strong class="u-txt-error">${file.type}</strong>.`;
                        fileInputImg.value = "";
                        return;
                    }

                    if (fileInputImg.form) {
                        fileInputImg.form.submit();
                    }
                }
            });
        }

        //  --- protokol fallback form
        if (fileInputProtocol && errorMessageProtocolfile) {
            fileInputProtocol.addEventListener("change", function () {
                const file_from_fallback = fileInputProtocol.files[0];
                errorMessageProtocolfile.textContent = "";

                if (file_from_fallback) {
                    const maxSize = 10
                    let countSize = maxSize * 1024 * 1024

                    if (file_from_fallback.size > countSize) {
                        const sizeMB = (file_from_fallback.size / 1024 / 1024).toFixed(2);
                        errorMessageProtocolfile.innerHTML = `File too big <strong>${sizeMB} </strong>MB. Max. size is <strong>${maxSize}</strong> MB.`;
                        fileInputProtocol.value = "";
                        return;
                    }


                    if (!allowedImageTypes.includes(file_from_fallback.type)) {
                        errorMessageProtocolfile.innerHTML = "Povolené formáty (např. JPG, PNG, WebP).";
                        fileInputProtocol.value = "";
                        return;
                    }
                }
            });
        }

        //  --- protokol image fallback form
        if (fileInputImgFallback && errorMessageImgfile) {
            fileInputImgFallback.addEventListener("change", function () {
                const file_from_fallback = fileInputImgFallback.files[0];
                errorMessageImgfile.textContent = "";

                if (file_from_fallback) {
                    const maxSize = 10
                    let countSize = maxSize * 1024 * 1024

                    if (file_from_fallback.size > countSize) {
                        const sizeMB = (file_from_fallback.size / 1024 / 1024).toFixed(2);
                        errorMessageImgfile.innerHTML = `File too big <strong>${sizeMB} </strong>MB. Max. size is <strong>${maxSize}</strong> MB.`;
                        fileInputImgFallback.value = "";
                        return;
                    }

                    if (!allowedImageTypes.includes(file_from_fallback.type)) {
                        errorMessageImgfile.innerHTML = "Povolené formáty (např. JPG, PNG, WebP).";
                        fileInputImgFallback.value = "";
                        return;
                    }
                }
            });
        }
        //  --- CSV form
        if (CsvFormFile && csv_error_message) {
            CsvFormFile.addEventListener("change", function () {
                const file_from_csv = CsvFormFile.files[0];
                csv_error_message.textContent = "";

                // Přeskoč kontrolu velikosti, pokud je checkbox zaškrtnutý
                const checkbox = document.getElementById("potlacitVelikostCsvChckBox");
                const ignoreSizeLimit = checkbox?.checked;

                if (file_from_csv) {
                    const maxSize = 10
                    let countSize = maxSize * 1024 * 1024
                    const fileName = file_from_csv.name.toLowerCase();
                    if (!ignoreSizeLimit && file_from_csv.size > countSize) {
                        const sizeMB = (file_from_csv.size / 1024 / 1024).toFixed(2);
                        csv_error_message.innerHTML = `File too big <strong>${sizeMB} </strong>MB. Max. size is <strong>${maxSize}</strong> MB.`;
                        CsvFormFile.value = "";
                        return;
                    }

                    if (!fileName.endsWith(".csv")) {
                        csv_error_message.innerHTML = `Soubor musí být ve formátu CSV. Nepovolený typ souboru: ${file_from_csv.type}`;
                        CsvFormFile.value = "";
                        return;
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

    // Theme control function
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
    // 
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


    // Autocomplete order number pro back protokol fallback form
    document.addEventListener("DOMContentLoaded", function () {
        // ---------- KONFIGURACE ----------
        const config = {
            inputId: "orderNumber",
            suggestionsId: "orderSuggestions",
            statusId: "StatusZakazky",
            switchWrapperId: "realizovanoSwitch",
            switchId: "flexSwitchCheckChecked",
            switchWarningId: "statusSwitchWarning",
            autocompleteUrl: "/autocomp-orders/",
            statusUrl: "/order-status/",
            debounceTime: 250,
        };

        // ---------- ELEMENTY ----------
        const el = {
            input: document.getElementById(config.inputId),
            suggestions: document.getElementById(config.suggestionsId),
            status: document.getElementById(config.statusId),
            switchWrapper: document.getElementById(config.switchWrapperId),
            switch: document.getElementById(config.switchId),
            switchWarning: document.getElementById(config.switchWarningId),
        };

        if (!el.input || !el.suggestions || !el.status) return;

        // ---------- DEBOUNCE ----------
        const debounce = (fn, delay) => {
            let timer;
            return (...args) => {
                clearTimeout(timer);
                timer = setTimeout(() => fn(...args), delay);
            };
        };

        // ---------- STATUS ----------
        const setStatus = (status) => {
            if (!el.status || !el.switchWrapper || !el.switch || !el.switchWarning) return;

            el.status.textContent = status;
            el.status.classList.remove("u-txt-muted", "u-txt-success", "u-txt-warning");
            el.switchWarning.style.visibility = "hidden";

            const lower = status.toLowerCase().trim();

            // --- speciální případ pro ne-montážní zakázku ---
            if (status === "Toto není montážní zakázka") {
                let saveProtocolBtn = document.getElementById("saveProtocolBtn")
                saveProtocolBtn.classList.add("disabled");
                el.status.classList.add("u-txt-warning");
                el.switchWrapper.style.display = "none"; // přepínač vůbec nezobrazit
                return;
            }
            switch (lower) {
                case "nezjištěno":
                    el.status.classList.add("u-txt-muted");
                    el.switchWrapper.style.display = "none";
                    el.switch.checked = false;
                    break;
                case "realizováno":
                    el.status.classList.add("u-txt-success");
                    el.switchWrapper.style.display = "none";
                    el.switch.checked = false;
                    break;
                case "vyúčtovaný":
                    el.status.classList.add("u-txt-warning");
                    el.switchWrapper.style.display = "block";
                    el.switch.checked = false;
                    break;
                default:
                    el.status.classList.add("u-txt-warning");
                    el.switchWrapper.style.display = "block";
                    el.switch.checked = true;
                    el.switchWarning.style.visibility = "visible";
                    break;
            }
        };

        const fetchStatus = (orderNumber) => {
            $.ajax({
                url: config.statusUrl,
                data: { order_number: orderNumber },
                success: (data) => setStatus(data.status),
                error: (jqXHR) => {
                    if (jqXHR.status === 404) {
                        setStatus("Neznámé číslo zakázky");
                    } else if (jqXHR.status === 409) {
                        setStatus("Toto není montážní zakázka");
                    } else {
                        setStatus("Chyba při získávání statusu");
                    }
                }
            });
        };

        // ---------- AUTOCOMPLETE ----------
        const fetchSuggestions = debounce((query) => {
            if (query.length < 2) {
                el.suggestions.innerHTML = "";
                setStatus("nezjištěno");
                return;
            }
            $.ajax({
                url: config.autocompleteUrl,
                data: { term: query },
                success: (data) => {
                    el.suggestions.innerHTML = data.orders.map(order =>
                        `<div class="suggestion-item">${order}</div>`
                    ).join('');
                },
                error: () => { el.suggestions.innerHTML = ""; }
            });
        }, config.debounceTime);

        el.input.addEventListener("input", function () {
            fetchSuggestions(this.value.trim());
        });

        // ---------- CLICK OUTSIDE ----------
        document.addEventListener("click", function (e) {
            if (!e.target.closest(`#${config.inputId}`) &&
                !e.target.closest(`#${config.suggestionsId}`)) {
                el.suggestions.innerHTML = "";
            }
        });

        // ---------- SELECT SUGGESTION ----------
        el.suggestions.addEventListener("mousedown", function (e) {
            if (e.target.classList.contains("suggestion-item")) {
                const selected = e.target.textContent.trim();
                el.input.value = selected;
                el.suggestions.innerHTML = "";
                fetchStatus(selected);
            }
        });

        // ---------- BLUR ----------
        el.input.addEventListener("blur", function () {
            // Timeout aby click na suggestion stihl proběhnout
            setTimeout(() => {
                if (el.suggestions.innerHTML === "") {
                    const val = el.input.value.trim();
                    if (val) fetchStatus(val);
                }
            }, 150);
        });

        // ---------- SWITCH ----------
        if (el.switch && el.switchWarning) {
            // initial reset
            el.switchWrapper.style.display = "none";
            el.switch.checked = false;

            el.switch.addEventListener("change", function () {
                el.switchWarning.style.visibility = this.checked ? "visible" : "hidden";
            });
        }
    });

    // Autocomplete order number pro image fallback form
    document.addEventListener("DOMContentLoaded", function () {
        const orderNumberInput = document.getElementById("orderNumberForImgFallback");
        const orderSuggestions = document.getElementById("orderSuggestionsForImgFallback");

        if (!orderNumberInput || !orderSuggestions) return;

        // Pomocná funkce pro získání statusu (pokud máš fetchStatus definované)
        const fetchStatusSafe = (orderNumber) => {
            if (typeof fetchStatus === "function") fetchStatus(orderNumber);
        };

        orderNumberInput.addEventListener("input", function () {
            const query = this.value.trim();

            if (query.length < 2) {
                orderSuggestions.innerHTML = "";
                if (typeof setStatus === "function") setStatus("nezjištěno");
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
            if (enteredOrderNumber && orderSuggestions.innerHTML === "") {
                fetchStatusSafe(enteredOrderNumber);
            }
        });

        // Zavření dropdownu kliknutím mimo input
        document.addEventListener("click", function (e) {
            if (!e.target.closest("#orderNumberForImgFallback") && !e.target.closest("#orderSuggestionsForImgFallback")) {
                orderSuggestions.innerHTML = "";
            }
        });

        // Výběr položky z autocomplete
        orderSuggestions.addEventListener("click", function (e) {
            if (e.target.classList.contains("suggestion-item")) {
                const selected = e.target.textContent.trim();
                orderNumberInput.value = selected;
                orderSuggestions.innerHTML = "";
                fetchStatusSafe(selected);
            }
        });
    });


    //  --- protokol img
    $(document).ready(function () {
        const protocolImg = $('#protocolImg');
        const imgModal = $('#imgModalProtocol');

        protocolImg.on('click', function () {
            imgModal.fadeIn(500);
        });

        imgModal.on('click', function () {
            imgModal.fadeOut(300);
        });
    });

    // --- autobot copy values to schranka function pro incomplete customers
    function setupAutobotCopy() {
        const btn = document.getElementById("copyBtnAutobot");
        const tokkenEl = document.getElementById("autobotTokken");
        const urlGetEl = document.getElementById("autobotUrlGet");
        const urlUpdateEl = document.getElementById("autobotUrlUpdate");
        const successMsg = document.getElementById("copySuccessAutobot");

        if (btn && tokkenEl && urlGetEl && urlUpdateEl && successMsg) {
            btn.addEventListener("click", function () {
                const cleanLine = (el) => {
                    return el.textContent.trim().replace(/\s+=\s+/, " = ");
                };

                const textToCopy = [
                    cleanLine(tokkenEl),
                    cleanLine(urlGetEl),
                    cleanLine(urlUpdateEl)
                ].join("\n");

                navigator.clipboard.writeText(textToCopy).then(() => {
                    successMsg.classList.remove("d-none");
                    successMsg.classList.add("d-inline-block");

                    // Zpráva se automaticky skryje po 2 sekundách
                    setTimeout(() => {
                        successMsg.classList.remove("d-inline-block");
                        successMsg.classList.add("d-none");
                    }, 2000);
                }).catch((err) => {
                    console.error("Chyba kopírování:", err);
                });
            });
        }
    }
    // --- copy values to schranka function pro dopravni zakazka
    function setupDopravniZakazka() {
        const btn = document.getElementById("copyBtnAutobotDopravniZakazka");
        const tokkenEl = document.getElementById("autobotTokkenDopravniZakazka");
        const urlGetEl = document.getElementById("autobotUrlGetDopravniZakazka");
        const urlUpdateEl = document.getElementById("autobotUrlUpdateDopravniZakazka");
        const successMsg = document.getElementById("copySuccessAutobotDopravniZakazka");

        if (btn && tokkenEl && urlGetEl && urlUpdateEl && successMsg) {
            btn.addEventListener("click", function () {
                const cleanLine = (el) => {
                    return el.textContent.trim().replace(/\s+=\s+/, " = ");
                };

                const textToCopy = [
                    cleanLine(tokkenEl),
                    cleanLine(urlGetEl),
                    cleanLine(urlUpdateEl)
                ].join("\n");

                navigator.clipboard.writeText(textToCopy).then(() => {
                    successMsg.classList.remove("d-none");
                    successMsg.classList.add("d-inline-block");

                    setTimeout(() => {
                        successMsg.classList.remove("d-inline-block");
                        successMsg.classList.add("d-none");
                    }, 2000);
                }).catch((err) => {
                    console.error("Chyba kopírování:", err);
                });
            });
        }
    }
    // --- copy values to schranka function pro baseUrl
    function setupApiBaseUrl() {
        const btn = document.getElementById("copyBaseUrl");
        const baseUrl = document.getElementById("baseUrl");
        const successMsg = document.getElementById("copySuccessBaseUrl");

        if (btn && baseUrl && successMsg) {
            btn.addEventListener("click", function () {
                const cleanLine = (el) => {
                    return el.textContent.trim().replace(/\s+=\s+/, " = ");
                };

                const textToCopy = [
                    cleanLine(baseUrl),
                ].join("\n");

                navigator.clipboard.writeText(textToCopy).then(() => {
                    successMsg.classList.remove("d-none");
                    successMsg.classList.add("d-inline-block");

                    setTimeout(() => {
                        successMsg.classList.remove("d-inline-block");
                        successMsg.classList.add("d-none");
                    }, 2000);
                }).catch((err) => {
                    console.error("Chyba kopírování:", err);
                });
            });
        }
    }

    // delete Order function
    function deleteOrder() {
        const checkBoxDeleteOrder = document.getElementById("checkBoxDeleteOrder");
        const deleteOrderButton = document.getElementById("deleteOrderButton")

        if (!checkBoxDeleteOrder && !deleteOrderButton) {
            return
        }
        checkBoxDeleteOrder.addEventListener("change", function () {
            if (checkBoxDeleteOrder.checked) {
                deleteOrderButton.classList.remove("disabled")
            } else {
                deleteOrderButton.classList.add("disabled")
            }
        })
    }
    // zaterminovano s dopravou na Realizovano function
    function advicedRealizedOrder() {
        const checkBoxRealizovanoSDopravou = document.getElementById("checkBoxRealizovanoSDopravou");
        const realizovanoSDopracouButton = document.getElementById("realizovanoSDopracouButton")

        if (!checkBoxRealizovanoSDopravou && !realizovanoSDopracouButton) {
            return
        }
        checkBoxRealizovanoSDopravou.addEventListener("change", function () {
            if (checkBoxRealizovanoSDopravou.checked) {
                realizovanoSDopracouButton.classList.remove("disabled")
            } else {
                realizovanoSDopracouButton.classList.add("disabled")
            }
        })
    }

    // hidden Order function
    function hiddenOrder() {
        const checkBoxHiddenOrder = document.getElementById("checkBoxHiddenOrder");
        const hiddenOrderButton = document.getElementById("hiddenOrderButton")

        if (!checkBoxHiddenOrder && !hiddenOrderButton) {
            return
        }
        checkBoxHiddenOrder.addEventListener("change", function () {
            if (checkBoxHiddenOrder.checked) {
                hiddenOrderButton.classList.remove("disabled")
            } else {
                hiddenOrderButton.classList.add("disabled")
            }
        })
    }

    // delete team function
    function deleteTeam() {
        const checkBoxDeleteTeam = document.getElementById("checkBoxDeleteTeam");
        const deleteTeamButton = document.getElementById("deleteTeamButton")

        if (!checkBoxDeleteTeam && !deleteTeamButton) {
            return
        }
        checkBoxDeleteTeam.addEventListener("change", function () {
            if (checkBoxDeleteTeam.checked) {
                deleteTeamButton.classList.remove("disabled")
            } else {
                deleteTeamButton.classList.add("disabled")
            }
        })
    }
    // hlavni filter zapinani OD pole function
    function scczFilter() {
        const mandantInput = document.getElementById("mandant");
        const odWrapper = document.getElementById("obchodniDumWrapper");

        if (!mandantInput || !odWrapper) {
            return;
        }

        function toggleOD() {
            const value = mandantInput.value.trim().toUpperCase();
            if (value === "SCCZ") {
                odWrapper.classList.remove("od_inactive");
            } else {
                odWrapper.classList.add("od_inactive");
            }
        }

        toggleOD();

        mandantInput.addEventListener("input", toggleOD);
    }

    //  input vynos naklad
    function input_vynos_naklad() {
        const idStatus = document.getElementById("id_status");
        const id_naklad = document.getElementById("id_naklad");
        const id_vynos = document.getElementById("id_vynos");
        const vynosNakladProfitLoss = document.getElementById("vynosNakladProfitLoss");

        if (!idStatus || !id_naklad || !id_vynos || !vynosNakladProfitLoss) return;

        function toggleInputFields() {
            if (idStatus.value !== "New" && idStatus.value !== "Adviced") {
                id_naklad.parentElement.classList.add("vynos_naklad_input", "inactive_input");
                id_vynos.parentElement.classList.add("vynos_naklad_input", "inactive_input");
            } else {
                id_naklad.parentElement.classList.remove("vynos_naklad_input", "inactive_input");
                id_vynos.parentElement.classList.remove("vynos_naklad_input", "inactive_input");
            }
        }

        function handleInputChange() {
            updateProfitLoss(id_naklad, id_vynos, vynosNakladProfitLoss);
        }

        function handleStatusChange() {
            toggleInputFields();
        }

        // počáteční nastavení
        toggleInputFields();
        updateProfitLoss(id_naklad, id_vynos, vynosNakladProfitLoss);

        // posluchače
        id_naklad.addEventListener("input", handleInputChange);
        id_vynos.addEventListener("input", handleInputChange);
        idStatus.addEventListener("change", handleStatusChange);
    }

    function updateProfitLoss(id_naklad, id_vynos, vynosNakladProfitLoss) {
        const vynos = parseFloat(id_vynos.value) || 0;
        const naklad = parseFloat(id_naklad.value) || 0;
        const profitLoss = vynos - naklad;

        vynosNakladProfitLoss.innerHTML = profitLoss;

        vynosNakladProfitLoss.classList.remove("profit", "ztrata", "zero");

        if (profitLoss > 0) {
            vynosNakladProfitLoss.classList.add("profit");
        } else if (profitLoss < 0) {
            vynosNakladProfitLoss.classList.add("ztrata");
        } else {
            vynosNakladProfitLoss.classList.add("zero");
        }
    }

    // making dopravni zakazku
    function making_delivery_order() {
        const idMontageTermin = document.getElementById("id_montage_termin");
        const idTeamType = document.getElementById("id_team_type");
        const idTeam = document.getElementById("id_team");

        if (!idMontageTermin || !idTeamType || !idTeam) return

        function updateTeamVisibility() {
            const teamWrapper = idTeam.closest(".L-form__group");
            const montageTerminWrapper = idMontageTermin.closest(".L-form__group");

            if (idTeamType.value === "By_customer" || idTeamType.value === "By_delivery_crew") {
                teamWrapper.classList.add("inactive_input");
                montageTerminWrapper.classList.add("inactive_input");
                idTeam.value = "";
                idMontageTermin.value = "";
            } else {
                teamWrapper.classList.remove("inactive_input");
                montageTerminWrapper.classList.remove("inactive_input");
            }
        }

        // spustíme při změně
        idTeamType.addEventListener("change", function () {
            setTimeout(updateTeamVisibility, 100); // s malým delayem
        });

        // spustíme hned při načtení stránky
        updateTeamVisibility();
    }

    // detail profit
    function detailProfit() {
        const vynosNakladProfitListItem = document.getElementById("vynosNakladProfitListItem")
        const detailProfit = document.getElementById("detailProfit")

        if (!vynosNakladProfitListItem) return

        let detailProfitValue = parseFloat(detailProfit.textContent.trim())
        detailProfit.classList.remove("profit", "ztrata", "zero");

        if (detailProfitValue > 0) {
            detailProfit.classList.add("profit");
        } else if (detailProfitValue < 0) {
            detailProfit.classList.add("ztrata");
        } else {
            detailProfit.classList.add("zero");
        }
    }
    // galerie lightbox
    lightbox.option({
        'resizeDuration': 200,
        'imageFadeDuration': 200,
        'wrapAround': true,
        "fitImagesInViewport": true,
    })

})();