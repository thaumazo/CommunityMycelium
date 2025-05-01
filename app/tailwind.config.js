/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["./templates/**/*.html", "./static/**/*.js"],
	theme: {
		extend: {
			fontFamily: {
				heading: ["Inter", "sans-serif"],
				body: ["Inter", "sans-serif"],
			},
		},
	},
	plugins: [require("@tailwindcss/typography"), require("@tailwindcss/forms")],
};
