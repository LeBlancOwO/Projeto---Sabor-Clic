// Painel do administrador. Depende de main.js e produtos.js.

let usuariosCache = [];

document.addEventListener("DOMContentLoaded", () => {
    carregarUsuarios();
    carregarReservasAdmin();
    carregarBloqueios();
    carregarLogs();

    // ----- Usuários: busca e troca de cargo -----
    const inputBusca = document.getElementById("busca-usuario");
    if (inputBusca) {
        inputBusca.addEventListener("input", (e) => {
            const termo = e.target.value.toLowerCase();
            renderizarUsuarios(usuariosCache.filter(u =>
                u.usuario.toLowerCase().includes(termo) ||
                u.email.toLowerCase().includes(termo) ||
                u.nome.toLowerCase().includes(termo)
            ));
        });
    }

    const boxUsuarios = document.getElementById("adm-usuarios");
    if (boxUsuarios) {
        boxUsuarios.addEventListener("change", async (e) => {
            const select = e.target.closest(".js-cargo");
            if (!select) return;
            const { data } = await apiJson(`/api/admin/usuarios/${select.dataset.id}/cargo`, "PUT", { nivel_acesso: select.value });
            mostrarToast(data.sucesso ? "Permissão Atualizada" : "Ação Bloqueada", data.mensagem || "", data.sucesso ? "sucesso" : "erro");
            carregarUsuarios();
            carregarLogs();
        });
    }

    // ----- Reservas: cancelar -----
    const boxReservas = document.getElementById("adm-reservas");
    if (boxReservas) {
        boxReservas.addEventListener("click", async (e) => {
            const btn = e.target.closest(".js-cancelar-reserva");
            if (!btn) return;
            if (!confirm("Cancelar esta reserva e avisar o cliente por e-mail?")) return;
            btn.disabled = true;
            const { data } = await api(`/api/admin/reservas/${btn.dataset.id}/cancelar`, { method: "DELETE" });
            mostrarToast(data.sucesso ? "Reserva Cancelada" : "Erro", data.mensagem || "", data.sucesso ? "sucesso" : "erro");
            carregarReservasAdmin();
            carregarBloqueios();
            carregarLogs();
        });
    }

    // ----- Bloqueios: liberar data -----
    const boxBloqueios = document.getElementById("adm-bloqueios");
    if (boxBloqueios) {
        boxBloqueios.addEventListener("click", async (e) => {
            const btn = e.target.closest(".js-liberar-data");
            if (!btn) return;
            const { data } = await api(`/api/admin/bloqueios/${btn.dataset.id}`, { method: "DELETE" });
            mostrarToast("Agenda Atualizada", data.mensagem || "Data liberada.", data.sucesso ? "sucesso" : "erro");
            carregarBloqueios();
        });
    }

    // ----- Bloqueios: criar -----
    const formBloquear = document.getElementById("form-bloquear-data");
    if (formBloquear) {
        formBloquear.addEventListener("submit", async (e) => {
            e.preventDefault();
            const { data } = await apiJson("/api/admin/bloqueios", "POST", {
                data_bloqueada: document.getElementById("data-bloqueio").value,
                motivo: document.getElementById("motivo-bloqueio").value
            });
            mostrarToast(data.sucesso ? "Data Bloqueada" : "Aviso", data.mensagem || "", data.sucesso ? "sucesso" : "erro");
            if (data.sucesso) {
                formBloquear.reset();
                carregarBloqueios();
            }
        });
    }
});

// ===== 1. Usuários e Cargos =====
async function carregarUsuarios() {
    const { ok, data } = await api("/api/admin/usuarios");
    if (!ok) {
        const el = document.getElementById("adm-usuarios");
        if (el) el.innerHTML = "<p>Não foi possível carregar os usuários.</p>";
        return;
    }
    usuariosCache = data.usuarios || [];
    renderizarUsuarios(usuariosCache);
}

