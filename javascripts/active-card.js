const panels = document.querySelectorAll(".project-card");

// disable on mobile / small screens
const isMobile = window.matchMedia("(max-width: 1085px)").matches;

if (!isMobile) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("up");
        } else {
          entry.target.classList.remove("up");
        }
      });
    },
    {
      root: null,
      threshold: 0.8
    }
  );

  panels.forEach((panel) => observer.observe(panel));
}