// Carrinho e "Meus pedidos". Depende de main.js.

const TAXA_ENTREGA = 8.00; // só para exibir a prévia; o servidor recalcula

function lerCarrinho() {
    try {
        const c = JSON.parse(localStorage.getItem("carrinho") || "[]");
        return Array.isArray(c) ? c : [];
    } catch {
        return [];
    }
}

function salvarCarrinho(carrinho) {
    localStorage.setItem("carrinho", JSON.stringify(carrinho));
    atualizarBadgeCarrinho();
}

function getTipoEntregaSelecionado() {
    const selecionado = document.querySelector('input[name="tipo_entrega"]:checked');
    return selecionado ? selecionado.value : "Retirada";
}

document.addEventListener("DOMContentLoaded", () => {
    renderizarCarrinho();
    carregarMeusPedidos();

    const boxEndereco = document.getElementById("campo-endereco-entrega");
    document.querySelectorAll('input[name="tipo_entrega"]').forEach(radio => {
        radio.addEventListener("change", () => {
            if (boxEndereco) boxEndereco.style.display = radio.value === "Entrega" ? "block" : "none";
            renderizarCarrinho();
        });
    });

    const btnFinalizar = document.getElementById("btn-finalizar");
    if (btnFinalizar) btnFinalizar.addEventListener("click", finalizarPedido);

    // Botões da tabela do carrinho (+, -, remover)
    const area = document.getElementById("area-carrinho");
    if (area) {
        area.addEventListener("click", (e) => {
            const btn = e.target.closest("[data-acao]");
            if (!btn) return;
            const idx = Number(btn.dataset.idx);
            if (btn.dataset.acao === "mais") alterarQtdCarrinho(idx, 1);
            else if (btn.dataset.acao === "menos") alterarQtdCarrinho(idx, -1);
            else if (btn.dataset.acao === "remover") removerItemCarrinho(idx);
        });
    }
});

function renderizarCarrinho() {
    const area = document.getElementById("area-carrinho");
    const btnFinalizar = document.getElementById("btn-finalizar");
    const blocoEntrega = document.getElementById("bloco-entrega");
    if (!area) return;

    const carrinho = lerCarrinho();

    if (!carrinho.length) {
        area.innerHTML = `
        <div style="text-align:center; padding: 2.5rem 1.5rem; background: var(--creme); border: 2px dashed var(--rosa); border-radius: 20px; margin: 1rem 0;">
            <div style="font-size: 2.8rem; margin-bottom: .4rem;">🛒</div>
            <h3 style="font-size: 1.4rem; margin-bottom: .3rem;">Seu carrinho está vazio</h3>
            <p style="opacity: .85; margin-bottom: 1rem;">Adicione doces, bolos ou salgados do nosso cardápio para fazer seu pedido!</p>
            <a href="/cardapio" class="btn btn-vinho">Ver Cardápio</a>
        </div>`;
        if (btnFinalizar) btnFinalizar.style.display = "none";
        if (blocoEntrega) blocoEntrega.style.display = "none";
        return;
    }

    if (btnFinalizar) btnFinalizar.style.display = "inline-block";
    if (blocoEntrega) blocoEntrega.style.display = "block";

    const tipoEntrega = getTipoEntregaSelecionado();
    const frete = tipoEntrega === "Entrega" ? TAXA_ENTREGA : 0;

    let subtotalProdutos = 0;
    const linhas = carrinho.map((item, idx) => {
        const subtotal = Number(item.valor) * Number(item.quantidade);
        subtotalProdutos += subtotal;
        return `
        <tr>
            <td><strong>${esc(item.nome)}</strong></td>
            <td>R$ ${Number(item.valor).toFixed(2)}</td>
            <td>
                <button type="button" class="btn" data-acao="menos" data-idx="${idx}" style="margin:0; padding:.25rem .65rem;">-</button>
                <strong style="margin: 0 .6rem;">${Number(item.quantidade)}</strong>
                <button type="button" class="btn" data-acao="mais" data-idx="${idx}" style="margin:0; padding:.25rem .65rem;">+</button>
            </td>
            <td><strong>R$ ${subtotal.toFixed(2)}</strong></td>
            <td>
                <button type="button" class="btn" data-acao="remover" data-idx="${idx}"
                    style="margin:0; padding:.35rem .8rem; background:#FADBD8; color:#922B21;">Remover</button>
            </td>
        </tr>`;
    }).join("");

    const totalGeral = subtotalProdutos + frete;

    area.innerHTML = `
    <table>
        <thead>
            <tr><th>Produto</th><th>Valor Unit.</th><th>Quantidade</th><th>Subtotal</th><th>Ação</th></tr>
        </thead>
        <tbody>
            ${linhas}
            <tr>
                <td colspan="3" style="text-align:right;">Taxa de Entrega (${esc(tipoEntrega)}):</td>
                <td colspan="2"><strong>${frete > 0 ? `R$ ${frete.toFixed(2)}` : "Grátis"}</strong></td>
            </tr>
            <tr>
                <td colspan="3" style="text-align:right;"><strong>Total do Pedido:</strong></td>
                <td colspan="2"><strong style="font-size:1.2rem; color:var(--vinho);">R$ ${totalGeral.toFixed(2)}</strong></td>
            </tr>
        </tbody>
    </table>`;
}

