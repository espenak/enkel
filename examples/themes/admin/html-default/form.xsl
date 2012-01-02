<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:f="http://enkel.wsgi.net/xml/form">


	<xsl:template match="f:form">
		<form method="post" action="{@action}" class="form_">
			<xsl:if test="@id">
				<xsl:attribute name="id">
					<xsl:value-of select="@id"/>
				</xsl:attribute>
			</xsl:if>
			<xsl:apply-templates select="f:*"/>
			<div class="form_submit">
				<input type="submit" value="{@submit_label}"/>
			</div>
		</form>
	</xsl:template>

	<xsl:template match="f:form//f:group">
		<fieldset>
			<legend><xsl:value-of select="@title"/></legend>
			<xsl:apply-templates/>
		</fieldset>
	</xsl:template>

	<xsl:template match="f:form//f:hidden">
		<input type="hidden" name="{@id}" value="{text()}"/>
	</xsl:template>


	<xsl:template name="tooltip">
		<xsl:if test="local-name() != 'readonly'">
			<xsl:if test="normalize-space(f:tooltip/text()) != ''">
				<div class="form_tooltip">
					<xsl:value-of select="f:tooltip/text()"/>
				</div>
			</xsl:if>
		</xsl:if>
	</xsl:template>


	<xsl:template name="f:create-field">
		<xsl:param name="input-widget"/>
		<div>
			<xsl:attribute name="class">
				<xsl:text>form_item</xsl:text>
				<xsl:if test="@required = 'yes'">
					<xsl:text> form_item_required</xsl:text>
				</xsl:if>
			</xsl:attribute>
			<label for="{@id}">
				<xsl:value-of select="f:label/text()"/>
			</label>
			<xsl:copy-of select="$input-widget"/>
			<xsl:call-template name="tooltip"/>
			<div class="form_formerror">
				<xsl:value-of select="f:error/text()"/>
			</div>
		</div>
	</xsl:template>


	<xsl:template match="f:text">
		<xsl:variable name="w">
			<textarea id="{@id}" name="{@id}" rows="20" cols="30"
					class="form_text">
				<xsl:value-of select="f:value/text()"/>
			</textarea>
		</xsl:variable>
		<xsl:call-template name="f:create-field">
			<xsl:with-param name="input-widget" select="$w"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="f:longstring">
		<xsl:variable name="w">
			<textarea id="{@id}" name="{@id}" rows="3" cols="30"
					class="form_longstring">
				<xsl:value-of select="f:value/text()"/>
			</textarea>
		</xsl:variable>
		<xsl:call-template name="f:create-field">
			<xsl:with-param name="input-widget" select="$w"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template
			match="f:form//f:int|f:long|f:float|f:date|f:datetime|f:time">
		<xsl:variable name="w">
			<input type="text" name="{@id}" id="{@id}"
					value="{f:value/text()}"/>
		</xsl:variable>
		<xsl:call-template name="f:create-field">
			<xsl:with-param name="input-widget" select="$w"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="f:string">
		<xsl:variable name="w">
			<input type="text" name="{@id}" id="{@id}"
					value="{f:value/text()}"
					maxlength="{@length}"/>
		</xsl:variable>
		<xsl:call-template name="f:create-field">
			<xsl:with-param name="input-widget" select="$w"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="f:readonly">
		<xsl:variable name="w">
			<input type="hidden" name="{@id}" value="{f:value/text()}"/>
			<span class="form_readonly" type="text">
				<xsl:value-of select="f:value/text()"/>
			</span>
		</xsl:variable>
		<xsl:call-template name="f:create-field">
			<xsl:with-param name="input-widget" select="$w"/>
		</xsl:call-template>
	</xsl:template>


	<!-- <one> field -->

	<xsl:template match="f:onevalue/f:item">
		<option value="{@value}">
			<xsl:value-of select="text()"/>
		</option>
	</xsl:template>

	<xsl:template match="f:onevalue/f:sel_item">
		<option value="{@value}" selected="selected">
			<xsl:value-of select="text()"/>
		</option>
	</xsl:template>

	<xsl:template match="f:one">
		<xsl:variable name="w">
			<select name="{@id}" id="{@id}">
				<xsl:if test="@required = 'no'">
					<option value=""/>
				</xsl:if>
				<xsl:apply-templates select="f:onevalue"/>
			</select>
		</xsl:variable>
		<xsl:call-template name="f:create-field">
			<xsl:with-param name="input-widget" select="$w"/>
		</xsl:call-template>
	</xsl:template>


	<!-- <many> field -->

	<xsl:template match="f:manyvalue/f:item|f:sel_item">
		<xsl:variable name="id">
			<xsl:value-of select="../../@id"/>
			<xsl:value-of select="generate-id()"/>
		</xsl:variable>
		<div class="form_manyitem">
			<input type="checkbox" name="{../../@id}" id="{$id}"
					value="{@value}">
				<xsl:if test="local-name() = 'sel_item'">
					<xsl:attribute name="checked">
						<xsl:text>checked</xsl:text>
					</xsl:attribute>
				</xsl:if>
			</input>
			<label for="{$id}">
				<xsl:value-of select="text()"/>
			</label>
		</div>
	</xsl:template>

	<xsl:template match="f:many">
		<xsl:variable name="w">
			<div>
				<xsl:apply-templates select="f:manyvalue"/>
			</div>
		</xsl:variable>
		<xsl:call-template name="f:create-field">
			<xsl:with-param name="input-widget" select="$w"/>
		</xsl:call-template>
	</xsl:template>

</xsl:stylesheet>
