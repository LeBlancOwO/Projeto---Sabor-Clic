fetch("/api/cadastro/cadastrar", {

    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify({

        nome: nome,
        email: email,
        cpf: cpf,
        senha: senha,
        nivel_acesso: "Cliente"

    })
})