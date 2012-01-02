<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:m="http://enkel.wsgi.net/xml/markup">


	<xsl:template match="m:p|m:section">
		<div class="markup_{local-name()}">
			<xsl:apply-templates/>
		</div>
	</xsl:template>

	<xsl:template match="m:pre|m:prog">
		<pre class="markup_{local-name()}">
			<xsl:apply-templates/>
		</pre>
	</xsl:template>


	<!--
	headings
	-->

	<xsl:template match="m:section/m:h">
		<h1>
			<xsl:apply-templates/>
		</h1>
	</xsl:template>

	<xsl:template match="m:section/m:section/m:h">
		<h2>
			<xsl:apply-templates/>
		</h2>
	</xsl:template>

	<xsl:template match="m:section/m:section/m:section/m:h">
		<h3>
			<xsl:apply-templates/>
		</h3>
	</xsl:template>

	<xsl:template match="m:section/m:section/m:section/m:section/m:h">
		<h4>
			<xsl:apply-templates/>
		</h4>
	</xsl:template>

	<xsl:template match="m:section/m:section/m:section/m:section/m:section/m:h">
		<h5>
			<xsl:apply-templates/>
		</h5>
	</xsl:template>

	<xsl:template match="m:section/m:section/m:section/m:section/m:section/m:section/m:h">
		<h6>
			<xsl:apply-templates/>
		</h6>
	</xsl:template>

</xsl:stylesheet>
