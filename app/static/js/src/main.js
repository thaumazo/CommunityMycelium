// 3rd party modules
// ...

// Our modules / classes
import Navigation from "./modules/Navigation";
import UserMenu from "./modules/UserMenu";

const manifest = {
	Navigation,
	UserMenu,
};

const app = {
	registerModules() {
		document.querySelectorAll("[data-module]").forEach((element) => {
			const moduleName = element.getAttribute("data-module");

			if (!manifest[moduleName]) {
				console.error(`Module "${moduleName}" does not exist in the manifest.`);
				return;
			}

			new manifest[moduleName](element);
		});
	},
};

app.registerModules();
