// Login e cadastro. Depende de main.js.

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("aviso") === "carrinho") {
        mostrarToast("Quase lá! 🛒", "Faça login na sua conta para adicionar o item ao carrinho.", "sucesso");
    }

    // ----- Login -----
    const formLogin = document.getElementById("form-login");
    if (formLogin) {
        formLogin.addEventListener("submit", async (e) => {
            e.preventDefault();
            const botao = formLogin.querySelector('button[type="submit"]');
            if (botao) botao.disabled = true;

            const { data } = await apiJson("/api/auth/logar", "POST", {
                identificador: document.getElementById("identificador").value,
                senha: document.getElementById("senha").value
            });

            if (!data.sucesso) {
                if (botao) botao.disabled = false;
                mostrarToast("Ops! Algo deu errado", data.mensagem || "Não foi possível entrar.", "erro");
                return;
            }

            // Item que o visitante tentou adicionar antes de logar
            const pendenteRaw = sessionStorage.getItem("item_pendente_carrinho");
            if (pendenteRaw) {
                try {
                    const pendente = JSON.parse(pendenteRaw);
                    let carrinho = [];
                    try { carrinho = JSON.parse(localStorage.getItem("carrinho") || "[]"); } catch { carrinho = []; }

                    const existente = carrinho.find(i => i.id === pendente.id);
                    if (existente) existente.quantidade += 1;
                    else carrinho.push(pendente);

                    localStorage.setItem("carrinho", JSON.stringify(carrinho));
                    atualizarBadgeCarrinho();
                } catch (erro) {
                    console.warn("Item pendente inválido:", erro);
                }
                sessionStorage.removeItem("item_pendente_carrinho");
            }

            mostrarToast(
                `Bem-vindo(a), ${data.usuario.nome.split(" ")[0]}!`,
                pendenteRaw ? "Item adicionado! Abrindo seu carrinho..." : "Login realizado com sucesso. Redirecionando...",
                "sucesso"
            );

            setTimeout(() => {
                if (pendenteRaw) window.location.href = "/carrinho";
                else if (data.usuario.nivel_acesso === "administrador") window.location.href = "/admin";
                else if (data.usuario.nivel_acesso === "cozinheiro") window.location.href = "/cozinha";
                else window.location.href = "/cardapio";
            }, 1000);
        });
    }

    // ----- Cadastro -----
    const formCadastro = document.getElementById("form-cadastro");
    if (formCadastro) {
        formCadastro.addEventListener("submit", async (e) => {
            e.preventDefault();
            const botao = formCadastro.querySelector('button[type="submit"]');
            if (botao) botao.disabled = true;

            const { data } = await apiJson("/api/auth/cadastrar", "POST", {
                nome: document.getElementById("nome").value,
                usuario: document.getElementById("usuario").value,
                email: document.getElementById("email").value,
                cpf: document.getElementById("cpf").value,
                senha: document.getElementById("senha").value,
                nivel_acesso: "cliente"
            });

            if (data.sucesso) {
                mostrarToast("🎉 Parabéns pelo cadastro!", "Sua conta na Doce Celebração foi criada. Agora faça seu login!", "sucesso");
                setTimeout(() => { window.location.href = "/login"; }, 2200);
            } else {
                if (botao) botao.disabled = false;
                mostrarToast("Atenção", data.mensagem || "Não foi possível cadastrar.", "erro");
            }
        });
    }
});