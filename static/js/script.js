(function () {
    console.log("script.js");
    const html = document.documentElement;
    const themeToggler = document.getElementById("themeToggler");
    const leftSide = document.getElementById("leftSide");
    const navLinks = leftSide.querySelectorAll(".L-sidebar__nav-link");

    // navlinky prepinani classy L-active
    navLinks.forEach((link) => {
        link.addEventListener("click", () => {
            navLinks.forEach((l) => l.classList.remove("L-active"));
            link.classList.add("L-active");
        });
    });

    function toggleTheme() {
        const current = html.dataset.theme;
        html.dataset.theme = current === "light" ? "dark" : "light";
    }

    themeToggler.addEventListener("click", toggleTheme);
})();
