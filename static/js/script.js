(function () {
    console.log("script.js");
    const html = document.documentElement;
    const themeToggler = document.getElementById("themeToggler");
    const orderTable = document.getElementById("orderTable");
    const teamTable = document.getElementById("teamTable");
    const articleTable = document.getElementById("articleTable");
    const numberInputs = document.querySelectorAll(".number");
    const messages = $(".C-messages");
    const arcticleBtn = $('.toggle-btn');

    messages.each(function (index, element) {
        setTimeout(function () {
            $(element).fadeOut(1000, function () {
                $(this).remove();
            });
        }, 5000);
    });
    // articles
    arcticleBtn.on('click', function () {
        $(this).next('.L-form__articles__fieldset').slideToggle();
    });


// validace tel num v inputech  v HTMX
document.body.addEventListener('htmx:afterSwap', function () {

    let numberInputs = document.querySelectorAll(".number");
    console.log(numberInputs);

    numberInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
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

}) ();




