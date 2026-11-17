function toastCozinha(titulo, msg, tipo = "sucesso") {
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
    carregarPedidosCozinha();
    carregarProdutosCozinha();
    carregarEstoqueCozinha();
    carregarReservasCozinha();

    const formProduto = document.getElementById("form-produto-gestao");
    if (formProduto) {
        formProduto.addEventListener("submit", async (e) => {
            e.preventDefault();
            try {
                const inputArquivo = formProduto.querySelector('input[name="foto_arquivo"]');
                const temArquivo = inputArquivo && inputArquivo.files && inputArquivo.files.length > 0;

                let res;
                if (temArquivo) {
                    const formData = new FormData(formProduto);
                    res = await fetch("/api/cardapio/adicionar", { method: "POST", body: formData });
                } else {
                    res = await fetch("/api/cardapio/adicionar", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            nome: formProduto.querySelector('[name="nome"]').value,
                            categoria: formProduto.querySelector('[name="categoria"]').value,
                            ingredientes: formProduto.querySelector('[name="ingredientes"]').value,
                            valor: formProduto.querySelector('[name="valor"]').value,
                            quantidade: formProduto.querySelector('[name="quantidade"]').value,
                            foto_url: formProduto.querySelector('[name="foto_url"]').value
                        })
                    });
                }

                const data = await res.json();
                toastCozinha(data.sucesso ? "Sucesso!" : "Atenção", data.mensagem, data.sucesso ? "sucesso" : "erro");
                if (data.sucesso) {
                    formProduto.reset();
                    carregarProdutosCozinha();
                }
            } catch (erro) {
                console.error(erro);
                toastCozinha("Erro", "Falha ao cadastrar produto.", "erro");
            }
        });
    }

    const formEstoque = document.getElementById("form-estoque");
    if (formEstoque) {
        formEstoque.addEventListener("submit", async (e) => {
            e.preventDefault();
            const res = await fetch("/api/cozinha/estoque", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    insumo: document.getElementById("insumo-nome").value,
                    quantidade: document.getElementById("insumo-qtd").value,
                    unidade: document.getElementById("insumo-un").value
                })
            });
            const data = await res.json();
            if (data.sucesso) {
                toastCozinha("Insumo Salvo", data.mensagem);
                formEstoque.reset();
                carregarEstoqueCozinha();
            }
        });
    }
});

async function carregarPedidosCozinha() {
    const el = document.getElementById("cozinha-pedidos");
    if (!el) return;
    try {
        const res = await fetch("/api/pedidos/listar");
        const data = await res.json();
        const lista = data.pedidos || [];
        el.innerHTML = lista.length ? `
        <table>
            <thead><tr><th>#</th><th>Cliente</th><th>Itens</th><th>Status</th><th>Atualizar Etapa</th></tr></thead>
            <tbody>
                ${lista.map(p => `
                <tr>
                    <td><strong>#${p.id}</strong></td>
                    <td>${p.cliente_nome}</td>
                    <td>${p.itens}</td>
                    <td><strong>${p.status}</strong></td>
                    <td>
                        <select onchange="mudarStatusPedido(${p.id}, this.value)" style="padding:.4rem; border-radius:10px;">
                            <option value="Aguardando" ${p.status === 'Aguardando' ? 'selected' : ''}>Aguardando</option>
                            <option value="Em Preparo" ${p.status === 'Em Preparo' ? 'selected' : ''}>Em Preparo</option>
                            <option value="Pronto" ${p.status === 'Pronto' ? 'selected' : ''}>Pronto (Avisar Cliente)</option>
                        </select>
                    </td>
                </tr>`).join("")}
            </tbody>
        </table>` : "<p>Nenhum pedido pendente na fila da cozinha.</p>";
    } catch {
        el.innerHTML = "<p>Nenhum pedido pendente na fila da cozinha.</p>";
    }
}

