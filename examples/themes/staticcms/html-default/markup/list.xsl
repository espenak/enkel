<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:m="http://enkel.wsgi.net/xml/markup">

	<xsl:template match="m:li">
		<li>
			<xsl:apply-templates/>
		</li>
	</xsl:template>

	<xsl:template match="m:ul|m:ol">
		<xsl:element name="{local-name()}">
			<xsl:apply-templates/>
		</xsl:element>
	</xsl:template>

</xsl:stylesheet>
