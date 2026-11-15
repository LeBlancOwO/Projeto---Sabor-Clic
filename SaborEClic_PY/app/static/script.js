document.addEventListener('DOMContentLoaded', () => {
    const $ = s => document.querySelector(s);

    
    // Menu hambúrguer
    const toggle = $('.menu-toggle'), menu = $('#menu');
    toggle.addEventListener('click', () => {
        toggle.setAttribute('aria-expanded', menu.classList.toggle('open'));
    });


    // Pesquisa (filtra as linhas da tabela do cardápio, se existir)
    const bar = $('#search-bar'), campo = bar.querySelector('input');
    $('#search-toggle').addEventListener('click', () => {
        bar.hidden = !bar.hidden;
        if (!bar.hidden) campo.focus();
    });
    bar.addEventListener('submit', e => e.preventDefault());
    campo.addEventListener('input', () => {
        const t = campo.value.toLowerCase();
        document.querySelectorAll('tbody tr').forEach(tr => {
            tr.hidden = !tr.textContent.toLowerCase().includes(t);
        });
    });


    // Contador do carrinho (demonstrativo): qualquer botão com data-add soma 1
    const badge = $('#cart-count');
    let n = Number(sessionStorage.getItem('cart') || 0);
    badge.textContent = n;
    document.querySelectorAll('[data-add]').
    forEach(b => b.addEventListener('click', () => {
        sessionStorage.setItem('cart', ++n);
        badge.textContent = n;
    }));


    // Carrossel (no celular; no computador os 3 banners aparecem lado a lado)
    const track = $('.hero-track');
    if (track) {
        const dots = [...document.querySelectorAll('.dots button')];
        const atual = () => Math.round(track.scrollLeft / track.clientWidth);
        const ir = i => track.scrollTo({ left: ((i + 3) % 3) * track.clientWidth, behavior: 'smooth' });
        $('.next').addEventListener('click', () => ir(atual() + 1));
        $('.prev').addEventListener('click', () => ir(atual() - 1));
        dots.forEach((d, i) => d.addEventListener('click', () => ir(i)));
        track.addEventListener('scroll', () => dots.forEach((d, i) => d.classList.toggle('on', i === atual())));
        dots[0].classList.add('on');
    }
});