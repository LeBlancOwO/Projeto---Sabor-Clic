let usuariosCache = [];

function toastAdmin(titulo, msg, tipo = "sucesso") {
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
    }, 3200);
}

document.addEventListener("DOMContentLoaded", () => {
    carregarUsuarios();
    carregarProdutosGestao();
    carregarReservasAdmin();
    carregarBloqueios();
    carregarLogs();

    // Busca dinâmica de usuários por nome, usuário ou e-mail
    const inputBusca = document.getElementById("busca-usuario");
    if (inputBusca) {
        inputBusca.addEventListener("input", (e) => {
            const termo = e.target.value.toLowerCase();
            const filtrados = usuariosCache.filter(u =>
                u.usuario.toLowerCase().includes(termo) ||
                u.email.toLowerCase().includes(termo) ||
                u.nome.toLowerCase().includes(termo)
            );
            renderizarUsuarios(filtrados);
        });
    }

    // Cadastro de produtos (com foto por arquivo ou link + estoque)
    const formProduto = document.getElementById("form-produto-gestao");
    if (formProduto) {
        formProduto.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const res = await fetch("/api/cardapio/adicionar", { method: "POST", body: formData });
            const data = await res.json();
            toastAdmin(data.sucesso ? "Sucesso!" : "Erro", data.mensagem, data.sucesso ? "sucesso" : "erro");
            if (data.sucesso) {
                e.target.reset();
                carregarProdutosGestao();
                carregarLogs();
            }
        });
    }

    // Bloqueio manual de datas no calendário do buffet
    const formBloquear = document.getElementById("form-bloquear-data");
    if (formBloquear) {
        formBloquear.addEventListener("submit", async (e) => {
            e.preventDefault();
            const res = await fetch("/api/admin/bloqueios", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    data_bloqueada: document.getElementById("data-bloqueio").value,
                    motivo: document.getElementById("motivo-bloqueio").value
                })
            });
            const data = await res.json();
            toastAdmin(data.sucesso ? "Data Bloqueada" : "Aviso", data.mensagem, data.sucesso ? "sucesso" : "erro");
            if (data.sucesso) {
                e.target.reset();
                carregarBloqueios();
            }
        });
    }
});

// ===== 1. Usuários e Cargos =====
async function carregarUsuarios() {
    const res = await fetch("/api/admin/usuarios");
    const data = await res.json();
    usuariosCache = data.usuarios || [];
    renderizarUsuarios(usuariosCache);
}

function renderizarUsuarios(lista) {
    const el = document.getElementById("adm-usuarios");
    if (!el) return;
    el.innerHTML = `
    <table>
        <thead><tr><th>Nome</th><th>Usuário</th><th>E-mail</th><th>Cargo Atual</th><th>Alterar Permissão</th></tr></thead>
        <tbody>
            ${lista.map(u => `
            <tr>
                <td>${u.nome}</td>
                <td><strong>@${u.usuario}</strong></td>
                <td>${u.email}</td>
                <td><span class="badge badge-preparo">${u.nivel_acesso}</span></td>
                <td>
                    <select onchange="alterarCargoUsuario(${u.id}, this.value)" style="padding:.4rem; border-radius:10px;">
                        <option value="cliente" ${u.nivel_acesso === 'cliente' ? 'selected' : ''}>Cliente</option>
                        <option value="cozinheiro" ${u.nivel_acesso === 'cozinheiro' ? 'selected' : ''}>Cozinheiro</option>
                        <option value="administrador" ${u.nivel_acesso === 'administrador' ? 'selected' : ''}>Administrador</option>
                    </select>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>`;
}

async function alterarCargoUsuario(id, novoNivel) {
    const res = await fetch(`/api/admin/usuarios/${id}/cargo`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nivel_acesso: novoNivel })
    });
    const data = await res.json();
    toastAdmin("Permissão Atualizada", data.mensagem);
    carregarUsuarios();
    carregarLogs();
}

// ===== 2. Produtos e Estoque =====
async function carregarProdutosGestao() {
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
                        onchange="atualizarEstoqueProduto(${p.id}, this.value)">
                </td>
                <td>
                    <button class="btn" style="margin:0;padding:.4rem .9rem;background:#FADBD8;color:#922B21;" onclick="excluirProduto(${p.id})">Excluir</button>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>`;
}

