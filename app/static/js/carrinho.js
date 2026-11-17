function toastCarrinho(titulo, msg, tipo = "sucesso") {
    const ant = document.querySelector(".toast-aviso");
    if (ant) ant.remove();
    const t = document.createElement("div");
    t.className = `toast-aviso ${tipo}`;
    t.innerHTML = `<strong>${titulo}</strong><span>${msg}</span>`;
    document.body.appendChild(t);
    setTimeout(() => {
        t.style.opacity = "0";
        t.style.transition = "opacity .4s ease";
        setTimeout(() => t.remove(), 400);
    }, 3000);
}

document.addEventListener("DOMContentLoaded", () => {
    renderizarCarrinho();
    carregarMeusPedidos();

    const btnFinalizar = document.getElementById("btn-finalizar");
    if (btnFinalizar) {
        btnFinalizar.addEventListener("click", finalizarPedido);
    }
});

function renderizarCarrinho() {
    const area = document.getElementById("area-carrinho");
    const btnFinalizar = document.getElementById("btn-finalizar");
    if (!area) return;

    const carrinho = JSON.parse(localStorage.getItem("carrinho") || "[]");

    if (!carrinho.length) {
        area.innerHTML = `
        <div style="text-align:center; padding: 2.5rem 1.5rem; background: var(--creme); border: 2px dashed var(--rosa); border-radius: 20px; margin: 1rem 0;">
            <div style="font-size: 2.8rem; margin-bottom: .4rem;">🛒</div>
            <h3 style="font-size: 1.4rem; margin-bottom: .3rem;">Seu carrinho está vazio</h3>
            <p style="opacity: .85; margin-bottom: 1rem;">Adicione doces, bolos ou salgados do nosso cardápio para fazer seu pedido!</p>
            <a href="/cardapio" class="btn btn-vinho">Ver Cardápio</a>
        </div>`;
        if (btnFinalizar) btnFinalizar.style.display = "none";
        return;
    }

    if (btnFinalizar) btnFinalizar.style.display = "inline-block";

    let totalGeral = 0;
    const linhas = carrinho.map((item, idx) => {
        const subtotal = Number(item.valor) * Number(item.quantidade);
        totalGeral += subtotal;
        return `
        <tr>
            <td><strong>${item.nome}</strong></td>
            <td>R$ ${Number(item.valor).toFixed(2)}</td>
            <td>
                <button class="btn" style="margin:0; padding:.25rem .65rem;" onclick="alterarQtdCarrinho(${idx}, -1)">-</button>
                <strong style="margin: 0 .6rem;">${item.quantidade}</strong>
                <button class="btn" style="margin:0; padding:.25rem .65rem;" onclick="alterarQtdCarrinho(${idx}, 1)">+</button>
            </td>
            <td><strong>R$ ${subtotal.toFixed(2)}</strong></td>
            <td>
                <button class="btn" style="margin:0; padding:.35rem .8rem; background:#FADBD8; color:#922B21;" onclick="removerItemCarrinho(${idx})">Remover</button>
            </td>
        </tr>`;
    }).join("");

    area.innerHTML = `
    <table>
        <thead>
            <tr>
                <th>Produto</th>
                <th>Valor Unit.</th>
                <th>Quantidade</th>
                <th>Subtotal</th>
                <th>Ação</th>
            </tr>
        </thead>
        <tbody>
            ${linhas}
            <tr>
                <td colspan="3" style="text-align:right;"><strong>Total do Pedido:</strong></td>
                <td colspan="2"><strong style="font-size:1.2rem; color:var(--vinho);">R$ ${totalGeral.toFixed(2)}</strong></td>
            </tr>
        </tbody>
    </table>`;
}

function alterarQtdCarrinho(index, delta) {
    let carrinho = JSON.parse(localStorage.getItem("carrinho") || "[]");
    if (!carrinho[index]) return;

    carrinho[index].quantidade += delta;
    if (carrinho[index].quantidade <= 0) {
        carrinho.splice(index, 1);
    }

    localStorage.setItem("carrinho", JSON.stringify(carrinho));
    if (typeof atualizarBadgeCarrinho === "function") atualizarBadgeCarrinho();
    renderizarCarrinho();
}

function removerItemCarrinho(index) {
    let carrinho = JSON.parse(localStorage.getItem("carrinho") || "[]");
    carrinho.splice(index, 1);
    localStorage.setItem("carrinho", JSON.stringify(carrinho));
    if (typeof atualizarBadgeCarrinho === "function") atualizarBadgeCarrinho();
    renderizarCarrinho();
    toastCarrinho("Removido", "Item retirado do carrinho.");
}

async function finalizarPedido() {
    const carrinho = JSON.parse(localStorage.getItem("carrinho") || "[]");
    if (!carrinho.length) return;

    const resumoItens = carrinho.map(i => `${i.quantidade}x ${i.nome}`).join(", ");
    const total = carrinho.reduce((acc, i) => acc + (Number(i.valor) * Number(i.quantidade)), 0);

    try {
        const res = await fetch("/api/pedidos/criar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                itens: resumoItens,
                produtos: carrinho,
                valor_total: total
            })
        });
        const data = await res.json();

        if (data.sucesso) {
            localStorage.removeItem("carrinho");
            if (typeof atualizarBadgeCarrinho === "function") atualizarBadgeCarrinho();
            renderizarCarrinho();
            carregarMeusPedidos();
            toastCarrinho("🎉 Pedido Realizado!", data.mensagem || "Seu pedido foi enviado para a cozinha!");
        } else {
            toastCarrinho("Atenção", data.mensagem || "Faça login para finalizar o pedido.", "erro");
        }
    } catch (erro) {
        console.error(erro);
        toastCarrinho("Erro", "Não foi possível enviar o pedido.", "erro");
    }
}

async function carregarMeusPedidos() {
    const el = document.getElementById("lista-meus-pedidos");
    if (!el) return;

    try {
        const res = await fetch("/api/pedidos/meus?t=" + Date.now(), { cache: "no-store" });
        if (!res.ok) {
            el.innerHTML = "<p>Nenhum pedido realizado ainda.</p>";
            return;
        }
        const data = await res.json();
        const lista = data.pedidos || [];

        if (!lista.length) {
            el.innerHTML = "<p>Nenhum pedido realizado ainda.</p>";
            return;
        }

        el.innerHTML = `
        <div class="table-wrap">
            <table>
                <thead><tr><th>#</th><th>Itens</th><th>Total</th><th>Status do Pedido</th></tr></thead>
                <tbody>
                    ${lista.map(p => {
                        let statusHtml = `<span class="badge badge-preparo">⏳ ${p.status}</span>`;
                        if (p.status === "Em Preparo") {
                            statusHtml = `<span class="badge badge-preparo">👩‍🍳 Em Preparo na Cozinha</span>`;
                        } else if (p.status === "Pronto") {
                            statusHtml = `<span class="badge badge-pronto" style="background:#D4EFDF;color:#145A32;padding:.4rem .8rem;border-radius:12px;font-weight:700;">✅ Pronto! Pode vir buscar na loja!</span>`;
                        }
                        return `
                        <tr>
                            <td><strong>#${p.id}</strong></td>
                            <td>${p.itens}</td>
                            <td>R$ ${Number(p.valor_total || 0).toFixed(2)}</td>
                            <td>${statusHtml}</td>
                        </tr>`;
                    }).join("")}
                </tbody>
            </table>
        </div>`;
    } catch {
        el.innerHTML = "<p>Nenhum pedido realizado ainda.</p>";
    }
}