// Sticky scroll spy: tracks the section in view, hides itself over the hero.
(function () {
    const spy = document.getElementById("spy");
    if (!spy) return;

    const items = Array.from(spy.querySelectorAll(".spy-item"));
    const sections = items
        .map((item) => {
            const id = item.dataset.target;
            const section = document.getElementById(id);
            return section ? { item, section } : null;
        })
        .filter(Boolean);

    if (!sections.length) return;

    /* ---- active dot tracking ---- */
    let queued = false;

    function setActive(active) {
        sections.forEach(({ item }) => {
            const on = item === active;
            item.classList.toggle("active", on);
            item.firstElementChild.setAttribute("aria-current", on ? "true" : "false");
        });
    }

    function updateActive() {
        queued = false;

        // The section whose top sits highest above the viewport anchor line wins.
        const anchor = window.scrollY + window.innerHeight * 0.35;
        let current = sections[0];

        sections.forEach((entry) => {
            if (entry.section.offsetTop <= anchor) current = entry;
        });

        // Bottom of the page always highlights the last section.
        if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 4) {
            current = sections[sections.length - 1];
        }

        setActive(current.item);
    }

    function onScroll() {
        if (queued) return;
        queued = true;
        requestAnimationFrame(updateActive);
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    updateActive();

    /* ---- click to jump ---- */
    items.forEach((item) => {
        item.firstElementChild.addEventListener("click", (e) => {
            const section = document.getElementById(item.dataset.target);
            if (!section) return;
            e.preventDefault();
            section.scrollIntoView({ behavior: "smooth", block: "start" });
            history.replaceState(null, "", "#" + item.dataset.target);
        });
    });

    const toTop = spy.querySelector(".spy-top");
    if (toTop) {
        toTop.addEventListener("click", (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: "smooth" });
            history.replaceState(null, "", location.pathname);
        });
    }

    /* ---- hide while the hero is on screen ---- */
    const hero = document.getElementById("hero");
    if (hero) {
        spy.classList.add("hidden");
        new IntersectionObserver(
            ([entry]) => spy.classList.toggle("hidden", entry.isIntersecting),
            { threshold: 0.35 }
        ).observe(hero);
    }
})();
