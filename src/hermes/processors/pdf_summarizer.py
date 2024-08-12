import re
import html
from difflib import SequenceMatcher

def find_best_match(search_text, content, is_audio=True, threshold=0.6):
    """Find the best matching substring in either a single transcript or across multiple documents."""
    search_text = search_text.strip().strip('.').strip()
    best_ratio = 0
    best_match = ""
    best_index = -1
    best_doc_num = -1

    if is_audio:
        # For audio transcripts
        full_text = content.lower()
        for i in range(len(full_text) - len(search_text) + 1):
            substring = full_text[i:i + len(search_text)]
            ratio = SequenceMatcher(None, search_text, substring).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = substring
                best_index = i
                best_doc_num = 1  # Always 1 for audio transcripts
    else:
        # For multiple documents
        for doc in content:
            doc_num = doc['doc_number']
            full_text = doc['text'].lower()
            for i in range(len(full_text) - len(search_text) + 1):
                substring = full_text[i:i + len(search_text)]
                ratio = SequenceMatcher(None, search_text, substring).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = substring
                    best_index = i
                    best_doc_num = doc_num

    if best_ratio >= threshold:
        return {
            'match': best_match,
            'index': best_index,
            'doc_number': best_doc_num
        }
    else:
        return None

def escape_html_like(text):
    """
    Escape HTML-like content in the text while preserving ReportLab's formatting tags and handling nested tags.
    """
    preserved_tags = ['b', 'i', 'u', 'super', 'sub', 'a', 'font', 'para']
    
    # Function to replace matched tags with placeholders
    def replace_tag(match):
        tag = match.group(1)
        if tag in preserved_tags:
            return f"{{{{TAG_{len(placeholders)}}}}}}}"
        return match.group(0)

    # Find all tags and replace them with placeholders
    placeholders = []
    pattern = r'<(/?)(\w+)([^>]*)>'
    text = re.sub(pattern, lambda m: replace_tag(m), text)

    # Escape the HTML
    text = html.escape(text)

    # Restore the preserved tags
    for i, tag in enumerate(placeholders):
        text = text.replace(f"{{{{TAG_{i}}}}}}}", tag)

    return text

