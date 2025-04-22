/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["./templates/**/*.html", "./static/**/*.js"],
	theme: {
		extend: {},
	},
	plugins: [require("@tailwindcss/typography"), require("@tailwindcss/forms")],
};