function alterarQtdCarrinho(index, delta) {
    const carrinho = lerCarrinho();
    if (!carrinho[index]) return;

    carrinho[index].quantidade += delta;
    if (carrinho[index].quantidade <= 0) carrinho.splice(index, 1);

    salvarCarrinho(carrinho);
    renderizarCarrinho();
}

function removerItemCarrinho(index) {
    const carrinho = lerCarrinho();
    carrinho.splice(index, 1);
    salvarCarrinho(carrinho);
    renderizarCarrinho();
    mostrarToast("Removido", "Item retirado do carrinho.", "sucesso", 2500);
}

async function finalizarPedido() {
    const carrinho = lerCarrinho();
    if (!carrinho.length) return;

    const tipoEntrega = getTipoEntregaSelecionado();
    const enderecoInput = document.getElementById("endereco-entrega");
    const enderecoEntrega = enderecoInput ? enderecoInput.value.trim() : "";

    if (tipoEntrega === "Entrega" && enderecoEntrega.length < 6) {
        mostrarToast("Endereço Obrigatório", "Digite o endereço completo para entrega.", "erro");
        if (enderecoInput) enderecoInput.focus();
        return;
    }

    const btn = document.getElementById("btn-finalizar");
    if (btn) btn.disabled = true;

    // Só id e quantidade: nome, preço e total são calculados no servidor
    const { data } = await apiJson("/api/pedidos/criar", "POST", {
        produtos: carrinho.map(i => ({ id: i.id, quantidade: i.quantidade })),
        tipo_entrega: tipoEntrega,
        endereco_entrega: enderecoEntrega
    });

    if (btn) btn.disabled = false;

    if (data.sucesso) {
        localStorage.removeItem("carrinho");
        atualizarBadgeCarrinho();
        renderizarCarrinho();
        carregarMeusPedidos();
        const total = Number(data.total || 0).toFixed(2);
        mostrarToast("🎉 Pedido Realizado!", `${data.mensagem} Total: R$ ${total}`);
    } else {
        mostrarToast("Atenção", data.mensagem || "Não foi possível enviar o pedido.", "erro");
    }
}

function badgeStatus(status) {
    switch (status) {
        case "Em Preparo":
            return `<span class="badge badge-preparo">👩‍🍳 Em Preparo na Cozinha</span>`;
        case "Saiu para Entrega":
            return `<span class="badge badge-preparo" style="background:#D6EAF8;color:#1B4F72;">🛵 Saiu para Entrega</span>`;
        case "Pronto":
            return `<span class="badge badge-pronto">✅ Concluído / Pronto!</span>`;
        default:
            return `<span class="badge badge-aguardando">⏳ ${esc(status)}</span>`;
    }
}

async function carregarMeusPedidos() {
    const el = document.getElementById("lista-meus-pedidos");
    if (!el) return;

    const { ok, data } = await api("/api/pedidos/meus", { cache: "no-store" });
    const lista = ok ? (data.pedidos || []) : [];

    if (!lista.length) {
        el.innerHTML = "<p>Nenhum pedido realizado ainda.</p>";
        return;
    }

    el.innerHTML = `
    <div class="table-wrap">
        <table>
            <thead><tr><th>#</th><th>Itens</th><th>Entrega</th><th>Total</th><th>Status do Pedido</th></tr></thead>
            <tbody>
                ${lista.map(p => `
                <tr>
                    <td><strong>#${p.id}</strong></td>
                    <td>${esc(p.itens)}</td>
                    <td><strong>${esc(p.tipo_entrega)}</strong><br><small>${esc(p.endereco_entrega || "")}</small></td>
                    <td>R$ ${Number(p.valor_total || 0).toFixed(2)}</td>
                    <td>${badgeStatus(p.status)}</td>
                </tr>`).join("")}
            </tbody>
        </table>
    </div>`;
}