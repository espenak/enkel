<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:m="http://enkel.wsgi.net/xml/markup"
		xmlns:a="http://enkel.wsgi.net/xml/admin"
		xmlns:f="http://enkel.wsgi.net/xml/form">

	<xsl:import href="markup.xsl"/>
	<xsl:import href="form.xsl"/>
	<xsl:output method="html" encoding="utf-8"/>


	<xsl:template match="a:admin/a:applist/a:app">
		<li>
			<div class="applist_head">
				<xsl:value-of select="@label"/>
			</div>
			<ul>
				<xsl:for-each select="a:action">
					<li>
						<a>
							<xsl:attribute name="href">
								<xsl:text>../</xsl:text>
								<xsl:value-of select="../@id"/>
								<xsl:text>/</xsl:text>
								<xsl:value-of select="@id"/>
							</xsl:attribute>
							<xsl:value-of select="@label"/>
						</a>
					</li>
				</xsl:for-each>
			</ul>
		</li>
	</xsl:template>


	<xsl:variable name="headfont">
<xsl:text>
font-family: "Georgia", sans-serif;
font-weight: normal;
</xsl:text>
	</xsl:variable>


	<xsl:template name="main">

		<xsl:param name="color1">
			<!-- Used on page title, menu-hover and fieldset border. -->
			<xsl:text>#a72c2c</xsl:text>
		</xsl:param>
		<xsl:param name="color2">
			<!-- Border hover color -->
			<xsl:text>#000</xsl:text>
		</xsl:param>
		<xsl:param name="color3">
			<!-- Text hover color -->
			<xsl:text>#333</xsl:text>
		</xsl:param>
		<xsl:param name="color4">
			<!-- Inactive text and form-label color. -->
			<xsl:text>#888</xsl:text>
		</xsl:param>
		<html>
			<head>
				<style type="text/css">
					body{
						color: #000;
						font-family: sans-serif;
						margin: 0; padding: 0;
					}

					#body{
						margin-left: 4%;
						margin-right: 4%;
						padding: 5px 0 5px 0;
					}

					#main{
						margin-left: 210px;
					}

					#header{
						font-size: 1.6em;
						font-family: sans-serif;
						color: #fff;
						padding: 25px 4% 25px 4%;
						margin-bottom: 40px;
						background-color: #000;
					}

					<!-- structural -->
					div .markup_section{}
					div .markup_p{margin: 10px 0 10px 0;}
					pre .markup_pre
					pre .markup_prog{}

					h1{
						<xsl:value-of select="$headfont"/>;
						color: <xsl:value-of select="$color1"/>;
						font-size: 3.0em;
						margin: 0 0 30px 0;
						padding: 0;
					}
					h2, h3, h4, h5, h6{
						<xsl:value-of select="$headfont"/>;
						color: #000;
						padding: 0;
						margin: 35px 0 25px 0;
					}
					h2{font-size: 2.2em}
					h3{font-size: 1.8em}
					h3{font-size: 1.6em}
					h4{font-size: 1.4em}
					h5{font-size: 1.2em}
					h6{font-size: 1.0em}

					<!-- Inline elements -->
					a{}
					code{}
					strong{}
					em{}

					<!-- <image> -->
					.markup_image{}
					.markup_image p{}
					.markup_image img{}


					<!-- form styles -->
					form.form_{
						margin: 40px 0 40px 0;
					}
					div .form_item{
						padding: 15px 0 15px 0;
					}
					.form_item_required label{
						font-weight: bold;
					}
					.form_item label{
						display: inline-block;
						float: left;
						width: 130px;
						text-align: left;
						color: <xsl:value-of select="$color4"/>;
					}
					.form_formerror{
						margin-top: 5px;
						color: red;
						font-weight: bold;
					}
					.form_tooltip{
						color: <xsl:value-of select="$color4"/>;
						margin-top: 5px;
						font-style: italic;
					}

					.form_item input[type="text"],
					.form_item select,
					.form_item textarea{
						border-color: #ddd;
						border-width: 1px 0 3px 0;
						border-style: solid;
						padding: 3px 0 3px 0;
						color: <xsl:value-of select="$color4"/>;
					}

					.form_item input[type="text"]:hover,
					.form_item select:hover,
					.form_item textarea:hover{
						border-color: <xsl:value-of select="$color2"/>;
						color: <xsl:value-of select="$color3"/>;
					}

					.form_item input[type="text"]:focus,
					.form_item select:focus,
					.form_item textarea:focus{
						border-color: <xsl:value-of select="$color2"/>;
						background-color: #feeded;
						color: <xsl:value-of select="$color3"/>;
					}

					.form_manyitem{
						clear: both;
					}
					.form_manyitem label{
						display: block;
						float: none;
						text-align: left;
						margin-left: 0;
						color: <xsl:value-of select="$color4"/>;
					}
					.form_manyitem label{
						cursor: pointer;
					}
					.form_manyitem label:hover{
						color: <xsl:value-of select="$color3"/>;
					}
					.form_manyitem label:active{
						color: <xsl:value-of select="$color3"/>;
						font-weight: bold;
					}
					.form_manyitem input[type="checkbox"]{
						float: left;
					}

					.form_item textarea{
						border-width: 1px 1px 3px 1px;
						width: 100%;
					}

					.form_submit{margin-top: 15px;}
					.form_submit input[type="submit"]{}

					.form_ fieldset{
						margin-top: 30px;
						border-width: 3px 0 0 0;
						border-color: <xsl:value-of select="$color1"/>;
						border-style: solid;
					}
					.form_ legend{
						<xsl:value-of select="$headfont"/>;
						font-size: 1.6em;
						padding: 0 10px 0 10px;
					}


					<!-- Table -->
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


					<!-- admin -->
					#applist{
						float: left;
						width: 130px;
						margin: 0;
						padding: 0;
						list-style: none;
					}
					#applist .applist_head, #applist li a{
						padding: 12px 25px 12px 0;
						text-align: right;
						border-style: solid;
						color: <xsl:value-of select="$color4"/>;
						border-color: #eee;
						width: 100%;
					}
					#applist .applist_head{
						font-size: 1.2em;
						font-weight: bold;
						border-width: 0 5px 5px 0;
					}
					#applist li a{
						text-decoration: none;
						display: block;
						border-width: 0 5px 0 0;
					}
					#applist li a:hover{
						color: <xsl:value-of select="$color1"/>;
						border-color: <xsl:value-of select="$color2"/>;
					}
					#applist li a:active{
						font-weight: bold;
					}
					#applist li ul{
						list-style: none;
						margin: 0;
						padding: 0;
					}
				</style>
			</head>
			<body>
				<div id="header">
					Enkel administration panel
				</div>
				<div id="body">
					<ul id="applist">
						<xsl:apply-templates select="a:admin/a:applist"/>
					</ul>
					<div id="main">
						<xsl:apply-templates select="a:admin/m:section"/>
					</div>
				</div>
			</body>
		</html>
	</xsl:template>


	<xsl:template match="/">
		<xsl:call-template name="main"/>
	</xsl:template>
</xsl:stylesheet>
