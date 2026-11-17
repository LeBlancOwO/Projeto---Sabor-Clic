function avisoBuffet(titulo, mensagem, tipo = "sucesso") {
    const anterior = document.querySelector(".toast-aviso");
    if (anterior) anterior.remove();

    const toast = document.createElement("div");
    toast.className = `toast-aviso ${tipo}`;
    toast.innerHTML = `<strong>${titulo}</strong><span>${mensagem}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity .4s ease";
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}

document.addEventListener("DOMContentLoaded", () => {
    const inputMes = document.getElementById("mes-buffet");
    const modal = document.getElementById("modal-reserva");
    const formReserva = document.getElementById("form-modal-reserva");

    const hoje = new Date();
    const mesAtualISO = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, "0")}`;
    
    if (inputMes) {
        inputMes.value = mesAtualISO;
        inputMes.min = mesAtualISO;
        carregarCalendario(mesAtualISO);
        inputMes.addEventListener("change", () => carregarCalendario(inputMes.value));
    }

    const fecharModal = () => modal.classList.remove("aberto");
    document.getElementById("fechar-modal").addEventListener("click", fecharModal);
    document.getElementById("cancelar-modal").addEventListener("click", fecharModal);
    modal.addEventListener("click", (e) => {
        if (e.target === modal) fecharModal();
    });

    formReserva.addEventListener("submit", async (e) => {
        e.preventDefault();
        const dataEvento = document.getElementById("reserva-data-iso").value;
        const tipoEvento = document.getElementById("reserva-tipo").value;
        const qtdConvidados = document.getElementById("reserva-convidados").value;

        try {
            const res = await fetch("/api/buffet/reservar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    data_evento: dataEvento,
                    tipo_evento: tipoEvento,
                    qtd_convidados: qtdConvidados
                })
            });
            const data = await res.json();
            fecharModal();

            if (data.sucesso) {
                avisoBuffet("🎉 Reserva Confirmada!", data.mensagem, "sucesso");
                carregarCalendario(inputMes.value);
            } else {
                avisoBuffet("Data Indisponível", data.mensagem, "erro");
            }
        } catch (erro) {
            console.error(erro);
            avisoBuffet("Erro de Conexão", "Não foi possível registrar sua reserva.", "erro");
        }
    });
});

async function carregarCalendario(mesAno) {
    const grid = document.getElementById("calendario-buffet");
    if (!grid || !mesAno) return;

    let ocupadas = [];
    try {
        const res = await fetch(`/api/buffet/datas-ocupadas?mes=${mesAno}`);
        if (res.ok) {
            const data = await res.json();
            ocupadas = data.ocupadas || [];
        }
    } catch (erro) {
        console.warn("Não foi possível carregar datas ocupadas, exibindo calendário livre:", erro);
    }

    const [ano, mes] = mesAno.split("-").map(Number);
    const totalDias = new Date(ano, mes, 0).getDate();
    grid.innerHTML = "";

    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);

    for (let d = 1; d <= totalDias; d++) {
        const dataFormatada = `${ano}-${String(mes).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
        const dataObj = new Date(ano, mes - 1, d);
        const isPassado = dataObj < hoje;
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