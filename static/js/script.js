(function () {
    console.log("script.js");
    const html = document.documentElement;
    const themeToggler = document.getElementById("themeToggler");
    const leftSide = document.getElementById("leftSide");
    const navLinks = leftSide.querySelectorAll(".L-sidebar__nav-link");
    const content = document.getElementById("content");



    // Navlinky - přepínání classy L-active
    navLinks.forEach((link) => {
        link.addEventListener("click", () => {
            navLinks.forEach((l) => l.classList.remove("L-active"));
            link.classList.add("L-active");
        });
    });

    function toggleTheme() {
        const current = html.dataset.theme;
        const newTheme = current === "light" ? "dark" : "light";

        html.dataset.theme = newTheme;

        localStorage.setItem("theme", newTheme);

        html.classList.remove(current); // odeber staré téma
        html.classList.add(newTheme);   // přidej nové téma
    }

    themeToggler.addEventListener("click", toggleTheme);
    // 
    //  nastaveni opacity kdyz zapisujeme do searche
    content.addEventListener("input", function (event) {
        if (event.target && event.target.id === "inputSearch") {
            const inputSearch = event.target;
            const orderTable = document.getElementById("orderTable")
            if (inputSearch.value.length >= 1) {
                orderTable.dataset.opacity = "half"; // Nastaví hodnotu data-opacity na "half"
            } else {
                orderTable.dataset.opacity = "full"; // Nastaví hodnotu data-opacity na "full"
            }
        }
    });

    if (content) {
        content.addEventListener('htmx:load', function () {
            const inputSearch = content.querySelector("#inputSearch");
            const orderTable = content.querySelector("#orderTable");
            if (inputSearch && orderTable) {
                if (inputSearch.value.length === 0) {
                    orderTable.dataset.opacity = "full";
                    console.log("HTMX obsah načten a zpracován");
                }
            }
            if (orderTable) {
                $(orderTable).DataTable({
                    paging: false,
                    rowReorder: true,
                    fixedColumns: true,
                    layout: {
                        topEnd: null
                    }
                });
            }
        });

    }
})();




