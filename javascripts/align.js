function adjustSplitAlignment() {
    document.querySelectorAll('.split').forEach(split => {
        const img = split.querySelector('.img-container img');
        const text = split.querySelector('.split-text');

        if (!img || !text) return;

        if (img.offsetHeight > text.offsetHeight) {
            split.classList.add('text-top');
        } else {
            split.classList.remove('text-top');
        }
    });
}

window.addEventListener('load', adjustSplitAlignment);
window.addEventListener('resize', adjustSplitAlignment);