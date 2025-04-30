js = r"""function gradioCustomJS() {
	console.log("gradioCustomJS Started")

	// MARK: berechne Helligkeit der Akzentfarbe
	function berechneHelligkeit(rgb) {
		const match = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/)
		if (!match) {
			throw new Error("Ungültiges Farbformat")
		}

		const r = parseInt(match[1]) / 255
		const g = parseInt(match[2]) / 255
		const b = parseInt(match[3]) / 255

		const rLin = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4)
		const gLin = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4)
		const bLin = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4)

		const luminanz = 0.2126 * rLin + 0.7152 * gLin + 0.0722 * bLin

		return luminanz
	}

	// MARK: Textfarbe bestimmen
	function anpasseTextfarbe(farbe) {
		const luminanz = berechneHelligkeit(farbe)
		const textFarbe = luminanz > 0.4 ? "var(--neutral-950)" : "var(--neutral-50)"
		console.log("Luminanz: " + luminanz + " Text-Farbe: " + textFarbe)

		return textFarbe
	}

	// MARK: Body Styles
	const body = document.querySelector("body")
	body.className = "dark"

	// Catppuccin colors
	// const rosewater = "245, 224, 220"
	// const flamingo = "242, 205, 205"
	// const pink = "245, 194, 231"
	// const maroon = "235, 160, 172"
	const mauve = "203, 166, 247"
	const red = "243, 139, 168"
	const peach = "250, 179, 135"
	const yellow = "249, 226, 175"
	const green = "166, 227, 161"
	const teal = "148, 226, 213"
	const sky = "137, 220, 235"
	const sapphire = "116, 199, 236"
	const blue = "137, 180, 250"

	let colors = [mauve, red, peach, yellow, green, teal, sky, sapphire, blue] // rosewater, flamingo, pink, maroon, 
	let usedColor = `rgb(${colors[Math.floor(Math.random() * colors.length)]})`

	// body.style.setProperty("--cat-rosewater", "rgb(" + rosewater + ")")
	// body.style.setProperty("--cat-flamingo", "rgb(" + flamingo + ")")
	// body.style.setProperty("--cat-pink", "rgb(" + pink + ")")
	// body.style.setProperty("--cat-maroon", "rgb(" + maroon + ")")
	body.style.setProperty("--cat-mauve", "rgb(" + mauve + ")")
	body.style.setProperty("--cat-red", "rgb(" + red + ")")
	body.style.setProperty("--cat-peach", "rgb(" + peach + ")")
	body.style.setProperty("--cat-yellow", "rgb(" + yellow + ")")
	body.style.setProperty("--cat-green", "rgb(" + green + ")")
	body.style.setProperty("--cat-teal", "rgb(" + teal + ")")
	body.style.setProperty("--cat-sky", "rgb(" + sky + ")")
	body.style.setProperty("--cat-sapphire", "rgb(" + sapphire + ")")
	body.style.setProperty("--cat-blue", "rgb(" + blue + ")")

	body.style.setProperty("--primary-600", usedColor)
	body.style.setProperty("--primary-50", "color-mix(in srgb, var(--primary-600) 5%, white)")
	body.style.setProperty("--primary-100", "color-mix(in srgb, var(--primary-600) 10%, white)")
	body.style.setProperty("--primary-200", "color-mix(in srgb, var(--primary-600) 20%, white)")
	body.style.setProperty("--primary-300", "color-mix(in srgb, var(--primary-600) 60%, white)")
	body.style.setProperty("--primary-400", "color-mix(in srgb, var(--primary-600) 70%, white)")
	body.style.setProperty("--primary-500", "color-mix(in srgb, var(--primary-600) 80%, white)")
	body.style.setProperty("--primary-700", "color-mix(in srgb, var(--primary-600) 80%, black)")
	body.style.setProperty("--primary-800", "color-mix(in srgb, var(--primary-600) 65%, black)")
	body.style.setProperty("--primary-900", "color-mix(in srgb, var(--primary-600) 40%, black)")
	body.style.setProperty("--primary-950", "color-mix(in srgb, var(--primary-600) 30%, black)")

	body.style.setProperty("--button-primary-background-fill", "var(--primary-600)")
	body.style.setProperty("--button-primary-background-fill-hover", "var(--primary-500)")
	body.style.setProperty("--blur-value", "0px")
	body.style.setProperty("--text-color-by-luminance", anpasseTextfarbe(usedColor))

    
	// // MARK: SVG Animationen & Emojis
	// document.querySelector(".row-header i.winking-hand-emoji").innerHTML =
	// 	'<svg aria-hidden="true" style="height: 16px;" preserveAspectRatio="xMidYMid meet" role="img" viewBox="0 0 128 128"><style> @keyframes wink{0%, 60%, 100%{transform: rotate(0deg);}10%, 30%, 70%, 90%{transform: rotate(14deg);}20%, 80%{transform: rotate(-8deg);}40%{transform: rotate(-4deg);}50%{transform: rotate(10deg);}}</style><g style="animation: wink 3s ease-in-out infinite; transform-origin: 50% 50%;"><radialGradient id="a" cx="-779.868" cy="686.689" r="91.008" gradientTransform="scale(1 -1) rotate(45 506.867 1318.897)" gradientUnits="userSpaceOnUse"><stop offset=".353" stop-color="#ffca28"/><stop offset=".872" stop-color="#ffb300"/></radialGradient><path fill="url(#a)" d="M59.53 107.44c-3.95-3.17-40.63-38.84-41.04-39.23-1.62-1.62-2.64-3.3-2.92-4.84-.29-1.6.2-3 1.5-4.3 1.21-1.21 2.69-1.85 4.28-1.85 1.94 0 3.93.92 5.59 2.59l16.63 15.98c.29.28.67.42 1.04.42a1.494 1.494 0 0 0 1.07-2.54L19.13 46.25c-2.66-2.66-3.91-6.73-.75-9.89 1.21-1.21 2.69-1.85 4.28-1.85 1.94 0 3.93.92 5.59 2.59l27.16 26.48c.29.28.67.43 1.05.43s.77-.15 1.06-.44c.58-.58.59-1.52.01-2.11L24.91 28.02c-1.51-1.51-2.42-3.32-2.58-5.08-.15-1.79.48-3.45 1.83-4.8 1.21-1.21 2.69-1.85 4.28-1.85 1.94 0 3.93.92 5.59 2.58L67.3 51.31c.29.28.67.43 1.05.43s.77-.15 1.06-.44c.58-.58.59-1.52.01-2.11L45.26 24.36c-1.52-1.52-2.43-3.32-2.58-5.08-.15-1.79.48-3.45 1.83-4.8 1.21-1.21 2.69-1.85 4.28-1.85 1.94 0 3.93.92 5.59 2.59 8.86 8.7 31.99 31.45 32.77 32.29 2.97 2.05 3.57-1.05 3.72-3.06.17-2.34-2.51-10.51-.95-17.86 2.62-9.77 10.17-8.17 10.34-8.09 4.14 1.94 3.35 4.84 1.88 10.67l-.15 1.15c-1.54 7.62 9.04 30.2 9.82 31.89 4.15 9.08 8.93 27.49-6.9 43.32-17.35 17.35-38.83 8.46-45.38 1.91z"/><path fill="#eda600" d="M81.79 117.18c-10.64 0-19.69-5.09-23.26-8.62-3.21-2.62-23.47-22.18-39.97-38.19-.67-.65-1.06-1.02-1.1-1.07-1.87-1.87-3.03-3.82-3.36-5.66-.38-2.09.27-3.98 1.91-5.63 1.5-1.5 3.34-2.29 5.34-2.29 2.35 0 4.71 1.08 6.65 3.03l16.61 15.96-26.56-27.42c-3.06-3.06-4.6-8.13-.73-11.99 1.5-1.5 3.34-2.29 5.34-2.29 2.35 0 4.71 1.08 6.65 3.03L56.45 62.5 23.84 29.07c-1.74-1.74-2.81-3.87-3-5.99-.19-2.26.59-4.33 2.26-6 1.5-1.5 3.34-2.29 5.34-2.29 2.34 0 4.7 1.07 6.65 3.02l33.26 32.43-24.16-24.83c-1.75-1.75-2.82-3.88-3-6-.19-2.25.59-4.32 2.26-5.99 1.5-1.5 3.34-2.29 5.34-2.29 2.35 0 4.71 1.08 6.65 3.03l7.21 7.07c12.85 12.6 23.59 23.15 24.74 24.33.56.45 1.29.62 1.6.47.2-.1.42-.56.38-1.53-.06-1.7-.3-3.81-.55-6.04-.5-4.48-1.02-9.12-.37-12.18 1.42-5.31 4.21-7.56 6.29-8.53 2.86-1.32 5.63-.86 6.16-.61 5.2 2.44 4.17 6.52 2.75 12.18l-.03.14-.16 1.17c-1.04 5.12 4.3 19.27 9.64 30.8l.08.16c3.57 7.8 10 27.81-7.2 45.01-7.91 7.89-16.47 10.58-24.19 10.58zM21.35 58.72c-1.18 0-2.3.49-3.22 1.41-.95.95-1.28 1.87-1.08 2.97.22 1.21 1.11 2.65 2.5 4.05.01.01.41.4 1.1 1.06 23.42 22.73 37.56 36.24 39.82 38.06l.12.11c5.52 5.52 26.03 15.32 43.26-1.91 15.87-15.87 9.9-34.4 6.59-41.64l-.07-.15c-3.44-7.42-11.26-25.42-9.87-32.6l.23-1.5c1.54-6.12 1.63-7.4-.98-8.66-.77-.14-6.29-.81-8.4 7.06-.53 2.51-.02 7.1.43 11.15.26 2.29.5 4.46.56 6.27.1 2.85-1.25 3.94-2.07 4.34-1.67.81-3.66.12-4.9-.92l-.13-.12c-.61-.66-15.12-14.89-24.72-24.31L53.3 16.3c-2.46-2.47-5.63-2.88-7.76-.75-1.04 1.04-1.51 2.26-1.4 3.61.12 1.41.88 2.88 2.15 4.15L70.5 48.14a3.012 3.012 0 0 1-.02 4.22c-1.11 1.11-3.07 1.13-4.21.03L32.98 19.94c-2.46-2.46-5.64-2.87-7.76-.74-1.04 1.04-1.51 2.26-1.4 3.61.13 1.41.89 2.89 2.15 4.14L58.6 60.41c1.15 1.16 1.14 3.06-.02 4.22-1.11 1.11-3.07 1.13-4.21.03L27.2 38.17c-2.46-2.48-5.64-2.88-7.76-.75-2.59 2.59-1.21 5.8.75 7.77l26.57 27.44a2.988 2.988 0 0 1-.03 4.2c-1.12 1.12-3.06 1.13-4.2.04L25.9 60.89c-1.4-1.41-3.01-2.17-4.55-2.17z"/><path fill="#eda600" d="M84.76 46.54c-5.49 11.21-4.78 26.9 3.46 39.49.93 1.7 2.52.87 1.71-.88-9.95-21.29.48-36.63.48-36.63l-5.65-1.98z"/><path fill="#b0bec5" d="M63.17 4.5c3.02-.79 6.24-.72 9.37.01 3.11.75 6.22 2.33 8.53 4.91 2.26 2.56 3.65 5.67 4.12 8.93.44 3.23.03 6.56-1.5 9.32-.18-3.1-.72-5.95-1.63-8.58-.47-1.31-1.02-2.56-1.69-3.74-.66-1.17-1.44-2.33-2.27-3.28-1.69-1.95-3.98-3.47-6.55-4.65-2.58-1.22-5.39-2.12-8.38-2.92z"/><path fill="#90a4ae" d="M64 13.98c1.67-1.06 3.76-1.28 5.73-.93 1.99.35 3.89 1.34 5.39 2.71 1.49 1.39 2.55 3.14 3.21 4.96.32.91.48 1.87.63 2.8.05.96.05 1.92-.1 2.88-.69-.73-1.23-1.46-1.74-2.17-.59-.67-1.05-1.38-1.58-2.03-1.04-1.29-2.05-2.46-3.14-3.5-1.12-1.01-2.3-1.9-3.67-2.67-1.36-.79-2.89-1.45-4.73-2.05z"/><path fill="#b0bec5" d="M6.83 77.34c1.41 2.76 2.88 5.32 4.59 7.58 1.7 2.26 3.65 4.18 5.92 5.43 1.1.61 2.41 1.14 3.69 1.54 1.29.41 2.63.69 4.01.88 2.76.34 5.66.28 8.73-.19-2.38 2.07-5.56 3.17-8.8 3.41-3.28.22-6.61-.49-9.59-2.17-3-1.71-5.2-4.43-6.58-7.32-1.38-2.91-2.12-6.04-1.97-9.16z"/><path fill="#90a4ae" d="M16.28 76.17c.97 1.68 1.93 3.03 2.98 4.21 1.04 1.18 2.16 2.15 3.38 3.03 1.24.85 2.6 1.6 4.08 2.35.74.38 1.53.68 2.31 1.12.81.35 1.63.72 2.49 1.25-.91.34-1.84.54-2.79.69-.94.04-1.91.09-2.87-.04-1.92-.26-3.84-.93-5.52-2.1-1.65-1.19-3.02-2.84-3.77-4.71-.76-1.86-.98-3.94-.29-5.8z"/></g></svg>'

	// document.querySelector(".row-header i.heart-beat-emoji").innerHTML =
	// 	'<svg xmlns="http://www.w3.org/2000/svg" style="height: 16px;" viewBox="0 0 512 512"><defs><style> @keyframes beat{0%{transform: scale(1);}5%{transform: scale(0.75);}20%{transform: scale(1);}30%{transform: scale(1);}35%{transform: scale(0.75);}50%{transform: scale(1);}55%{transform: scale(0.75);}70%{transform: scale(1);}}</style></defs><g style="animation: beat 2s ease-in-out infinite; transform-origin: 50% 50%;"><path fill="#bd0a0a" d="M47.6 300.4L228.3 469.1c7.5 7 17.4 10.9 27.7 10.9s20.2-3.9 27.7-10.9L464.4 300.4c30.4-28.3 47.6-68 47.6-109.5v-5.8c0-69.9-50.5-129.5-119.4-141C347 36.5 300.6 51.4 268 84L256 96 244 84c-32.6-32.6-79-47.5-124.6-39.9C50.5 55.6 0 115.2 0 185.1v5.8c0 41.5 17.2 81.2 47.6 109.5z"/></g></svg>'


	return "Animation created"
}
"""

js_zoom_in = """
function toggleZoomScreen() {
	// document.body.style.zoom = "150%";
	window.parent.document.body.style.zoom = 1.4;
} 
"""


metadata_js = """   () => {
    if (document.activeElement.getAttribute('aria-label') === 'clicked like') {
        console.log('User liked the result');
        document.getElementById('hidden_other_results').click();
    } else {
        // Do nothing
        console.log('User did not like the result');
    }
}"""
