<?xml version="1.0" encoding="utf-8"?>


<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:m="http://enkel.wsgi.net/xml/markup"
		exclude-result-prefixes="m">

	<xsl:import href="markup.xsl"/>

	<xsl:template match="/">
		<html>
			<head>
				<meta http-equiv="Content-Type"
						content="text/html; charset=utf-8"/> 
				<title>
					<xsl:value-of select="$title"/>
				</title>

				<style type="text/css">
					body{
						font-family: sans-serif;
						color: #222;
						margin: 30px 30px 30px 0;
					}

					code{
						color: #a72c2c;
					}

					div .markup_p{margin: 10px 0 10px 0;}
					div .markup_prog, div .markup_pre{
						border: 1px solid #000;
						background-color: #eee;
						padding: 10px;
					}


					.markup_section{
						margin-left: 30px;
					}

					h1{
						font-family: "Georgia", serif;
						color: #a72c2c;
						font-weight: normal;
						font-size: 3.0em;
						margin: 0 0 30px 0;
						padding: 0;
					}
					h2, h3, h4, h5, h6{
						font-family: "Georgia", serif;
						font-weight: normal;
						color: #000;
						padding: 0;
						margin: 35px 0 25px -30px;
					}
					h2{font-size: 2.2em}
					h3{font-size: 1.8em}
					h3{font-size: 1.6em}
					h4{font-size: 1.4em}
					h5{font-size: 1.2em}
					h5{font-size: 1.0em}


					table{
						border: 1px solid #000;
						border-spacing: 0;
						border-collapse: collapse;
						margin: 10px 0 10px 0;
					}
					th, td{
						padding: 5px 10px 5px 10px;
						border-left: 1px solid #000;
						font-size: 1.0em;
					}
					th{
						border-bottom: 3px solid #000;
						border-left: 1px solid #000;
					}
					td{
						border-bottom: 1px solid #000;
					}

				</style>
			</head>
			<body>
				<xsl:apply-templates/>
			</body>
		</html>
	</xsl:template>

</xsl:stylesheet>
