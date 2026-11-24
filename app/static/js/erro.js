// Páginas de erro. Depende de main.js (carregado antes no base.html).

document.addEventListener("DOMContentLoaded", () => {
    const btnVoltar = document.getElementById("btn-voltar");
    if (!btnVoltar) return;

    btnVoltar.addEventListener("click", () => {
        let veioDoSite = false;
        try {
            veioDoSite = !!document.referrer &&
                new URL(document.referrer).origin === window.location.origin;
        } catch {
            veioDoSite = false;
        }

        if (veioDoSite) window.history.back();
        else window.location.href = "/";
    });
});