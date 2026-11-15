
document.addEventListener('DOMContentLoaded', () => {

    // Menu hambúrguer
    const toggle = document.querySelector('.menu-toggle');
    const menu = document.querySelector('#menu');

    if (toggle && menu) {
        toggle.addEventListener('click', () => {
            toggle.setAttribute(
                'aria-expanded',
                menu.classList.toggle('open')
            );
        });
    }

    // Pesquisa
    const bar = document.querySelector('#search-bar');
    const campo = bar?.querySelector('input');
    const botaoPesquisa = document.querySelector('#search-toggle');

    if (bar && campo && botaoPesquisa) {
        botaoPesquisa.addEventListener('click', () => {
            bar.hidden = !bar.hidden;

            if (!bar.hidden) {
                campo.focus();
            }
        });

        bar.addEventListener('submit', (e) => {
            e.preventDefault();
        });

        campo.addEventListener('input', () => {
            const pesquisa = campo.value.toLowerCase().trim();

            document.querySelectorAll('.table-wrap tbody tr').forEach(tr => {
                const texto = tr.textContent.toLowerCase();
                tr.hidden = !texto.includes(pesquisa);
            });
        });
    }

    // Contador do carrinho
    const badge = document.querySelector('#cart-count');

    if (badge) {
        let n = Number(sessionStorage.getItem('cart') || 0);
        badge.textContent = n;

        document.querySelectorAll('[data-add]').forEach(botao => {
            botao.addEventListener('click', () => {
                sessionStorage.setItem('cart', ++n);
                badge.textContent = n;
            });
        });
    }

    // Carrossel
    const track = document.querySelector('.hero-track');

    if (track) {
        const dots = [...document.querySelectorAll('.dots button')];
        const next = document.querySelector('.next');
        const prev = document.querySelector('.prev');

        const atual = () =>
            Math.round(track.scrollLeft / track.clientWidth);

        const ir = i => {
            track.scrollTo({
                left: ((i + 3) % 3) * track.clientWidth,
                behavior: 'smooth'
            });
        };

        if (next) next.addEventListener('click', () => ir(atual() + 1));
        if (prev) prev.addEventListener('click', () => ir(atual() - 1));

        dots.forEach((d, i) => {
            d.addEventListener('click', () => ir(i));
        });

        if (dots.length > 0) {
            dots[0].classList.add('on');

            track.addEventListener('scroll', () => {
                dots.forEach((d, i) => {
                    d.classList.toggle('on', i === atual());
                });
            });
        }
    }

});
