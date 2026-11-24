// Cardápio. Depende de main.js.

let pratosCache = [];

document.addEventListener("DOMContentLoaded", async () => {
    const grid = document.getElementById("grid-cardapio");
    const inputFiltro = document.getElementById("filtro-cardapio");

    const { ok, data } = await api("/api/cardapio/listar");
    pratosCache = ok ? (data.pratos || []) : [];
    renderizarCards(pratosCache);

    // Filtro com debounce (não redesenha a cada tecla)
    if (inputFiltro) {
        let timer;
        inputFiltro.addEventListener("input", (e) => {
            clearTimeout(timer);
            timer = setTimeout(() => {
                const termo = e.target.value.toLowerCase().trim();
                renderizarCards(pratosCache.filter(p =>
                    p.nome.toLowerCase().includes(termo) ||
                    p.ingredientes.toLowerCase().includes(termo) ||
                    p.categoria.toLowerCase().includes(termo)
                ));
            }, 200);
        });
    }

    // Clique em "+ Carrinho"
    if (grid) {
        grid.addEventListener("click", (e) => {
            const btn = e.target.closest(".js-add-carrinho");
            if (!btn || btn.disabled) return;
            const prato = pratosCache.find(p => p.id === Number(btn.dataset.id));
            if (prato) adicionarCarrinho(prato);
        });
    }
});

function renderizarCards(lista) {
    const grid = document.getElementById("grid-cardapio");
    if (!grid) return;

    if (!lista.length) {
        grid.style.display = "block";
        grid.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon-circle">🧁</div>
            <h3>Ainda não temos produtos no cardápio</h3>
            <p>Em breve teremos deliciosos doces, bolos e salgados disponíveis por aqui!</p>
        </div>`;
        return;
    }

    grid.style.display = "grid";
    grid.innerHTML = lista.map(p => {
        const indisponivel = p.quantidade <= 0 || !p.ativo;
        const rotuloBadge = p.quantidade <= 0 ? "Esgotado" : (!p.ativo ? "Inativo" : `${p.quantidade} disp.`);
        return `
        <div class="produto-card">
            <div class="produto-img-wrap">
                <img src="${esc(p.foto)}" alt="${esc(p.nome)}" onerror="this.src='/static/imagens/doces.jpg'">
                <span class="produto-qtd-badge ${indisponivel ? "esgotado" : ""}">${rotuloBadge}</span>
            </div>
            <div class="produto-info">
                <h3 class="produto-titulo">${esc(p.nome)}</h3>
                <p class="produto-subtitulo">${esc(p.ingredientes)}</p>
                <div class="produto-rodape">
                    <span class="produto-preco">R$ ${Number(p.valor).toFixed(2)}</span>
                    <button type="button" class="btn btn-vinho js-add-carrinho" data-id="${p.id}"
                        ${indisponivel ? 'disabled style="opacity:.5;cursor:not-allowed;"' : ""}>
                        ${indisponivel ? "Indisponível" : "+ Carrinho"}
                    </button>
                </div>
            </div>
        </div>`;
    }).join("");
}

function lerCarrinho() {
    try {
        const c = JSON.parse(localStorage.getItem("carrinho") || "[]");
        return Array.isArray(c) ? c : [];
    } catch {
        return [];
    }
}

function adicionarCarrinho(prato) {
    const novoItem = { id: prato.id, nome: prato.nome, valor: Number(prato.valor), quantidade: 1 };

    // Visitante sem login: guarda o item e leva para o login
    if (typeof USUARIO_LOGADO !== "undefined" && !USUARIO_LOGADO) {
        sessionStorage.setItem("item_pendente_carrinho", JSON.stringify(novoItem));
        window.location.href = "/login?aviso=carrinho";
        return;
    }

    const carrinho = lerCarrinho();
    const item = carrinho.find(i => i.id === prato.id);

    if (item) {
        if (prato.quantidade && item.quantidade >= prato.quantidade) {
            mostrarToast("Estoque Limite", "Você atingiu a quantidade máxima disponível.", "erro", 2500);
            return;
        }
        item.quantidade += 1;
    } else {
        carrinho.push(novoItem);
    }

    localStorage.setItem("carrinho", JSON.stringify(carrinho));
    atualizarBadgeCarrinho();
    window.location.href = "/carrinho";
}