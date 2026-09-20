export default class ParentPicker {
	constructor(element) {
		this.element = element;
		this.search = element.querySelector("[data-parent-search]");
		this.results = element.querySelector("[data-parent-results]");
		this.chips = element.querySelector("[data-parent-chips]");
		this.hiddenInputs = element.querySelector("[data-parent-hidden-inputs]");
		this.searchUrl = element.dataset.searchUrl;
		this.selected = new Set(
			Array.from(this.hiddenInputs.querySelectorAll('input[name="parent"]')).map((input) => input.value),
		);
		this.searchTimer = null;

		this.init();
	}

	init() {
		this.search.addEventListener("input", () => {
			clearTimeout(this.searchTimer);
			this.searchTimer = setTimeout(() => this.find(), 250);
		});
		this.search.addEventListener("keydown", (event) => {
			if (event.key === "Escape") this.closeResults();
		});
		this.element.addEventListener("click", (event) => {
			const removeButton = event.target.closest("[data-remove-parent]");
			if (removeButton) this.remove(removeButton.dataset.removeParent);
		});
		document.addEventListener("click", (event) => {
			if (!this.element.contains(event.target)) this.closeResults();
		});
	}

	async find() {
		const query = this.search.value.trim();
		if (query.length < 2) {
			this.closeResults();
			return;
		}

		const response = await fetch(`${this.searchUrl}?q=${encodeURIComponent(query)}`, {
			headers: { Accept: "application/json" },
		});
		if (!response.ok) return;

		const payload = await response.json();
		this.results.innerHTML = "";
		payload.results
			.filter((result) => !this.selected.has(String(result.id)))
			.forEach((result) => {
				const button = document.createElement("button");
				button.type = "button";
				button.className = "block w-full border-b border-gray-100 px-3 py-2 text-left hover:bg-gray-50";
				button.innerHTML = `<span class="block text-sm font-medium text-gray-900"></span><span class="block text-xs text-gray-500"></span>`;
				button.firstElementChild.textContent = result.title;
				button.lastElementChild.textContent = `${result.phase} · ${result.state}`;
				button.addEventListener("click", () => this.add(result));
				this.results.appendChild(button);
			});

		this.results.classList.toggle("hidden", !this.results.children.length);
	}

	add(result) {
		const id = String(result.id);
		if (this.selected.has(id)) return;
		this.selected.add(id);

		const input = document.createElement("input");
		input.type = "hidden";
		input.name = "parent";
		input.value = id;
		this.hiddenInputs.appendChild(input);

		const chip = document.createElement("span");
		chip.className = "inline-flex items-center gap-1 rounded-full bg-indigo-100 px-3 py-1 text-sm text-indigo-900";
		chip.dataset.parentChip = "";
		chip.dataset.parentId = id;
		chip.innerHTML = `<span></span><button type="button" class="text-indigo-700 hover:text-indigo-950" data-remove-parent="${id}" aria-label="Remove parent">&times;</button>`;
		chip.firstElementChild.textContent = result.title;
		this.chips.appendChild(chip);
		this.search.value = "";
		this.closeResults();
	}

	remove(id) {
		id = String(id);
		this.selected.delete(id);
		Array.from(this.hiddenInputs.querySelectorAll('input[name="parent"]'))
			.find((input) => input.value === id)?.remove();
		Array.from(this.chips.querySelectorAll("[data-parent-id]"))
			.find((chip) => chip.dataset.parentId === id)?.remove();
	}

	closeResults() {
		this.results.classList.add("hidden");
	}
}
