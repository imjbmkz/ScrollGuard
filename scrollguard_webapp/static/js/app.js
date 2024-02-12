function switchTheme() {
    // Get the dark mode toggle, the html tag, and all buttons
    const htmlTag = document.querySelector("html");
    const darkModeToggle = document.getElementById("flexSwitchCheckChecked");
    const button = document.getElementById("btnDemo");
    const links = document.getElementsByTagName("a");

    // Light mode configuration
    let data_bs_theme = "";
    let button_class = "btn btn-lg btn-dark";
    let link_class = "link-secondary"

    // Switch to dark mode if the toggle is checked
    if (darkModeToggle.checked) {
        data_bs_theme = "dark";
        button_class = "btn btn-lg btn-light";
        link_class = "link-light";
    } 

    // Apply toggled theme
    htmlTag.setAttribute("data-bs-theme", data_bs_theme);
    // for (let button of buttons) {
    //     button.setAttribute("class", button_class);
    // }
    button.setAttribute("class", button_class)
    for (let link of links) {
        if (link.hasAttribute("class")) {
            if (link.getAttribute("class").startsWith("link-")) {
                link.setAttribute("class", link_class);
            }
        }
    }
}