def generate_summarize_pdf(filename, content, summary_data, is_audio=True):
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors

    pdf_filename = f"{filename}.pdf"
    doc_template = SimpleDocTemplate(pdf_filename, pagesize=letter,
                                     rightMargin=72, leftMargin=72,
                                     topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='UnderlinedHeader', fontSize=16, fontName='Helvetica-Bold', underline=True))
    styles.add(ParagraphStyle(name='KeyPoint', fontSize=14, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SubPoint', fontSize=12, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='NormalText', fontSize=10, fontName='Helvetica'))
    styles.add(ParagraphStyle(name='LinkStyle', parent=styles['Normal'], textColor=colors.blue, alignment=TA_LEFT))

    def create_link(destination, text):
        return f'<link href="#{destination}">{escape_html_like(text)}</link>'

    content_list = []

    # Add title
    content_list.append(Paragraph(escape_html_like(filename.upper()), styles['Title']))
    content_list.append(Spacer(1, 24))

    # Add summary
    content_list.append(Paragraph("<u>Summary</u>", styles['UnderlinedHeader']))
    content_list.append(Spacer(1, 20))
    content_list.append(Paragraph(escape_html_like(summary_data['summary']), styles['Justify']))
    content_list.append(Spacer(1, 28))

    # Add key points
    content_list.append(Paragraph("<u>Key Points</u>", styles['UnderlinedHeader']))
    content_list.append(Spacer(1, 20))
    for i, point in enumerate(summary_data['key_points'], 1):
        key_point_anchor = f"key_point_{i}"
        content_list.append(Paragraph(f'<a name="{key_point_anchor}"/>{i}. {escape_html_like(point["point"])}', styles['KeyPoint']))
        content_list.append(Spacer(1, 8))
        content_list.append(Paragraph(escape_html_like(point['explanation']), styles['NormalText']))
        content_list.append(Spacer(1, 16))
        if 'sub_points' in point:
            for j, sub_point in enumerate(point['sub_points'], 1):
                content_list.append(Paragraph(f"  {i}.{j}. {escape_html_like(sub_point['sub_point'])}", styles['SubPoint']))
                content_list.append(Spacer(1, 6))
                content_list.append(Paragraph(escape_html_like(sub_point['sub_explanation']), styles['NormalText']))
                if 'sub_reference' in sub_point:
                    content_list.append(Spacer(1, 4))
                    ref = sub_point['sub_reference']
                    ref_anchor = f"ref_{i}_{j}"
                    link = create_link(ref_anchor, ref)
                    content_list.append(Paragraph(f"<b>Reference:</b> <span color='blue'>{link}</span>", styles['NormalText']))
                content_list.append(Spacer(1, 12))
        content_list.append(Spacer(1, 12))

    # Add references
    content_list.append(PageBreak())
    content_list.append(Paragraph("<u>References</u>", styles['UnderlinedHeader']))
    content_list.append(Spacer(1, 12))

    for i, point in enumerate(summary_data['key_points'], 1):
        if 'sub_points' in point:
            for j, sub_point in enumerate(point['sub_points'], 1):
                if 'sub_reference' in sub_point:
                    ref = sub_point['sub_reference']
                    ref_anchor = f"ref_{i}_{j}"
                    content_list.append(Paragraph(f'<a name="{ref_anchor}"/><b>{escape_html_like(ref)}</b>', styles['NormalText']))
                    
                    first_line = sub_point.get('sub_reference_first_line', '')
                    last_line = sub_point.get('sub_reference_last_line', '')
                    
                    if first_line and last_line:
                        first_content = re.sub(r'^(Line |Document \d+, Line )\d+:\s*', '', first_line).strip()
                        last_content = re.sub(r'^(Line |Document \d+, Line )\d+:\s*', '', last_line).strip()
                        
                        start_match = find_best_match(first_content.lower(), content, is_audio)
                        end_match = find_best_match(last_content.lower(), content, is_audio)
                        
                        if start_match and end_match:
                            if is_audio:
                                full_text = content
                            else:
                                document = next((d for d in content if d['doc_number'] == start_match['doc_number']), None)
                                if document:
                                    full_text = document['text']
                                    content_list.append(Paragraph(f"Document: {escape_html_like(document['file_name'])}", styles['NormalText']))
                                else:
                                    content_list.append(Paragraph("Unable to locate referenced document.", styles['NormalText']))
                                    continue

                            start_index = start_match['index']
                            end_index = end_match['index'] + len(end_match['match'])
                            if start_index < end_index:
                                referenced_text = full_text[start_index:end_index]
                                content_list.append(Paragraph(escape_html_like(f"...{referenced_text}..."), styles['NormalText']))
                            else:
                                content_list.append(Paragraph("Unable to locate referenced content in correct order.", styles['NormalText']))
                        else:
                            content_list.append(Paragraph("Unable to find matching content.", styles['NormalText']))
                    else:
                        content_list.append(Paragraph("Unable to extract referenced lines.", styles['NormalText']))
                    content_list.append(Spacer(1, 12))

    # Add full content
    content_list.append(PageBreak())
    if is_audio:
        content_list.append(Paragraph("<u>Full Transcript</u>", styles['UnderlinedHeader']))
        content_list.append(Spacer(1, 12))
        content_list.append(Paragraph(escape_html_like(content), styles['NormalText']))
    else:
        content_list.append(Paragraph("<u>Full Documents</u>", styles['UnderlinedHeader']))
        content_list.append(Spacer(1, 12))
        for document in content:
            content_list.append(Paragraph(f"Document {document['doc_number']}: {escape_html_like(document['file_name'])}", styles['SubPoint']))
            content_list.append(Spacer(1, 6))
            content_list.append(Paragraph(escape_html_like(document['text']), styles['NormalText']))
            content_list.append(Spacer(1, 12))

    # Build the PDF
    doc_template.build(content_list)
    return pdf_filename