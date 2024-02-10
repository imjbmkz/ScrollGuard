
function switchTheme() {
    // Get the dark mode toggle, the html tag, and all buttons
    const darkModeToggle = document.getElementById("flexSwitchCheckChecked");
    const htmlTag = document.querySelector("html");
    const buttons = document.getElementsByClassName("btn");

    console.log(buttons.length);

    // Light mode configuration
    let data_bs_theme = "";
    let class_name = "btn btn-lg btn-dark";

    // Switch to dark mode if the toggle is checked
    if (darkModeToggle.checked) {
        data_bs_theme = "dark";
        class_name = "btn btn-lg btn-light";
    } 

    // Apply toggled theme
    htmlTag.setAttribute("data-bs-theme", data_bs_theme);
    for (let button of buttons) {
        button.setAttribute("class", class_name);
    }
}