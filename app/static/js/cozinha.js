// Painel da cozinha. Depende de main.js e produtos.js.

document.addEventListener("DOMContentLoaded", () => {
    carregarPedidosCozinha();
    carregarEstoqueCozinha();
    carregarReservasCozinha();

    // ----- Pedidos: mudar status -----
    const boxPedidos = document.getElementById("cozinha-pedidos");
    if (boxPedidos) {
        boxPedidos.addEventListener("change", async (e) => {
            const select = e.target.closest(".js-status-pedido");
            if (!select) return;
            const { data } = await apiJson(`/api/pedidos/status/${select.dataset.id}`, "PUT", { status: select.value });
            mostrarToast(
                data.sucesso ? "Status Atualizado" : "Erro",
                data.sucesso ? `Pedido #${select.dataset.id} marcado como: ${select.value}` : (data.mensagem || "Não foi possível atualizar."),
                data.sucesso ? "sucesso" : "erro"
            );
            carregarPedidosCozinha();
        });
    }

    // ----- Insumos: alterar quantidade / remover -----
    const boxEstoque = document.getElementById("cozinha-estoque");
    if (boxEstoque) {
        boxEstoque.addEventListener("change", async (e) => {
            const input = e.target.closest(".js-insumo-qtd");
            if (!input) return;
            const { data } = await apiJson(`/api/cozinha/estoque/${input.dataset.id}`, "PUT", { quantidade: input.value });
            mostrarToast(data.sucesso ? "Insumo Atualizado" : "Erro", data.mensagem || "", data.sucesso ? "sucesso" : "erro");
            carregarEstoqueCozinha();
        });

        boxEstoque.addEventListener("click", async (e) => {
            const btn = e.target.closest(".js-insumo-remover");
            if (!btn) return;
            if (!confirm("Remover este insumo da lista?")) return;
            const { data } = await api(`/api/cozinha/estoque/${btn.dataset.id}`, { method: "DELETE" });
            mostrarToast(data.sucesso ? "Removido" : "Erro", data.mensagem || "Insumo excluído.", data.sucesso ? "sucesso" : "erro");
            carregarEstoqueCozinha();
        });
    }

    // ----- Insumos: cadastrar -----
    const formEstoque = document.getElementById("form-estoque");
    if (formEstoque) {
        formEstoque.addEventListener("submit", async (e) => {
            e.preventDefault();
            const { data } = await apiJson("/api/cozinha/estoque", "POST", {
                insumo: document.getElementById("insumo-nome").value,
                quantidade: document.getElementById("insumo-qtd").value,
                unidade: document.getElementById("insumo-un").value
            });
            mostrarToast(data.sucesso ? "Insumo Salvo" : "Atenção", data.mensagem || "", data.sucesso ? "sucesso" : "erro");
            if (data.sucesso) {
                formEstoque.reset();
                carregarEstoqueCozinha();
            }
        });
    }
});

async function carregarPedidosCozinha() {
    const el = document.getElementById("cozinha-pedidos");
    if (!el) return;

    const { ok, data } = await api("/api/pedidos/listar");
    if (!ok) {
        el.innerHTML = "<p>Não foi possível carregar os pedidos.</p>";
        return;
    }

    const lista = data.pedidos || [];
    const opcao = (valor, rotulo, atual) =>
        `<option value="${valor}" ${atual === valor ? "selected" : ""}>${rotulo}</option>`;

    el.innerHTML = lista.length ? `
    <table>
        <thead><tr><th>#</th><th>Cliente</th><th>Itens</th><th>Total</th><th>Entrega</th><th>Status</th><th>Atualizar Etapa</th></tr></thead>
        <tbody>
            ${lista.map(p => `
            <tr>
                <td><strong>#${p.id}</strong></td>
                <td>${esc(p.cliente_nome)}</td>
                <td>${esc(p.itens)}</td>
                <td>R$ ${Number(p.valor_total || 0).toFixed(2)}</td>
                <td><strong>${esc(p.tipo_entrega || "Retirada")}</strong><br><small>${esc(p.endereco_entrega || "")}</small></td>
                <td><strong>${esc(p.status)}</strong></td>
                <td>
                    <select class="js-status-pedido" data-id="${p.id}" style="padding:.4rem; border-radius:10px;">
                        ${opcao("Aguardando", "Aguardando", p.status)}
                        ${opcao("Em Preparo", "Em Preparo", p.status)}
                        ${opcao("Saiu para Entrega", "Saiu para Entrega", p.status)}
                        ${opcao("Pronto", "Pronto / Entregue", p.status)}
                    </select>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>` : "<p>Nenhum pedido na fila da cozinha.</p>";
}

async function carregarEstoqueCozinha() {
    const el = document.getElementById("cozinha-estoque");
    if (!el) return;

    const { ok, data } = await api("/api/cozinha/estoque");
    if (!ok) {
        el.innerHTML = "<p>Não foi possível carregar os insumos.</p>";
        return;
    }

    const lista = data.estoque || [];
    el.innerHTML = lista.length ? `
    <table>
        <thead><tr><th>Insumo</th><th>Quantidade Salva</th><th>Unidade</th><th>Ação</th></tr></thead>
        <tbody>
            ${lista.map(i => `
            <tr>
                <td><strong>${esc(i.insumo)}</strong></td>
                <td>
                    <input type="number" min="0" step="0.1" value="${Number(i.quantidade)}" data-id="${i.id}"
                        class="js-insumo-qtd" style="width:85px;padding:.35rem;border-radius:8px;">
                </td>
                <td>${esc(i.unidade)}</td>
                <td>
                    <button type="button" class="btn js-insumo-remover" data-id="${i.id}"
                        style="margin:0;padding:.35rem .8rem;background:#FADBD8;color:#922B21;">Remover</button>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>` : "<p>Nenhum insumo cadastrado ainda.</p>";
}

async function carregarReservasCozinha() {
    const el = document.getElementById("cozinha-reservas");
    if (!el) return;

    const { ok, data } = await api("/api/cozinha/reservas");
    if (!ok) {
        el.innerHTML = "<p>Não foi possível carregar as reservas.</p>";
        return;
    }

    const lista = data.reservas || [];
    el.innerHTML = lista.length ? `
    <table>
        <thead><tr><th>Data Evento</th><th>Cliente</th><th>Tipo de Evento</th><th>Convidados</th><th>Status</th></tr></thead>
        <tbody>
            ${lista.map(r => `
            <tr>
                <td><strong>${esc(r.data_evento)}</strong></td>
                <td>${esc(r.cliente_nome)}</td>
                <td>${esc(r.tipo_evento)}</td>
                <td>${Number(r.qtd_convidados)} pessoas</td>
                <td><span class="badge badge-pronto">${esc(r.status)}</span></td>
            </tr>`).join("")}
        </tbody>
    </table>` : "<p>Nenhuma reserva de cozinha agendada no momento.</p>";
}