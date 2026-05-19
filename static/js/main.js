document.addEventListener("DOMContentLoaded", () => {
    const venueSelect = document.getElementById("id_venue");
    const venueButtons = document.querySelectorAll("[data-select-venue]");

    if (!venueSelect || venueButtons.length === 0) {
        return;
    }

    venueButtons.forEach((button) => {
        button.addEventListener("click", () => {
            venueSelect.value = button.getAttribute("data-select-venue");
            venueSelect.dispatchEvent(new Event("change"));
            venueSelect.scrollIntoView({ behavior: "smooth", block: "center" });
            venueSelect.focus();
        });
    });
});
