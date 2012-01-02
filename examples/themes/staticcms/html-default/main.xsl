<?xml version="1.0" encoding="utf-8"?>


<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:s="http://enkel.wsgi.net/xml/staticcms"
		xmlns:m="http://enkel.wsgi.net/xml/markup"
		exclude-result-prefixes="s m">

	<xsl:import href="markup.xsl"/>
	<xsl:include href="common.xsl"/>
	<xsl:include href="tags.xsl"/>
	<xsl:include href="post.xsl"/>


	<!-- required parameters: "tmp-folder" -->

	<!-- The title of the page. -->
	<xsl:param name="title">
		<xsl:text>Enkel staticcms</xsl:text>
	</xsl:param>

	<!-- The logo of the page. Should be the url to a
	image. "title" is used as alternative text. -->
	<xsl:param name="logo">
		<xsl:text>no</xsl:text>
	</xsl:param>

	<!-- the sort order of the taglist.
		postcount: By number of posts in the tag.
		alpha: By id alphabetically.
	-->
	<xsl:param name="sort-tags">
		<xsl:text>postcount</xsl:text>
	</xsl:param>

	<!-- the sort order of the postlists.
		mtime: Last modified first.
		alpha: By id alphabetically.
	-->
	<xsl:param name="sort-posts">
		<xsl:text>mtime</xsl:text>
	</xsl:param>

	<xsl:param name="postfile-prefix">
		<xsl:text>post-</xsl:text>
	</xsl:param>
	<xsl:param name="postfile-extension">
		<xsl:text>html</xsl:text>
	</xsl:param>

	<xsl:param name="tagfile-prefix">
		<xsl:text>tag-</xsl:text>
	</xsl:param>
	<xsl:param name="tagfile-extension">
		<xsl:text>html</xsl:text>
	</xsl:param>


	<xsl:variable name="tags-file">
		<xsl:value-of select="$tmp-folder"/>
		<xsl:text>/tags.xml</xsl:text>
	</xsl:variable>
	<xsl:variable name="out-folder">
		<xsl:value-of select="$tmp-folder"/>
		<xsl:text>/out</xsl:text>
	</xsl:variable>

	<xsl:variable name="page-title">
		<xsl:value-of select="$title"/>
	</xsl:variable>
	<xsl:variable name="page-logo">
		<xsl:value-of select="$logo"/>
	</xsl:variable>


	<xsl:template name="create-post-files">
		<xsl:for-each select="/posts/post">
			<xsl:document
					href="{$out-folder}/{$postfile-prefix}{@id}.{$postfile-extension}"
					method="html">
				<xsl:apply-templates select="document(@src)/s:post"/>
			</xsl:document>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="create-tag-files">
		<xsl:for-each select="document($tags-file)/tags/tag">
			<xsl:document
					href="{$out-folder}/{$tagfile-prefix}{@id}.{$tagfile-extension}"
					method="html">
				<xsl:call-template name="create-tag-file"/>
			</xsl:document>
		</xsl:for-each>
	</xsl:template>

	<xsl:template match="/">
		<xsl:call-template name="create-post-files"/>
		<xsl:call-template name="create-tag-files"/>
	</xsl:template>

</xsl:stylesheet>
