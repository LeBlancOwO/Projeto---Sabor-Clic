document.addEventListener("DOMContentLoaded", () => {
    // 1. Alternar Modo Claro/Escuro via Cookie
    const btnTheme = document.getElementById("toggle-theme");
    if (btnTheme) {
        btnTheme.addEventListener("click", async () => {
            const isDark = document.body.classList.toggle("dark-mode");
            const tema = isDark ? "escuro" : "claro";
            document.cookie = `tema_preferido=${tema}; path=/; max-age=31536000`;
            await fetch("/api/auth/preferencias", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tema })
            });
        });
    }

    // 2. Logout
    const btnLogout = document.getElementById("btn-logout");
    if (btnLogout) {
        btnLogout.addEventListener("click", async (e) => {
            e.preventDefault();
            await fetch("/api/auth/logout", { method: "POST" });
            window.location.href = "/login";
        });
    }
});

function atualizarBadgeCarrinho() {
    const carrinho = JSON.parse(localStorage.getItem("carrinho") || "[]");
    const totalUnidades = carrinho.reduce((soma, item) => soma + Number(item.quantidade || 1), 0);

    // Procura o contador por ID, classe ou dentro do link do carrinho
    const seletores = [
        document.getElementById("carrinho-contador"),
        document.getElementById("cart-count"),
        document.querySelector(".carrinho-badge"),
        document.querySelector(".badge-carrinho"),
        document.querySelector('a[href="/carrinho"] span')
    ];

    seletores.forEach(el => {
        if (el) el.textContent = totalUnidades;
    });
}

document.addEventListener("DOMContentLoaded", () => {
    atualizarBadgeCarrinho();
});

// Sincroniza se o carrinho mudar em outra aba
window.addEventListener("storage", (e) => {
    if (e.key === "carrinho") atualizarBadgeCarrinho();
});