class Navigation {
  constructor() {
    this.navIcon = document.querySelector(".menu-switch");
    this.nav = document.querySelector("nav");
    this.state = {
      open: false,
    };
  }
  toggleNav() {
    if (this.state.open) {
      this.nav.dataset.state = "";
      this.state.open = false;
    } else {
      this.nav.dataset.state = "mobile-active";
      this.state.open = true;
    }
  }
  init() {
    this.navIcon.addEventListener("click", () => {
      this.toggleNav();
    });
  }
}

module.exports = Navigation;