function renderizarUsuarios(lista) {
    const el = document.getElementById("adm-usuarios");
    if (!el) return;

    const opcao = (valor, rotulo, atual) =>
        `<option value="${valor}" ${atual === valor ? "selected" : ""}>${rotulo}</option>`;

    el.innerHTML = `
    <table>
        <thead><tr><th>Nome</th><th>Usuário</th><th>E-mail</th><th>Cargo Atual</th><th>Alterar Permissão</th></tr></thead>
        <tbody>
            ${lista.map(u => `
            <tr>
                <td>${esc(u.nome)}</td>
                <td><strong>@${esc(u.usuario)}</strong></td>
                <td>${esc(u.email)}</td>
                <td><span class="badge badge-preparo">${esc(u.nivel_acesso)}</span></td>
                <td>
                    <select class="js-cargo" data-id="${u.id}" style="padding:.4rem; border-radius:10px;">
                        ${opcao("cliente", "Cliente", u.nivel_acesso)}
                        ${opcao("cozinheiro", "Cozinheiro", u.nivel_acesso)}
                        ${opcao("administrador", "Administrador", u.nivel_acesso)}
                    </select>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>`;
}

// ===== 3. Reservas de Buffet =====
async function carregarReservasAdmin() {
    const el = document.getElementById("adm-reservas");
    if (!el) return;

    const { ok, data } = await api("/api/admin/reservas");
    if (!ok) {
        el.innerHTML = "<p>Não foi possível carregar as reservas.</p>";
        return;
    }

    const lista = data.reservas || [];
    el.innerHTML = lista.length ? `
    <table>
        <thead><tr><th>Data</th><th>Cliente</th><th>Contato & CPF</th><th>Finalidade / Turno</th><th>Equipe</th><th>Ação</th></tr></thead>
        <tbody>
            ${lista.map(r => `
            <tr>
                <td><strong>${esc(r.data_evento)}</strong></td>
                <td>${esc(r.cliente_nome)}<br><small>@${esc(r.cliente_usuario)}</small></td>
                <td>${esc(r.cliente_email)}<br><small>CPF: ${esc(r.cliente_cpf)}</small></td>
                <td>${esc(r.tipo_evento)}</td>
                <td>${Number(r.qtd_convidados)} pessoas</td>
                <td>
                    <button type="button" class="btn js-cancelar-reserva" data-id="${r.id}"
                        style="margin:0;padding:.4rem .9rem;background:#FADBD8;color:#922B21;">Cancelar & Avisar</button>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>` : "<p>Nenhuma reserva agendada ainda.</p>";
}

// ===== 4. Bloqueio de Datas na Agenda =====
async function carregarBloqueios() {
    const el = document.getElementById("adm-bloqueios");
    if (!el) return;

    const { ok, data } = await api("/api/admin/bloqueios");
    if (!ok) {
        el.innerHTML = "<p>Não foi possível carregar os bloqueios.</p>";
        return;
    }

    const lista = data.bloqueios || [];
    el.innerHTML = lista.length ? `
    <table>
        <thead><tr><th>Data Bloqueada</th><th>Motivo</th><th>Ação</th></tr></thead>
        <tbody>
            ${lista.map(b => `
            <tr>
                <td><strong>${esc(b.data_bloqueada)}</strong></td>
                <td>${esc(b.motivo)}</td>
                <td>
                    <button type="button" class="btn js-liberar-data" data-id="${b.id}"
                        style="margin:0;padding:.4rem .9rem;">Liberar Data</button>
                </td>
            </tr>`).join("")}
        </tbody>
    </table>` : "<p>Nenhuma data bloqueada manualmente.</p>";
}

// ===== 5. Logs de Auditoria =====
async function carregarLogs() {
    const el = document.getElementById("adm-logs");
    if (!el) return;

    const { ok, data } = await api("/api/admin/logs");
    if (!ok) {
        el.innerHTML = "<p>Não foi possível carregar os logs.</p>";
        return;
    }

    el.innerHTML = `
    <table>
        <thead><tr><th>Data/Hora</th><th>Usuário</th><th>Nível</th><th>Ação</th></tr></thead>
        <tbody>
            ${(data.logs || []).map(l => `
            <tr>
                <td>${esc(l.data_hora)}</td>
                <td>${esc(l.usuario_nome)}</td>
                <td>${esc(l.nivel_acesso)}</td>
                <td>${esc(l.acao)}</td>
            </tr>`).join("")}
        </tbody>
    </table>`;
}