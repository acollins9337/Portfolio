const panels = document.querySelectorAll(".project-card");

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
    threshold: 0.8 // how much must be visible
  }
);

panels.forEach((panel) => observer.observe(panel));