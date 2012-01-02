from setuptools import setup, find_packages


setup(
	name = "Enkel",
	version = "1.0_rc7",
	author = "Espen Angell Kristiansen",
	author_email = "post@espenak.net",
	url = "http://code.google.com/p/enkel/",
	zip_safe=False,

	package_data = {
		"enkel.rngdata": ["*.rng", "markup/*.rng", "staticcms/*.rng"],
		"enkel": [
			"translations/en/LC_MESSAGES/default.mo",
			"translations/nb/LC_MESSAGES/default.mo"
		],
	},

	packages = find_packages(exclude=["testsuite*"]),

	entry_points = {
		"console_scripts": [
			"enkel-benchmark-server = enkel.scripts.benchmark_server:cli",
			"enkel-cgi-server = enkel.scripts.cgi_server:cli",
			"enkel-server-response-tester = "\
				"enkel.scripts.server_response_tester:cli",
			"enkel-staticcms = enkel.batteri.staticcms.cli:cli",
		]
	},

	test_suite = "testsuite.suite",
)
