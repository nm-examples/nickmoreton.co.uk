const menu = document.querySelector("[data-menu]");
const nav = document.querySelector(".site-nav");
if (menu && nav) {
  menu.hidden = false;
  menu.closest(".site-header").classList.add("is-enhanced");
  const close = (restoreFocus = false) => {
    const wasOpen = menu.getAttribute("aria-expanded") === "true";
    nav.classList.remove("open");
    menu.setAttribute("aria-expanded", "false");
    if (wasOpen && restoreFocus) menu.focus();
  };
  menu.addEventListener("click", () => {
    const open = menu.getAttribute("aria-expanded") !== "true";
    menu.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("open", open);
  });
  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => close());
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close(true);
  });
  window
    .matchMedia("(min-width: 761px)")
    .addEventListener("change", () => close());
}
