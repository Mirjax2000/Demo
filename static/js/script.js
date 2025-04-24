(function () {
    console.log("script.js");
    const html = document.documentElement;
    const themeToggler = document.getElementById("themeToggler");
    const leftSide = document.getElementById("leftSide");
    const navLinks = leftSide.querySelectorAll(".L-sidebar__nav-link");

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
        localStorage.setItem("theme", newTheme); // Uložení tématu
    }

    themeToggler.addEventListener("click", toggleTheme);
})();