async function atualizarEstoqueProduto(id, qtd) {
    await fetch(`/api/cardapio/quantidade/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantidade: qtd })
    });
    toastAdmin("Estoque Salvo", "Quantidade atualizada no cardápio.");
}

async function excluirProduto(id) {
    await fetch(`/api/cardapio/remover/${id}`, { method: "DELETE" });
    toastAdmin("Excluído", "Produto removido do cardápio.");
    carregarProdutosGestao();
    carregarLogs();
}

// ===== 3. Reservas de Buffet =====
async function carregarReservasAdmin() {
    const res = await fetch("/api/admin/reservas");
    const data = await res.json();
    const lista = data.reservas || [];
    const el = document.getElementById("adm-reservas");
    if (!el) return;
    el.innerHTML = lista.length ? `
    <table>
        <thead><tr><th>Data Evento</th><th>Cliente</th><th>Contato & CPF</th><th>Evento</th><th>Convidados</th><th>Ação</th></tr></thead>
        <tbody>
            ${lista.map(r => `
            <tr>
                <td><strong>${r.data_evento}</strong></td>
                <td>${r.cliente_nome}<br><small>@${r.cliente_usuario}</small></td>
                <td>${r.cliente_email}<br><small>CPF: ${r.cliente_cpf}</small></td>
                <td>${r.tipo_evento}</td>
                <td>${r.qtd_convidados} pessoas</td>
                <td>
                    <button class="btn" style="margin:0;padding:.4rem .9rem;background:#FADBD8;color:#922B21;"
                        onclick="cancelarReservaAdmin(${r.id})">Cancelar & Avisar</button>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>` : "<p>Nenhuma reserva agendada ainda.</p>";
}

async function cancelarReservaAdmin(id) {
    const res = await fetch(`/api/admin/reservas/${id}/cancelar`, { method: "DELETE" });
    const data = await res.json();
    toastAdmin(data.sucesso ? "Reserva Cancelada" : "Erro", data.mensagem, data.sucesso ? "sucesso" : "erro");
    carregarReservasAdmin();
    carregarLogs();
}

// ===== 4. Bloqueio de Datas na Agenda =====
async function carregarBloqueios() {
    const res = await fetch("/api/admin/bloqueios");
    const data = await res.json();
    const lista = data.bloqueios || [];
    const el = document.getElementById("adm-bloqueios");
    if (!el) return;
    el.innerHTML = lista.length ? `
    <table>
        <thead><tr><th>Data Bloqueada</th><th>Motivo</th><th>Ação</th></tr></thead>
        <tbody>
            ${lista.map(b => `
            <tr>
                <td><strong>${b.data_bloqueada}</strong></td>
                <td>${b.motivo}</td>
                <td>
                    <button class="btn" style="margin:0;padding:.4rem .9rem;" onclick="liberarDataAdmin(${b.id})">Liberar Data</button>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>` : "<p>Nenhuma data bloqueada manualmente.</p>";
}

async function liberarDataAdmin(id) {
    const res = await fetch(`/api/admin/bloqueios/${id}`, { method: "DELETE" });
    const data = await res.json();
    toastAdmin("Agenda Atualizada", data.mensagem);
    carregarBloqueios();
}

// ===== 5. Logs de Auditoria =====
async function carregarLogs() {
    const res = await fetch("/api/admin/logs");
    const data = await res.json();
    const el = document.getElementById("adm-logs");
    if (!el) return;
    el.innerHTML = `
    <table>
        <thead><tr><th>Data/Hora</th><th>Usuário</th><th>Nível</th><th>Ação</th></tr></thead>
        <tbody>
            ${(data.logs || []).map(l => `
            <tr><td>${l.data_hora}</td><td>${l.usuario_nome}</td><td>${l.nivel_acesso}</td><td>${l.acao}</td></tr>`).join("")}
        </tbody>
    </table>`;
}