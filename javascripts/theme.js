// Apply a theme
function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);

    // Save theme across pages
    localStorage.setItem("theme", theme);
}

// Restore saved theme on page load
const savedTheme = localStorage.getItem("theme");

if (savedTheme) {
    document.documentElement.setAttribute("data-theme", savedTheme);
}

// Button listeners
document.getElementById("gt-button").addEventListener("click", () => {
    setTheme("gt");
});

document.getElementById("cu-button").addEventListener("click", () => {
    setTheme("cu");
});

console.log("Saved theme:", localStorage.getItem("theme"));