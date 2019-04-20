$(document).ready(function() {
    localStorage.getItem("mode") === "dark" ? $("body").addClass("dark-mode") : $("body").removeClass("dark-mode");
});

function toggleDarkMode(){
    const previousValue = localStorage.getItem("mode") || "dark";
    localStorage.setItem("mode", previousValue === "dark" ? "light" : "dark");
    localStorage.getItem("mode") === "dark" ? $("body").addClass("dark-mode") : $("body").removeClass("dark-mode");
}
