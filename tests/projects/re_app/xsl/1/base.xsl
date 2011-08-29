<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="local.xsl"/>
<xsl:include href="../1/global.xsl"/>

<xsl:template match="doc">
<html><body>
<xsl:apply-templates select="ok" mode="local"/>
<xsl:apply-templates select="ok" mode="global"/>
</body></html>
</xsl:template>

</xsl:stylesheet>
