(function () {
    console.log("script.js");
    const html = document.documentElement;
    const themeToggler = document.getElementById("themeToggler")

    function toggleTheme() {
        const current = html.dataset.theme;
        html.dataset.theme = current === "light" ? "dark" : "light";
    }

    themeToggler.addEventListener("click", toggleTheme)


})();