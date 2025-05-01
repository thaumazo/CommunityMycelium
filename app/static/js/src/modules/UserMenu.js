export default class UserMenu {
	constructor(element) {
		this.element = element;
		this.menuButton = element.querySelector('[data-dropdown-toggle="dropdown-user"]');
		this.menu = element.querySelector("#dropdown-user");
		this.isOpen = false;

		if (this.menuButton && this.menu) {
			this.init();
		}
	}

	init() {
		// Add click event to toggle menu
		this.menuButton.addEventListener("click", (e) => {
			e.stopPropagation();
			this.toggleMenu();
		});

		// Close menu when clicking outside
		document.addEventListener("click", (e) => {
			if (this.isOpen && !this.menu.contains(e.target) && !this.menuButton.contains(e.target)) {
				this.closeMenu();
			}
		});

		// Close menu when pressing Escape key
		document.addEventListener("keydown", (e) => {
			if (e.key === "Escape" && this.isOpen) {
				this.closeMenu();
			}
		});
	}

	toggleMenu() {
		if (this.isOpen) {
			this.closeMenu();
		} else {
			this.openMenu();
		}
	}

	openMenu() {
		this.menu.classList.remove("hidden");
		this.menuButton.setAttribute("aria-expanded", "true");
		this.isOpen = true;
	}

	closeMenu() {
		this.menu.classList.add("hidden");
		this.menuButton.setAttribute("aria-expanded", "false");
		this.isOpen = false;
	}
}
