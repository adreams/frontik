<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="to_import.xsl"/>
<xsl:include href="to_include.xsl"/>

<xsl:template match="doc">
<html><body>
<xsl:apply-templates select="ok" mode="import"/>
<xsl:apply-templates select="ok" mode="include"/>
</body></html>
</xsl:template>

</xsl:stylesheet>

