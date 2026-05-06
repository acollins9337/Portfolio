document.querySelectorAll('.project-card').forEach(card => {
    const images = card.querySelectorAll('.project-image');
    let index = 0;

    const showImage = i => {
        images.forEach(img => img.classList.remove('active'));
        images[i].classList.add('active');
    };

    card.querySelector('.next').addEventListener('click', e => {
        e.stopPropagation();
        index = (index + 1) % images.length;
        showImage(index);
    });

    card.querySelector('.prev').addEventListener('click', e => {
        e.stopPropagation();
        index = (index - 1 + images.length) % images.length;
        showImage(index);
    });
});
