<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:m="http://enkel.wsgi.net/xml/markup">

	<xsl:template name="table-cell">
		<xsl:param name="name"/>
		<xsl:element name="{$name}">
			<xsl:if test="@rowspan">
				<xsl:attribute name="rowspan">
					<xsl:value-of select="@rowspan"/>
				</xsl:attribute>
			</xsl:if>
			<xsl:if test="@colspan">
				<xsl:attribute name="colspan">
					<xsl:value-of select="@colspan"/>
				</xsl:attribute>
			</xsl:if>
			<xsl:apply-templates/>
		</xsl:element>
	</xsl:template>

	<xsl:template match="m:row/m:cell">
		<xsl:variable name="name">
			<xsl:text>td</xsl:text>
		</xsl:variable>
		<xsl:call-template name="table-cell">
			<xsl:with-param name="name" select="$name"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="m:hrow/m:hcell">
		<xsl:variable name="name">
			<xsl:text>th</xsl:text>
		</xsl:variable>
		<xsl:call-template name="table-cell">
			<xsl:with-param name="name" select="$name"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="m:row|m:hrow">
		<tr>
			<xsl:apply-templates/>
		</tr>
	</xsl:template>

	<xsl:template match="m:table">
		<table>
			<xsl:apply-templates/>
		</table>
	</xsl:template>

</xsl:stylesheet>
