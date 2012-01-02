<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:s="http://enkel.wsgi.net/xml/staticcms"
		xmlns:m="http://enkel.wsgi.net/xml/markup"
		exclude-result-prefixes="s m">


	<xsl:template name="a-element">
		<a>
			<xsl:choose>
				<xsl:when test="@href">
					<xsl:attribute name="href">
						<xsl:value-of select="@href"/>
					</xsl:attribute>
				</xsl:when>
				<xsl:when test="@s:post">
					<xsl:attribute name="href">
						<xsl:value-of select="$postfile-prefix"/>
						<xsl:value-of select="@s:post"/>
						<xsl:text>.</xsl:text>
						<xsl:value-of select="$postfile-extension"/>
					</xsl:attribute>
				</xsl:when>
				<xsl:when test="@s:tag">
					<xsl:attribute name="href">
						<xsl:value-of select="$tagfile-prefix"/>
						<xsl:value-of select="@s:tag"/>
						<xsl:text>.</xsl:text>
						<xsl:value-of select="$tagfile-extension"/>
					</xsl:attribute>
				</xsl:when>
			</xsl:choose>
			<xsl:apply-templates/>
		</a>
	</xsl:template>

	<xsl:template match="m:strong|m:em|m:code">
		<xsl:element name="{local-name()}">
			<xsl:choose>
				<xsl:when test="@href|@s:post|@s:tag">
					<xsl:call-template name="a-element"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:apply-templates/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:element>
	</xsl:template>


	<!-- Called once for each post. -->
	<xsl:template match="s:post">
		<xsl:call-template name="create-html-doc">
			<xsl:with-param name="body">
				<div id="post-body">
					<xsl:apply-templates select="m:section"/>
				</div>
			</xsl:with-param>
		</xsl:call-template>
	</xsl:template>

</xsl:stylesheet>
