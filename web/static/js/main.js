const cards = document.querySelectorAll(".movie-card, .metric-card, .explain-card, .panel");

cards.forEach((card) => {
    card.addEventListener("mousemove", (event) => {
        const rect = card.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;
        card.style.background = `radial-gradient(circle at ${x}% ${y}%, rgba(34, 211, 238, 0.12), transparent 28%), rgba(18, 24, 46, 0.76)`;
    });

    card.addEventListener("mouseleave", () => {
        card.style.background = "";
    });
});

const form = document.querySelector(".recommendation-form");

if (form) {
    form.addEventListener("submit", (event) => {
        const button = form.querySelector("button[type='submit']");
        button.textContent = "Analizando afinidad...";
        button.disabled = true;
    });
}
