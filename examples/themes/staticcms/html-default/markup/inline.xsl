<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:m="http://enkel.wsgi.net/xml/markup">


	<!--
	Inside inline elements
	-->

	<xsl:template match="m:sub|m:sup">
		<xsl:element name="{local-name()}">
			<xsl:apply-templates/>
		</xsl:element>
	</xsl:template>



	<!--
	Inline elements
	-->

	<xsl:template name="a-element">
		<a href="{@href}">
			<xsl:apply-templates/>
		</a>
	</xsl:template>

	<xsl:template match="m:a">
		<xsl:call-template name="a-element"/>
	</xsl:template>

	<xsl:template match="m:strong|m:em|m:code">
		<xsl:element name="{local-name()}">
			<xsl:choose>
				<xsl:when test="@href">
					<xsl:call-template name="a-element"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:apply-templates/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:element>
	</xsl:template>

</xsl:stylesheet>
