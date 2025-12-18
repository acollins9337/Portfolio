document.querySelectorAll('.project-card').forEach(card => {
    const images = card.querySelectorAll('.project-image');
    let index = 0;

    images.forEach((img, i) => {
        if (img.classList.contains('active')) index = i;
    });

    card.addEventListener('click', () => {
        if (images.length <= 1) return;

        images[index].classList.remove('active');
        index = (index + 1) % images.length;
        images[index].classList.add('active');
    });
});