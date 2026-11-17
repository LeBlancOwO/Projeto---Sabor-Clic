let pratosCache = [];

function toastCardapio(titulo, msg) {
    const ant = document.querySelector(".toast-aviso");
    if (ant) ant.remove();
    const t = document.createElement("div");
    t.className = "toast-aviso sucesso";
    t.innerHTML = `<strong>${titulo}</strong><span>${msg}</span>`;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2500);
}

document.addEventListener("DOMContentLoaded", async () => {
    const res = await fetch("/api/cardapio/listar");
    const data = await res.json();
    pratosCache = data.pratos || [];
    renderizarCards(pratosCache);

    document.getElementById("filtro-cardapio").addEventListener("input", (e) => {
        const termo = e.target.value.toLowerCase();
        const filtrados = pratosCache.filter(p =>
            p.nome.toLowerCase().includes(termo) ||
            p.ingredientes.toLowerCase().includes(termo) ||
            p.categoria.toLowerCase().includes(termo)
        );
        renderizarCards(filtrados);
    });
});

function renderizarCards(lista) {
    const grid = document.getElementById("grid-cardapio");
    if (!lista.length) {
        grid.style.display = "block";
        grid.innerHTML = `
        <div style="text-align:center; padding: 3.5rem 1.5rem; background: var(--creme); border: 2px dashed var(--rosa); border-radius: 24px; margin-top: 1rem;">
            <div style="font-size: 3.2rem; margin-bottom: .5rem;">🍰</div>
            <h3 style="font-size: 1.6rem; margin-bottom: .4rem;">Nosso cardápio está sendo preparado!</h3>
            <p style="max-width: 460px; margin: 0 auto; opacity: .85;">
                Ainda não encontramos delícias cadastradas para esta busca. Volte em instantes para conferir nossas novidades artesanais!
            </p>
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
                        onclick="adicionarCarrinho(${p.id}, '${p.nome.replace(/'/g, "\\'")}', ${p.valor})">
                        ${esgotado ? 'Indisponível' : '+ Carrinho'}
                    </button>
                </div>
            </div>
        </div>`;
    }).join("");
}

function adicionarCarrinho(id, nome, valor) {
    let carrinho = JSON.parse(localStorage.getItem("carrinho") || "[]");
    const item = carrinho.find(i => i.id === id);
    if (item) item.quantidade += 1;
    else carrinho.push({ id, nome, valor, quantidade: 1 });
    localStorage.setItem("carrinho", JSON.stringify(carrinho));
    if (typeof atualizarBadgeCarrinho === "function") atualizarBadgeCarrinho();
    toastCardapio("Adicionado!", `${nome} foi para o seu carrinho.`);
}