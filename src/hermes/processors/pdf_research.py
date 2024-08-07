import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='research_bot.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

def generate_research_pdf(filename, research_data):
    import re
    import html
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_JUSTIFY

    pdf_filename = f"{filename}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()
    
    # Modify existing styles
    styles['Title'].fontSize = 24
    styles['Title'].spaceAfter = 12
    styles['Title'].alignment = 1
    styles['Heading1'].fontSize = 20
    styles['Heading1'].spaceAfter = 16  # Reduced from 16
    styles['Heading2'].fontSize = 16
    styles['Heading2'].spaceAfter = 10  # Reduced from 12
    styles['Heading3'].fontSize = 14
    styles['Heading3'].spaceAfter = 6
    
    # Add new styles
    styles.add(ParagraphStyle(name='Justify', fontSize=12, fontName='Helvetica', alignment=TA_JUSTIFY, spaceAfter=6, leading=16))
    styles.add(ParagraphStyle(name='Reference', fontSize=10, fontName='Helvetica', leftIndent=36, firstLineIndent=-36, spaceAfter=3))
    styles.add(ParagraphStyle(name='NumberedSubheading', 
                              fontSize=12, 
                              fontName='Helvetica-Bold',
                              spaceAfter=6,  # Reduced from 10
                              spaceBefore=3))  # Reduced from 4

    def process_main_points(main_points, main_points_context, main_subpoints_body, content_list):
        def remove_numbering(text):
            # This regex matches numbers (with or without decimal points) at the start of the string,
            # optionally followed by a period and a space
            return re.sub(r'^[\d.]+\.?\s*', '', text)

        for i, (x, subpoints) in enumerate(main_points.items(), start=1):
            main_point = remove_numbering(x)
            content_list.append(Paragraph(html.escape(main_point), styles['Heading2']))
            
            if isinstance(subpoints, dict):
                for j, (y, _) in enumerate(subpoints.items(), start=1):
                    subpoint = remove_numbering(y)
                    numbered_subheading = f"{i}.{j} {subpoint}"
                    content_list.append(Paragraph(html.escape(numbered_subheading), styles['NumberedSubheading']))
                    
                    # Use the original keys to access context and subpoints body
                    sentence1 = main_points_context.get(x, {}).get(y, '')
                    sentence2 = main_subpoints_body.get(x, {}).get(y, '')
                    
                    combined_content = f"{sentence1} {sentence2}".strip()
                    if combined_content:
                        content_list.append(Paragraph(html.escape(combined_content), styles['Justify']))
                    content_list.append(Spacer(1, 6))
                
                content_list.append(Spacer(1, 6))

    content_list = []

    try:
        # Title page
        # Calculate the space needed to center the title vertically
        page_height = letter[1] - 144  # Total page height minus top and bottom margins
        title_height = styles['Title'].fontSize + styles['Title'].spaceAfter
        top_space = (page_height - title_height) / 2
        
        content_list.append(Spacer(1, top_space))
        content_list.append(Paragraph(html.escape(filename.upper()), styles['Title']))
        content_list.append(PageBreak())

        # Abstract page
        content_list.append(Paragraph("<u>Abstract</u>", styles['Heading1']))
        content_list.append(Paragraph(html.escape(research_data.get('abstract', 'No abstract available')), styles['Justify']))
        content_list.append(PageBreak())

        # Introduction
        content_list.append(Paragraph("<u>Introduction</u>", styles['Heading1']))
        intro_sections = ['overview', 'body', 'background', 'problem_statement']
        for section in intro_sections:
            content_list.append(Paragraph(html.escape(research_data.get(f'introduction_{section}', f'No {section} available')), styles['Justify']))
            content_list.append(Spacer(1, 6))

        content_list.append(PageBreak())

        # Key Findings and Analysis
        content_list.append(Paragraph("<u>Key Findings and Analysis</u>", styles['Heading1']))
        main_points = research_data.get('main_points', {})
        main_points_context = research_data.get('main_points_context', {})
        main_subpoints_body = research_data.get('main_subpoints_body', {})
        process_main_points(main_points, main_points_context, main_subpoints_body, content_list)

        content_list.append(PageBreak())

        # Case Study
        content_list.append(Paragraph("<u>Case Study</u>", styles['Heading1']))
        
        # Background
        background = research_data.get('case_study_background', 'No background available')
        content_list.append(Paragraph(html.escape(background), styles['Justify']))
        content_list.append(Spacer(1, 12))

        # Problems
        content_list.append(Paragraph("<u>Problems</u>", styles['NumberedSubheading']))
        problems = research_data.get('case_study_problems', [])
        for i, problem in enumerate(problems, 1):
            content_list.append(Paragraph(f"• {html.escape(problem)}", styles['Justify']))
        content_list.append(Spacer(1, 12))

        # Goals
        content_list.append(Paragraph("<u>Goals</u>", styles['NumberedSubheading']))
        goals = research_data.get('case_study_goals', [])
        for i, goal in enumerate(goals, 1):
            content_list.append(Paragraph(f"• {html.escape(goal)}", styles['Justify']))
        content_list.append(Spacer(1, 12))

        # Implementation
        implementation = research_data.get('case_study_implementation', [])
        implementation_text = ' '.join(implementation)
        content_list.append(Paragraph(html.escape(implementation_text), styles['Justify']))
        content_list.append(Spacer(1, 12))

        # Results
        results = research_data.get('case_study_results', 'No results available')
        content_list.append(Paragraph(html.escape(results), styles['Justify']))

        content_list.append(PageBreak())

        # Conclusion
        content_list.append(Paragraph("<u>Conclusion</u>", styles['Heading1']))
        summary = research_data.get('conclusion_summary', {})
        if isinstance(summary, dict):
            summary_text = ' '.join(summary.values())
            content_list.append(Paragraph(html.escape(summary_text), styles['Justify']))
        elif isinstance(summary, str):
            content_list.append(Paragraph(html.escape(summary), styles['Justify']))
        
        content_list.append(Spacer(1, 6))
        
        implications = research_data.get('conclusion_implications', '')
        if implications:
            content_list.append(Paragraph(html.escape(implications), styles['Justify']))

        content_list.append(PageBreak())

        # References
        content_list.append(Paragraph("<u>References</u>", styles['Heading1']))
        references = research_data.get('references', {})
        if isinstance(references, dict):
            for value in references.values():
                # Extract the URL from the reference
                url_start = value.rfind("http")
                if url_start != -1:
                    text = value[:url_start].strip()
                    url = value[url_start:].strip()
                    formatted_ref = f"{text} <i><a href='{url}' color='blue'>{url}</a></i>"
                else:
                    formatted_ref = value
                content_list.append(Paragraph(formatted_ref, styles['Reference']))
                content_list.append(Spacer(1, 6))
        elif isinstance(references, list):
            for ref in references:
                # Extract the URL from the reference
                url_start = ref.rfind("http")
                if url_start != -1:
                    text = ref[:url_start].strip()
                    url = ref[url_start:].strip()
                    formatted_ref = f"{text} <i><a href='{url}' color='blue'>{url}</a></i>"
                else:
                    formatted_ref = ref
                content_list.append(Paragraph(formatted_ref, styles['Reference']))
                content_list.append(Spacer(1, 6))
        else:
            content_list.append(Paragraph("References data is in an unexpected format", styles['Normal']))

    except Exception as e:
        logger.error(f"Error generating PDF content: {str(e)}", exc_info=True)
        content_list.append(Paragraph("An error occurred while generating the PDF. Please check the log for details.", styles['Normal']))

    try:
        doc.build(content_list)
        logger.info(f"PDF generated successfully: {pdf_filename}")
    except Exception as e:
        logger.error(f"Error building PDF: {str(e)}", exc_info=True)
        raise

    return pdf_filename