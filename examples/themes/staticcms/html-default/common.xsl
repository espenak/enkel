<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template name="create-html-doc">
		<xsl:param name="title"/>
		<xsl:param name="body"/>

		<html>
			<head>
				<meta http-equiv="Content-Type"
						content="text/html; charset=utf-8"/> 
				<title>
					<xsl:value-of select="$title"/>
				</title>

				<style type="text/css">
					body{
						color: #000;
						font-family: sans-serif;
					}

					#container{
						margin: 30px 4% 5px 4%;
					}

					#head{
						font-size: 40px;
						font-weight: bold;
						margin-bottom: 40px;
					}

					#body{
						color: #333;
						margin-left: 240px;
					}

					ul#alltags{
						width: 150px;
						list-style: none;
						padding: 0;
						margin: 0;
						left: 0;
						float: left;
					}
					ul#alltags li{
					}
					ul#alltags li a{
						padding: 12px 25px 12px 0;
						text-align: right;
						border-width: 0 5px 0 0;
						border-style: solid;
						border-color: #eee;
						text-decoration: none;
						color: #aaa;
						font-size: 1.1em;
						width: 100%;
						display: block;
					}
					ul#alltags li a:hover{
						color: #a72c2c;
						border-color: #000;
					}
					ul#alltags li a:active{
						font-weight: bold;
					}


					ul#tagindex{
						list-style: none;
						margin: 0;
						padding: 0;
					}
					ul#tagindex li{
						margin: 0 0 30px 0;
					}
					ul#tagindex li a{
						color: #000;
						font-weight: bold;
						text-decoration: underline;
						font-size: 1.1em;
					}
					ul#tagindex li a:hover{
						color: #a72c2c;
					}


					div .markup_p{margin: 10px 0 10px 0;}

					h1{
						font-family: "Georgia", serif;
						color: #a72c2c;
						font-weight: normal;
						font-size: 3.0em;
						margin: 0 0 30px -30px;
						padding: 0;
					}
					h2, h3, h4, h5, h6{
						font-family: "Georgia", serif;
						font-weight: normal;
						color: #000;
						padding: 0;
						margin: 35px 0 25px 0;
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
<div id="container">
	<div id="head">
		<xsl:choose>
			<xsl:when test="$page-logo = 'no'">
				<xsl:value-of select="$page-title"/>
			</xsl:when>
			<xsl:otherwise>
				<img src="{$page-logo}" alt="{$page-title}"/>
			</xsl:otherwise>
		</xsl:choose>
	</div>

	<ul id="alltags">
		<xsl:choose>
			<xsl:when test="$sort-tags = 'postcount'">
				<xsl:for-each select="document($tags-file)/tags/tag">
					<xsl:sort select="count(post)" order="descending"
						data-type="number"/>
					<xsl:call-template name="taglist-tag"/>
				</xsl:for-each>
			</xsl:when>
			<xsl:otherwise>
				<xsl:for-each select="document($tags-file)/tags/tag">
					<xsl:sort select="@id"/>
					<xsl:call-template name="taglist-tag"/>
				</xsl:for-each>
			</xsl:otherwise>
		</xsl:choose>
	</ul>

	<div id="body">
		<xsl:copy-of select="$body"/>
	</div>
</div>
			</body>
		</html>
	</xsl:template>

	<xsl:template name="taglist-tag">
		<li>
			<a href="{$tagfile-prefix}{@id}.{$tagfile-extension}">
				<xsl:value-of select="@name"/>
			</a>
		</li>
	</xsl:template>

</xsl:stylesheet>
