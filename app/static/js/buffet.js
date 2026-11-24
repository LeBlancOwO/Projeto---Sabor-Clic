// Reserva de cozinha (calendário). Depende de main.js.

document.addEventListener("DOMContentLoaded", () => {
    const inputMes = document.getElementById("mes-buffet");
    const modal = document.getElementById("modal-reserva");
    const formReserva = document.getElementById("form-modal-reserva");
    if (!modal || !formReserva) return;

    const hoje = new Date();
    const mesAtualISO = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, "0")}`;

    if (inputMes) {
        inputMes.value = mesAtualISO;
        inputMes.min = mesAtualISO;
        carregarCalendario(mesAtualISO);
        inputMes.addEventListener("change", () => {
            if (inputMes.value) carregarCalendario(inputMes.value);
        });
    }

    const fecharModal = () => modal.classList.remove("aberto");
    document.getElementById("fechar-modal").addEventListener("click", fecharModal);
    document.getElementById("cancelar-modal").addEventListener("click", fecharModal);
    modal.addEventListener("click", (e) => { if (e.target === modal) fecharModal(); });

    formReserva.addEventListener("submit", async (e) => {
        e.preventDefault();

        const { data } = await apiJson("/api/buffet/reservar", "POST", {
            data_evento: document.getElementById("reserva-data-iso").value,
            tipo_evento: document.getElementById("reserva-tipo").value,
            qtd_convidados: document.getElementById("reserva-convidados").value
        });

        fecharModal();

        if (data.sucesso) {
            mostrarToast("🎉 Reserva Confirmada!", data.mensagem, "sucesso", 3500);
        } else {
            mostrarToast("Data Indisponível", data.mensagem || "Não foi possível reservar.", "erro", 3500);
        }
        if (inputMes && inputMes.value) carregarCalendario(inputMes.value);
    });
});

async function carregarCalendario(mesAno) {
    const grid = document.getElementById("calendario-buffet");
    if (!grid || !mesAno) return;

    let ocupadas = [];
    const { ok, data } = await api(`/api/buffet/datas-ocupadas?mes=${encodeURIComponent(mesAno)}`);
    if (ok) {
        ocupadas = data.ocupadas || [];
    } else {
        console.warn("Não foi possível carregar datas ocupadas, exibindo calendário livre.");
    }

    const [ano, mes] = mesAno.split("-").map(Number);
    const totalDias = new Date(ano, mes, 0).getDate();
    grid.innerHTML = "";

    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);

    for (let d = 1; d <= totalDias; d++) {
        const dataFormatada = `${ano}-${String(mes).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
        const isPassado = new Date(ano, mes - 1, d) < hoje;
        const isOcupado = ocupadas.includes(dataFormatada);

        const box = document.createElement("div");

        if (isPassado) {
            box.className = "dia-box dia-passado";
            box.innerHTML = `<strong>${d}</strong><br><small>Encerrado</small>`;
        } else if (isOcupado) {
            box.className = "dia-box dia-ocupado";
            box.innerHTML = `<strong>${d}</strong><br><small>Ocupado</small>`;
        } else {
            box.className = "dia-box dia-livre";
            box.innerHTML = `<strong>${d}</strong><br><small>Livre</small>`;
            box.addEventListener("click", () => abrirModalReserva(dataFormatada, d, mes, ano));
        }

        grid.appendChild(box);
    }
}

function abrirModalReserva(dataISO, dia, mes, ano) {
    document.getElementById("reserva-data-iso").value = dataISO;
    document.getElementById("modal-data-texto").textContent =
        `Data selecionada: ${String(dia).padStart(2, "0")}/${String(mes).padStart(2, "0")}/${ano}`;
    document.getElementById("modal-reserva").classList.add("aberto");
}