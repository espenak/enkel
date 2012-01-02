<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:m="http://enkel.wsgi.net/xml/markup">


	<xsl:template match="m:image">
		<img src="{@href}">
			<xsl:attribute name="style">
				<xsl:choose>
					<xsl:when test="@display = 'inline'">
						<xsl:text>display:inline;float:none;</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:text>display:block;clear:both;</xsl:text>
						<xsl:choose>
							<xsl:when test="@float">
								<xsl:text>float:</xsl:text>
								<xsl:value-of select="@float"/>
								<xsl:text>;</xsl:text>
							</xsl:when>
							<xsl:otherwise>
								<xsl:text>float=none;</xsl:text>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:if test="@alt">
				<xsl:attribute name="alt">
					<xsl:value-of select="@alt"/>
				</xsl:attribute>
			</xsl:if>
		</img>
	</xsl:template>

</xsl:stylesheet>
