export default class Navigation {
	constructor(element) {
		this.element = element;
		this.menu = element.querySelector("[data-menu]");
		this.menuButton = element.querySelector("[data-menu-button]");
		this.menuOpenClasses = ["transform-none"];
		this.menuClosedClasses = ["-translate-x-full"];
		this.state = "closed";

		this.init();
	}

	init() {
		this.setupAriaAttributes();
		this.setupEventListeners();
	}

	setupAriaAttributes() {
		this.menuButton.setAttribute("aria-expanded", "false");
		this.menuButton.setAttribute("aria-controls", this.menu.id);
		this.menu.setAttribute("aria-hidden", "true");
	}

	setupEventListeners() {
		this.menuButton.addEventListener("click", this.handleMenuButtonClick.bind(this));
		document.addEventListener("keydown", this.handleDocumentKeydown.bind(this));
		this.menu.addEventListener("keydown", this.handleMenuKeydown.bind(this));
	}

	handleMenuButtonClick() {
		this.setState(this.state === "closed" ? "opened" : "closed");
	}

	handleDocumentKeydown(event) {
		if (event.key === "Escape" && this.state === "opened") {
			this.setState("closed");
		}
	}

	handleMenuKeydown(event) {
		if (event.key !== "Tab") return;

		const focusableElements = this.getFocusableElements();
		const firstElement = focusableElements[0];
		const lastElement = focusableElements[focusableElements.length - 1];

		if (event.shiftKey && document.activeElement === firstElement) {
			lastElement.focus();
			event.preventDefault();
		} else if (!event.shiftKey && document.activeElement === lastElement) {
			firstElement.focus();
			event.preventDefault();
		}
	}

	getFocusableElements() {
		return this.menu.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
	}

	setState(newState) {
		this.state = newState;
		this.updateMenuClasses();
		this.updateAriaAttributes();
		this.handleFocus();
	}

	updateMenuClasses() {
		if (this.state === "opened") {
			this.menuClosedClasses.forEach((className) => this.menu.classList.remove(className));
			this.menuOpenClasses.forEach((className) => this.menu.classList.add(className));
			document.body.classList.add("overflow-hidden");
		} else {
			this.menuOpenClasses.forEach((className) => this.menu.classList.remove(className));
			this.menuClosedClasses.forEach((className) => this.menu.classList.add(className));
			document.body.classList.remove("overflow-hidden");
		}
	}

	updateAriaAttributes() {
		const isOpen = this.state === "opened";
		this.menuButton.setAttribute("aria-expanded", isOpen.toString());
		this.menu.setAttribute("aria-hidden", (!isOpen).toString());
		this.menuButton.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
	}

	handleFocus() {
		if (this.state === "opened") {
			setTimeout(() => {
				const firstFocusable = this.getFocusableElements()[0];
				if (firstFocusable) firstFocusable.focus();
			}, 100);
		} else {
			this.menuButton.focus();
		}
	}
}
