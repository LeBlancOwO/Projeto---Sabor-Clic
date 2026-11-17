function mostrarNotificacao(titulo, mensagem, tipo = "sucesso") {
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
    }, 3200);
}

document.addEventListener("DOMContentLoaded", () => {
    // 1. Login
    const formLogin = document.getElementById("form-login");
    if (formLogin) {
        formLogin.addEventListener("submit", async (e) => {
            e.preventDefault();
            try {
                const res = await fetch("/api/auth/logar", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        identificador: document.getElementById("identificador").value,
                        senha: document.getElementById("senha").value
                    })
                });
                const data = await res.json();
                if (data.sucesso) {
                    mostrarNotificacao(
                        `Bem-vindo(a), ${data.usuario.nome.split(" ")[0]}!`,
                        "Login realizado com sucesso. Redirecionando...",
                        "sucesso"
                    );
                    setTimeout(() => {
                        if (data.usuario.nivel_acesso === "administrador") window.location.href = "/admin";
                        else if (data.usuario.nivel_acesso === "cozinheiro") window.location.href = "/cozinha";
                        else window.location.href = "/cardapio";
                    }, 1200);
                } else {
                    mostrarNotificacao("Ops! Algo deu errado", data.mensagem, "erro");
                }
            } catch (erro) {
                console.error(erro);
                mostrarNotificacao("Erro de conexão", "Não foi possível conectar ao servidor.", "erro");
            }
        });
    }

    // 2. Cadastro
    const formCadastro = document.getElementById("form-cadastro");
    if (formCadastro) {
        formCadastro.addEventListener("submit", async (e) => {
            e.preventDefault();
            try {
                const res = await fetch("/api/auth/cadastrar", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        nome: document.getElementById("nome").value,
                        usuario: document.getElementById("usuario").value,
                        email: document.getElementById("email").value,
                        cpf: document.getElementById("cpf").value,
                        senha: document.getElementById("senha").value,
                        nivel_acesso: "cliente"
                    })
                });
                const data = await res.json();
                if (data.sucesso) {
                    mostrarNotificacao(
                        "🎉 Parabéns pelo cadastro!",
                        "Sua conta na Doce Celebração foi criada. Agora faça seu login!",
                        "sucesso"
                    );
                    setTimeout(() => {
                        window.location.href = "/login";
                    }, 2200);
                } else {
                    mostrarNotificacao("Atenção", data.mensagem, "erro");
                }
            } catch (erro) {
                console.error(erro);
                mostrarNotificacao("Erro de conexão", "Verifique se o servidor está rodando.", "erro");
            }
        });
    }
});