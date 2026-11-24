// Gestão de produtos: usada pelo painel admin e pelo painel da cozinha.
// Depende de main.js (esc, mostrarToast, api, apiJson).

async function carregarProdutosGestao() {
    const el = document.getElementById("gestao-produtos-lista");
    if (!el) return;

    const { ok, data } = await api("/api/cardapio/listar");
    if (!ok) {
        el.innerHTML = "<p>Não foi possível carregar os produtos.</p>";
        return;
    }

    const lista = data.pratos || [];
    if (!lista.length) {
        el.innerHTML = "<p>Nenhum produto cadastrado ainda.</p>";
        return;
    }

    el.innerHTML = `
    <table>
        <thead><tr><th>Foto</th><th>Produto</th><th>Valor</th><th>Estoque</th><th>Ações</th></tr></thead>
        <tbody>
            ${lista.map(p => `
            <tr>
                <td><img src="${esc(p.foto)}" alt="" style="width:54px;height:54px;object-fit:cover;border-radius:10px;" onerror="this.src='/static/imagens/doces.jpg'"></td>
                <td><strong>${esc(p.nome)}</strong><br><small>${esc(p.categoria)} • ${esc(p.ingredientes)}</small></td>
                <td>R$ ${Number(p.valor).toFixed(2)}</td>
                <td>
                    <input type="number" min="0" value="${Number(p.quantidade)}" data-id="${p.id}"
                        class="js-estoque-produto" style="width:75px;padding:.35rem;border-radius:8px;">
                </td>
                <td>
                    <button type="button" class="btn js-excluir-produto" data-id="${p.id}"
                        style="margin:0;padding:.4rem .9rem;background:#FADBD8;color:#922B21;">Excluir</button>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>`;
}

document.addEventListener("DOMContentLoaded", () => {
    const lista = document.getElementById("gestao-produtos-lista");
    const form = document.getElementById("form-produto-gestao");

    carregarProdutosGestao();

    if (lista) {
        // Alterar estoque
        lista.addEventListener("change", async (e) => {
            const input = e.target.closest(".js-estoque-produto");
            if (!input) return;
            const { data } = await apiJson(`/api/cardapio/quantidade/${input.dataset.id}`, "PUT", { quantidade: input.value });
            mostrarToast(data.sucesso ? "Estoque Salvo" : "Erro", data.mensagem || "Quantidade atualizada!", data.sucesso ? "sucesso" : "erro");
            carregarProdutosGestao();
        });

        // Excluir produto
        lista.addEventListener("click", async (e) => {
            const btn = e.target.closest(".js-excluir-produto");
            if (!btn) return;
            if (!confirm("Excluir este produto do cardápio?")) return;
            const { data } = await api(`/api/cardapio/remover/${btn.dataset.id}`, { method: "DELETE" });
            mostrarToast(data.sucesso ? "Excluído" : "Erro", data.mensagem || "Produto removido.", data.sucesso ? "sucesso" : "erro");
            carregarProdutosGestao();
            if (typeof carregarLogs === "function") carregarLogs();
        });
    }

    // Cadastrar produto (sempre FormData: o servidor aceita arquivo e/ou link)
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const botao = form.querySelector('button[type="submit"]');
            if (botao) botao.disabled = true;

            const { data } = await api("/api/cardapio/adicionar", { method: "POST", body: new FormData(form) });
            mostrarToast(data.sucesso ? "Sucesso!" : "Atenção", data.mensagem || "", data.sucesso ? "sucesso" : "erro");

            if (botao) botao.disabled = false;
            if (data.sucesso) {
                form.reset();
                carregarProdutosGestao();
                if (typeof carregarLogs === "function") carregarLogs();
            }
        });
    }
});