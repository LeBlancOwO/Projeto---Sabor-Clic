// ===== Utilitários globais (usados por todas as páginas) =====

// Escapa texto antes de colocar em innerHTML (evita XSS)
function esc(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, c => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
}

function mostrarToast(titulo, mensagem, tipo = "sucesso", duracao = 3200) {
    const anterior = document.querySelector(".toast-aviso");
    if (anterior) anterior.remove();

    const toast = document.createElement("div");
    toast.className = `toast-aviso ${tipo}`;
    toast.innerHTML = `<strong>${esc(titulo)}</strong><span>${esc(mensagem)}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity .4s ease";
        setTimeout(() => toast.remove(), 400);
    }, duracao);
}

// Modal de confirmação estilizado. Uso:
//   if (!await confirmar({ titulo: "...", mensagem: "...", perigo: true })) return;
function confirmar({
    titulo = "Tem certeza?",
    mensagem = "",
    textoConfirmar = "Confirmar",
    textoCancelar = "Cancelar",
    icone = "⚠️",
    perigo = false
} = {}) {
    return new Promise((resolve) => {
        const focoAnterior = document.activeElement;

        const overlay = document.createElement("div");
        overlay.className = "modal-overlay";
        overlay.setAttribute("role", "dialog");
        overlay.setAttribute("aria-modal", "true");
        overlay.setAttribute("aria-labelledby", "confirmar-titulo");
        overlay.innerHTML = `
        <div class="modal-box confirmar-box">
            <div class="confirmar-icone" aria-hidden="true">${esc(icone)}</div>
            <h3 id="confirmar-titulo">${esc(titulo)}</h3>
            <p class="confirmar-mensagem">${esc(mensagem)}</p>
            <div class="modal-acoes">
                <button type="button" class="btn" data-acao="cancelar">${esc(textoCancelar)}</button>
                <button type="button" class="btn ${perigo ? "btn-perigo" : "btn-vinho"}" data-acao="confirmar">${esc(textoConfirmar)}</button>
            </div>
        </div>`;

        const fechar = (resultado) => {
            document.removeEventListener("keydown", aoTeclar);
            overlay.remove();
            if (focoAnterior && focoAnterior.focus) focoAnterior.focus();
            resolve(resultado);
        };

        const aoTeclar = (e) => {
            if (e.key === "Escape") {
                fechar(false);
            } else if (e.key === "Tab") {
                // Mantém o foco dentro do modal
                const botoes = overlay.querySelectorAll("button");
                const primeiro = botoes[0];
                const ultimo = botoes[botoes.length - 1];
                if (e.shiftKey && document.activeElement === primeiro) {
                    e.preventDefault();
                    ultimo.focus();
                } else if (!e.shiftKey && document.activeElement === ultimo) {
                    e.preventDefault();
                    primeiro.focus();
                }
            }
        };

        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) return fechar(false); // clique fora
            const btn = e.target.closest("[data-acao]");
            if (btn) fechar(btn.dataset.acao === "confirmar");
        });

        document.addEventListener("keydown", aoTeclar);
        document.body.appendChild(overlay);
        overlay.classList.add("aberto");
        overlay.querySelector('[data-acao="cancelar"]').focus(); // foco no botão seguro
    });
}

function atualizarBadgeCarrinho() {
    let carrinho = [];
    try {
        carrinho = JSON.parse(localStorage.getItem("carrinho") || "[]");
    } catch {
        carrinho = [];
    }
    const total = carrinho.reduce((soma, item) => soma + Number(item.quantidade || 1), 0);

    const seletores = [
        document.getElementById("carrinho-contador"),
        document.getElementById("cart-count"),
        document.querySelector(".carrinho-badge"),
        document.querySelector(".badge-carrinho"),
        document.querySelector('a[href="/carrinho"] span')
    ];
    seletores.forEach(el => { if (el) el.textContent = total; });
}

// ===== Inicialização =====
document.addEventListener("DOMContentLoaded", () => {
    atualizarBadgeCarrinho();

    // 1. Modo claro/escuro (o cookie é gravado pelo servidor)
    const btnTheme = document.getElementById("toggle-theme");
    if (btnTheme) {
        btnTheme.addEventListener("click", async () => {
            const isDark = document.body.classList.toggle("dark-mode");
            const tema = isDark ? "escuro" : "claro";
            try {
                await fetch("/api/auth/preferencias", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ tema })
                });
            } catch (e) {
                console.warn("Não foi possível salvar o tema:", e);
            }
        });
    }

    // 2. Logout (limpa o carrinho local para o próximo usuário)
    const btnLogout = document.getElementById("btn-logout");
    if (btnLogout) {
        btnLogout.addEventListener("click", async (e) => {
            e.preventDefault();
            try {
                await fetch("/api/auth/logout", { method: "POST" });
            } finally {
                localStorage.removeItem("carrinho");
                sessionStorage.removeItem("item_pendente_carrinho");
                window.location.href = "/login";
            }
        });
    }
});

// Sincroniza o contador se o carrinho mudar em outra aba
window.addEventListener("storage", (e) => {
    if (e.key === "carrinho") atualizarBadgeCarrinho();
});

// ===== Requisições =====
async function api(url, opcoes = {}) {
    try {
        const res = await fetch(url, opcoes);
        let data = {};
        try { data = await res.json(); } catch { /* resposta sem JSON */ }

        if (!data.mensagem) {
            if (res.status === 401) data.mensagem = "Sua sessão expirou. Faça login novamente.";
            else if (res.status === 403) data.mensagem = "Você não tem permissão para esta ação.";
            else if (res.status >= 500) data.mensagem = "Erro no servidor. Tente novamente.";
        }
        return { ok: res.ok, status: res.status, data };
    } catch (erro) {
        console.error(erro);
        return { ok: false, status: 0, data: { sucesso: false, mensagem: "Falha de conexão com o servidor." } };
    }
}

function apiJson(url, metodo, corpo) {
    return api(url, {
        method: metodo,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(corpo ?? {})
    });
}