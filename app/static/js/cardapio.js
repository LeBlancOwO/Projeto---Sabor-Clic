let pratosCache = [];

function toastCardapio(titulo, msg, tipo = "sucesso") {
    const ant = document.querySelector(".toast-aviso");
    if (ant) ant.remove();
    const t = document.createElement("div");
    t.className = `toast-aviso ${tipo}`;
    t.innerHTML = `<strong>${titulo}</strong><span>${msg}</span>`;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2500);
}

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/api/cardapio/listar");
        const data = await res.json();
        pratosCache = data.pratos || [];
        renderizarCards(pratosCache);
    } catch (erro) {
        console.error("Erro ao carregar cardápio:", erro);
        renderizarCards([]);
    }

    const inputFiltro = document.getElementById("filtro-cardapio");
    if (inputFiltro) {
        inputFiltro.addEventListener("input", (e) => {
            const termo = e.target.value.toLowerCase();
            const filtrados = pratosCache.filter(p =>
                p.nome.toLowerCase().includes(termo) ||
                p.ingredientes.toLowerCase().includes(termo) ||
                p.categoria.toLowerCase().includes(termo)
            );
            renderizarCards(filtrados);
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
        const esgotado = p.quantidade <= 0;
        return `
        <div class="produto-card">
            <div class="produto-img-wrap">
                <img src="${p.foto}" alt="${p.nome}" onerror="this.src='/static/imagens/doces.jpg'">
                <span class="produto-qtd-badge ${esgotado ? 'esgotado' : ''}">
                    ${esgotado ? 'Esgotado' : `${p.quantidade} disp.`}
                </span>
            </div>
            <div class="produto-info">
                <h3 class="produto-titulo">${p.nome}</h3>
                <p class="produto-subtitulo">${p.ingredientes}</p>
                <div class="produto-rodape">
                    <span class="produto-preco">R$ ${Number(p.valor).toFixed(2)}</span>
                    <button class="btn btn-vinho" ${esgotado ? 'disabled style="opacity:.5;cursor:not-allowed;"' : ''}
                        onclick="adicionarCarrinho(${p.id}, '${p.nome.replace(/'/g, "\\'")}', ${p.valor}, ${p.quantidade})">
                        ${esgotado ? 'Indisponível' : '+ Carrinho'}
                    </button>
                </div>
            </div>
        </div>`;
    }).join("");
}

function adicionarCarrinho(id, nome, valor, estoqueMax) {
    if (typeof USUARIO_LOGADO !== "undefined" && !USUARIO_LOGADO) {
        sessionStorage.setItem("item_pendente_carrinho", JSON.stringify({
            id: id,
            nome: nome,
            valor: Number(valor),
            quantidade: 1
        }));
        window.location.href = "/login?aviso=carrinho";
        return;
    }

    let carrinho = JSON.parse(localStorage.getItem("carrinho") || "[]");
    const item = carrinho.find(i => i.id === id);

    if (item) {
        if (estoqueMax && item.quantidade >= estoqueMax) {
            toastCardapio("Estoque Limite", "Você atingiu a quantidade máxima disponível.", "erro");
            return;
        }
        item.quantidade += 1;
    } else {
        carrinho.push({ id, nome, valor: Number(valor), quantidade: 1 });
    }

    localStorage.setItem("carrinho", JSON.stringify(carrinho));
    if (typeof atualizarBadgeCarrinho === "function") atualizarBadgeCarrinho();
    window.location.href = "/carrinho";
}