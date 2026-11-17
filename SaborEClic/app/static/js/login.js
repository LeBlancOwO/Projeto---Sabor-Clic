fetch("/api/login/logar", {

    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify({

        email: email,
        cpf: cpf,
        senha: senha

    })
})
.then(res => res.json())
.then(dados => {

    if(dados.sucesso){

        console.log(dados.usuario)

    }else{

        alert(dados.mensagem)

    }

})