async function mudarStatusPedido(id, status) {
    await fetch(`/api/pedidos/status/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
    });
    toastCozinha("Status Atualizado", `Pedido #${id} marcado como: ${status}`);
    carregarPedidosCozinha();
}

async function carregarProdutosCozinha() {
    const res = await fetch("/api/cardapio/listar");
    const data = await res.json();
    const el = document.getElementById("gestao-produtos-lista");
    if (!el) return;
    el.innerHTML = `
    <table>
        <thead><tr><th>Foto</th><th>Produto</th><th>Valor</th><th>Estoque</th><th>Ações</th></tr></thead>
        <tbody>
            ${(data.pratos || []).map(p => `
            <tr>
                <td><img src="${p.foto}" style="width:54px;height:54px;object-fit:cover;border-radius:10px;" onerror="this.src='/static/imagens/doces.jpg'"></td>
                <td><strong>${p.nome}</strong><br><small>${p.categoria} • ${p.ingredientes}</small></td>
                <td>R$ ${Number(p.valor).toFixed(2)}</td>
                <td>
                    <input type="number" min="0" value="${p.quantidade}" style="width:75px;padding:.35rem;border-radius:8px;"
                        onchange="atualizarEstoqueCozinha(${p.id}, this.value)">
                </td>
                <td>
                    <button class="btn" style="margin:0;padding:.4rem .9rem;background:#FADBD8;color:#922B21;" onclick="excluirProdutoCozinha(${p.id})">Excluir</button>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>`;
}

async function atualizarEstoqueCozinha(id, qtd) {
    await fetch(`/api/cardapio/quantidade/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantidade: qtd })
    });
    toastCozinha("Estoque Salvo", "Quantidade atualizada!");
}

async function excluirProdutoCozinha(id) {
    await fetch(`/api/cardapio/remover/${id}`, { method: "DELETE" });
    toastCozinha("Excluído", "Produto removido do cardápio.");
    carregarProdutosCozinha();
}

async function carregarEstoqueCozinha() {
    const el = document.getElementById("cozinha-estoque");
    if (!el) return;
    try {
        const res = await fetch("/api/cozinha/estoque");
        const data = await res.json();
        const lista = data.estoque || [];
        el.innerHTML = lista.length ? `
        <table>
            <thead><tr><th>Insumo</th><th>Quantidade Salva</th><th>Unidade</th><th>Ação</th></tr></thead>
            <tbody>
                ${lista.map(e => `
                <tr>
                    <td><strong>${e.insumo}</strong></td>
                    <td>${e.quantidade}</td>
                    <td>${e.unidade}</td>
                    <td>
                        <button class="btn" style="margin:0;padding:.35rem .8rem;background:#FADBD8;color:#922B21;" onclick="removerInsumoCozinha(${e.id})">Remover</button>
                    </td>
                </tr>`).join("")}
            </tbody>
        </table>` : "<p>Nenhum insumo cadastrado ainda.</p>";
    } catch {
        el.innerHTML = "<p>Nenhum insumo cadastrado ainda.</p>";
    }
}

async function removerInsumoCozinha(id) {
    await fetch(`/api/cozinha/estoque/${id}`, { method: "DELETE" });
    toastCozinha("Removido", "Insumo excluído da lista.");
    carregarEstoqueCozinha();
}

async function carregarReservasCozinha() {
    const el = document.getElementById("cozinha-reservas");
    if (!el) return;
    try {
        const res = await fetch("/api/cozinha/reservas");
        const data = await res.json();
        const lista = data.reservas || [];
        el.innerHTML = lista.length ? `
        <table>
            <thead><tr><th>Data Evento</th><th>Cliente</th><th>Tipo de Evento</th><th>Convidados</th><th>Status</th></tr></thead>
            <tbody>
                ${lista.map(r => `
                <tr>
                    <td><strong>${r.data_evento}</strong></td>
                    <td>${r.cliente_nome}</td>
                    <td>${r.tipo_evento}</td>
                    <td>${r.qtd_convidados} pessoas</td>
                    <td><span class="badge badge-pronto">${r.status}</span></td>
                </tr>`).join("")}
            </tbody>
        </table>` : "<p>Nenhuma reserva de buffet agendada no momento.</p>";
    } catch {
        el.innerHTML = "<p>Nenhuma reserva de buffet agendada no momento.</p>";
    }
}