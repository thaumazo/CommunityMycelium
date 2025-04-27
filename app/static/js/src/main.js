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

// Sample code to test the bundler
console.log("Hello from Mycelium!");

// Example of a simple function
function initApp() {
	console.log("App initialized");
}

// Initialize the app when the DOM is loaded
document.addEventListener("DOMContentLoaded", initApp);
