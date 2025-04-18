def xml_string_to_formatted_html(xml_string):
    """
    Convert XML string to formatted HTML for better display
    
    Args:
        xml_string (str): XML document as a string
        
    Returns:
        str: Formatted HTML representation of the XML
    """
    from lxml import etree
    
    try:
        root = etree.fromstring(xml_string.encode('utf-8') if isinstance(xml_string, str) else xml_string)
        
        pretty_xml = etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8')
        
        html_safe_xml = pretty_xml.replace('<', '&lt;').replace('>', '&gt;')
        
        highlighted_xml = html_safe_xml.replace('&lt;', '<span class="xml-tag">&lt;').replace(
            '&gt;', '&gt;</span>')
        
        return f'<pre class="xml-code">{highlighted_xml}</pre>'
    except Exception as e:
        return f'<p>Error formatting XML: {str(e)}</p><pre>{xml_string}</pre>'