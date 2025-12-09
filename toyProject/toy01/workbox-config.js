module.exports = {
	globDirectory: 'app',
	globPatterns: [
		'**/*.js'
	],
	swDest: 'app/sw.js',
	ignoreURLParametersMatching: [
		/^utm_/,
		/^fbclid$/
	]
};