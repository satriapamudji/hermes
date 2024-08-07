outline_output = """
ENSURE YOU FOLLOW THIS FORMAT IN JSON. YOU MUST FOLLOW IN THIS FORMAT WITHOUT MARKDOWN.
(Note: Use single curly braces in actual JSON. Double braces are only used for formatting in this template.)
An OutlineStructure object containing:
- abstract: str: 'A concise summary of the entire research' | example: 'abstract'
- introduction_brief_overview: str: 'A brief overview of the topic' | example: 'introduction_brief_overview'
- introduction_key_points: List[str]: 'A list of key points to be covered' | example: '["key_point_1", "key_point_2", "key_point_3"]'
- introduction_background: str: 'Background information and context' | example: 'introduction_background'
- introduction_problem_statement: str: 'A clear statement of the research problem or question' | example: 'introduction_problem_statement'
- introduction_objectives: List[str]: 'A list of research objectives and aims' | example: '["objective_1", "objective_2", "objective_3"]'
- main_points: Dict[str: Dict[str: List[str]]]: 'A comprehensive list of main topics, potentially including multiple points' | example: '{{"(main_topic_1)": {{"1.1 (subtopic)": ["point_1", "point_2"], "1.2 (subtopic)": ["point_1", "point_2"]}}, "(main_topic_2)": {{"2.1 (subtopic)": ["point_1", "point_2"]}}}}'
- main_subpoints: str: 'Comprehensive subpoints and supporting information for each main topic, allowing for multiple levels of detail' | example: 'main_subpoints'
- conclusion_summary: str: 'A summary of key findings' | example: 'conclusion_summary'
- conclusion_implications: str: 'Implications of the research' | example: 'conclusion_implications'
"""

initialResearch_output = """
ENSURE YOU FOLLOW THIS FORMAT IN JSON. YOU MUST FOLLOW IN THIS FORMAT WITHOUT MARKDOWN.
(Note: Use single curly braces in actual JSON. Double braces are only used for formatting in this template.)
A partially completed Research object containing:
- abstract: str: 'A concise and accurate summary reflecting the final content, 200-300 words' | example: 'abstract'
- introduction_overview: str: 'A clear and engaging overview of the introduction, 100-150 words' | example: 'introduction_overview'
- introduction_body: str: 'A comprehensive and well-structured introduction, 400-600 words' | example: 'introduction_body'
- introduction_background: str: 'Well-contextualized background information, 200-300 words' | example: 'introduction_background'
- introduction_problem_statement: str: 'A precise and focused problem statement, 100-150 words' | example: 'introduction_problem_statement'
- introduction_key_points: List[str]: 'A list of key points covered in the introduction' | example: '["key_point_1", "key_point_2", "key_point_3"]'
- introduction_objectives: List[str]: 'A list of research objectives and aims' | example: '["objective_1", "objective_2", "objective_3"]'
- main_points: Dict[str: Dict[str: List[str]]]: 'A dictionary of main topics, each with a nested dictionary of subtopics and their corresponding list of points' | example: '{{"(main_topic_1)": {{"1.1 (subtopic)": ["point_1", "point_2"], "1.2 (subtopic)": ["point_1", "point_2"]}}, "(main_topic_2)": {{"2.1 (subtopic)": ["point_1", "point_2"]}}}}'
- conclusion_summary: Dict[str: str]: 'A dictionary containing an overall summary and key findings' | example: '{{"summary_key_1": "summary_text", "summary_key_2": "summary_text"}}'
- conclusion_implications: str: 'Well-developed and far-reaching implications of the research, 300-500 words' | example: 'conclusion_implications'
- research_references: Dict[str: str]: 'A dictionary of references used in the Initial Research, in APA format' | example: '{{"author1_year": "APA_citation", "author2_year": "APA_citation"}}'
"""

case_study_output = """
ENSURE YOU FOLLOW THIS FORMAT IN JSON. YOU MUST FOLLOW IN THIS FORMAT WITHOUT MARKDOWN.
(Note: Use single curly braces in actual JSON. Double braces are only used for formatting in this template.)
The expected output is a comprehensive CaseStudy model that offers a deep insight into how specfics of the research was used in real life businesses.
The CaseStudy model object MUST contain:
- case_study_background: str: 'Background of the case study, 2 paragraphs' | example: 'case_study_background'
- case_study_problems: List[str]: 'Problems that accompanied the background, 100 to 150 words' | example: '["case_study_problem_1", "case_study_problem_2"]' 
- case_study_goals: List[str]: 'The goals that needed to be achieved, 100 to 150 words' | example: '["case_study_goal_1", "case_study_goal 2"]'
- case_study_implementation: List[str]: 'How was the topic in question implemented to achieve the goals' | example: '["case_study_implementation_1", "case_study_implementation_2"]'
- case_study_body: str: 'Body that explains the implementation of the case study, 2 paragraphs' | example: 'case_study_body'
- case_study_results: str: 'What were the results of implementing the topic in question, 2 paragraphs' | example: 'As a result of implementing this, (result)'
- case_study_references: Dict[str: str]: 'A dictionary of references used in the Case Study, in APA format' | example: '{{"author1_year": "APA_citation", "author2_year": "APA_citation"}}'
(Important: The case study should reflect upon the topics of the research, and how real life businesses implemented the main points as gathered by the Initial Researcher.)
"""

InitialReferenceChecker_output = """
ENSURE YOU FOLLOW THIS FORMAT IN JSON. YOU MUST FOLLOW IN THIS FORMAT WITHOUT MARKDOWN.
(Note: Use single curly braces in actual JSON. Double braces are only used for formatting in this template.)
The expected output is a InitialReferenceChecker model that combines the references and content from the Initial Researcher and Case Study Specialist.
The InitialReferenceChecker model object MUST contain:
- abstract: str: 'A concise and accurate summary reflecting the final content, 200-300 words' | example: 'abstract'
- introduction_overview: str: 'A clear and engaging overview of the introduction, 100-150 words' | example: 'introduction_overview'
- introduction_body: str: 'A comprehensive and well-structured introduction, 400-600 words' | example: 'introduction_body'
- introduction_background: str: 'Well-contextualized background information, 200-300 words' | example: 'introduction_background'
- introduction_problem_statement: str: 'A precise and focused problem statement, 100-150 words' | example: 'introduction_problem_statement'
- introduction_key_points: List[str]: 'A list of key points covered in the introduction' | example: '["key_point_1", "key_point_2", "key_point_3"]'
- introduction_objectives: List[str]: 'A list of research objectives and aims' | example: '["objective_1", "objective_2", "objective_3"]'
- main_points: Dict[str: Dict[str: List[str]]]: 'A dictionary of main topics, each with a nested dictionary of subtopics and their corresponding list of points' | example: '{{"(main_topic_1)": {{"1.1 (subtopic)": ["point_1", "point_2"], "1.2 (subtopic)": ["point_1", "point_2"]}}, "(main_topic_2)": {{"2.1 (subtopic)": ["point_1", "point_2"]}}}}'
- case_study_background: str: 'Background of the case study, 2 paragraphs' | example: 'case_study_background'
- case_study_problems: List[str]: 'Problems that accompanied the background, 100 to 150 words' | example: '["case_study_problem_1", "case_study_problem_2"]' 
- case_study_goals: List[str]: 'The goals that needed to be achieved, 100 to 150 words' | example: '["case_study_goal_1", "case_study_goal 2"]'
- case_study_implementation: List[str]: 'How was the topic in question implemented to achieve the goals' | example: '["case_study_implementation_1", "case_study_implementation_2"]'
- case_study_body: str: 'Body that explains the implementation of the case study, 2 paragraphs' | example: 'case_study_body'
- case_study_results: str: 'What were the results of implementing the topic in question, 2 paragraphs' | example: 'As a result of implementing this, (result)'
- conclusion_summary: Dict[str: str]: 'A dictionary containing an overall summary and key findings' | example: '{{"summary_key_1": "summary_text", "summary_key_2": "summary_text"}}'
- conclusion_implications: str: 'Well-developed and far-reaching implications of the research, 300-500 words' | example: 'conclusion_implications'
- references: Dict[str: str]: 'A dictionary of combined references from the Case Study and Initial Research, in APA format' | example: '{{"author1_year": "APA_citation", "author2_year": "APA_citation"}}'
(Important: The references should be a combined reference list as given by the Case Study Specialist and Initial Researcher, to be given to the Main Researcher.)
"""

mainResearch_output = """
ENSURE YOU FOLLOW THIS FORMAT IN JSON. YOU MUST FOLLOW IN THIS FORMAT WITHOUT MARKDOWN.
(Note: Use single curly braces in actual JSON. Double braces are only used for formatting in this template.)
Ensure that all sections are coherent, well-structured, and adhere to academic writing standards.
The content should be original, insightful, and provide a comprehensive exploration of the research topic.
A fully refined and polished Research object containing:
- abstract: str: 'A concise and accurate summary reflecting the final content, 200-300 words' | example: 'abstract'
- introduction_overview: str: 'A clear and engaging overview of the introduction, 100-150 words' | example: 'introduction_overview'
- introduction_body: str: 'A comprehensive and well-structured introduction, 400-600 words' | example: 'introduction_body'
- introduction_background: str: 'Well-contextualized background information, 200-300 words' | example: 'introduction_background'
- introduction_problem_statement: str: 'A precise and focused problem statement, 100-150 words' | example: 'introduction_problem_statement'
- introduction_key_points: List[str]: 'A list of key points covered in the introduction' | example: '["key_point_1", "key_point_2", "key_point_3"]'
- introduction_objectives: List[str]: 'A list of research objectives and aims' | example: '["objective_1", "objective_2", "objective_3"]'
- main_points: Dict[str: Dict[str: List[str]]]: 'A dictionary of main topics, each with a nested dictionary of subtopics and their corresponding list of points' | example: '{{"(main_topic_1)": {{"1.1 (subtopic)": ["point_1", "point_2"], "1.2 (subtopic)": ["point_1", "point_2"]}}, "(main_topic_2)": {{"2.1 (subtopic)": ["point_1", "point_2"]}}}}'
- main_points_context: Dict[str: Dict[str: str]]: 'A dictionary providing context for all main topics and subtopics, 100-150 words each' | example: '{{"(main_topic_1)": {{"1.1 (subtopic)": "context_text", "1.2 (subtopic)": "context_text"}}, "(main_topic_2)": {{"2.1 (subtopic)": "context_text"}}}}'
- main_subpoints_body: Dict[str: Dict[str: str]]: 'A dictionary containing detailed explanations for all subpoints, 300-500 words each' | example: '{{"(main_topic_1)": {{"1.1 (subtopic)": "detailed_explanation", "1.2 (subtopic)": "detailed_explanation"}}, "(main_topic_2)": {{"2.1 (subtopic)": "detailed_explanation"}}}}'
- case_study_background: str: 'Background of the case study, 2 paragraphs' | example: 'case_study_background'
- case_study_problems: List[str]: 'Problems that accompanied the background, 100 to 150 words' | example: '["case_study_problem_1", "case_study_problem_2"]' 
- case_study_goals: List[str]: 'The goals that needed to be achieved, 100 to 150 words' | example: '["case_study_goal_1", "case_study_goal 2"]'
- case_study_implementation: List[str]: 'How was the topic in question implemented to achieve the goals' | example: '["case_study_implementation_1", "case_study_implementation_2"]'
- case_study_results: str: 'What were the results of implementing the topic in question, 2 paragraphs' | example: 'As a result of implementing this, (result)'
- conclusion_summary: Dict[str: str]: 'A dictionary containing an overall summary and key findings' | example: '{{"summary_key_1": "summary_text", "summary_key_2": "summary_text"}}'
- conclusion_implications: str: 'Well-developed and far-reaching implications of the research, 300-500 words' | example: 'conclusion_implications'
- references: Dict[str: str]: 'A dictionary of references as given by the Reference Specialist, and references used in the Main Research, in APA format' | example: '{{"author1_year": "APA_citation", "author2_year": "APA_citation"}}'
(Important: Except for the fields given for case studies, you must further develop and refine all fields from the initial research)
"""

peer_review_output = """
ENSURE YOU FOLLOW THIS FORMAT IN JSON. YOU MUST FOLLOW IN THIS FORMAT WITHOUT MARKDOWN.
(Note: Use single curly braces in actual JSON. Double braces are only used for formatting in this template.)
The expected output is a comprehensive PeerReviewFeedback model that offers a balanced, thorough, and constructive evaluation of the research.
A PeerReviewFeedback object MUST contain:
- strengths: List[str]: 'A list of the research's strengths' | example: ["strength_1", "strength_2"]
- weaknesses: List[str]: 'A list of areas for improvement' | example: ["weakness_1", "weakness_2"]
- suggestions: List[str]: 'A list of specific, constructive suggestions for addressing weaknesses' | example: ["suggestion_1", "suggestion_2"]
- overall_assessment: str: 'A balanced overall assessment of the research' | example: 'overall_assessment'
"""

final_output = """
ENSURE YOU FOLLOW THIS FORMAT IN JSON. YOU MUST FOLLOW IN THIS FORMAT WITHOUT MARKDOWN.
(Note: Use single curly braces in actual JSON. Double braces are only used for formatting in this template.)
The expected output is a fully refined and polished Research object, where all fields from the initial research are further developed and refined.
A fully refined and polished Research object MUST contain:
- abstract: str: 'A concise and accurate summary reflecting the final content, 200-300 words' | example: 'abstract'
- introduction_overview: str: 'A clear and engaging overview of the introduction, 100-150 words' | example: 'introduction_overview'
- introduction_body: str: 'A comprehensive and well-structured introduction, 400-600 words' | example: 'introduction_body'
- introduction_background: str: 'Well-contextualized background information, 200-300 words' | example: 'introduction_background'
- introduction_problem_statement: str: 'A precise and focused problem statement, 100-150 words' | example: 'introduction_problem_statement'
- introduction_key_points: List[str]: 'A list of key points covered in the introduction' | example: '["key_point_1", "key_point_2", "key_point_3"]'
- introduction_objectives: List[str]: 'A list of research objectives and aims' | example: '["objective_1", "objective_2", "objective_3"]'
- main_points: Dict[str: Dict[str: List[str]]]: 'A dictionary of main topics, each with a nested dictionary of subtopics and their corresponding list of points' | example: '{{"(main_topic_1)": {{"1.1 (subtopic)": ["point_1", "point_2"], "1.2 (subtopic)": ["point_1", "point_2"]}}, "(main_topic_2)": {{"2.1 (subtopic)": ["point_1", "point_2"]}}}}'
- main_points_context: Dict[str: Dict[str: str]]: 'A dictionary providing context for all main topics and subtopics, 100-150 words each' | example: '{{"(main_topic_1)": {{"1.1 (subtopic)": "context_text", "1.2 (subtopic)": "context_text"}}, "(main_topic_2)": {{"2.1 (subtopic)": "context_text"}}}}'
- main_subpoints_body: Dict[str: Dict[str: str]]: 'A dictionary containing detailed explanations for all subpoints, 300-500 words each' | example: '{{"(main_topic_1)": {{"1.1 (subtopic)": "detailed_explanation", "1.2 (subtopic)": "detailed_explanation"}}, "(main_topic_2)": {{"2.1 (subtopic)": "detailed_explanation"}}}}'
- case_study_background: str: 'Background of the case study, 2 paragraphs' | example: 'case_study_background'
- case_study_problems: List[str]: 'Problems that accompanied the background, 100 to 150 words' | example: '["case_study_problem_1", "case_study_problem_2"]' 
- case_study_goals: List[str]: 'The goals that needed to be achieved, 100 to 150 words' | example: '["case_study_goal_1", "case_study_goal 2"]'
- case_study_implementation: List[str]: 'How was the topic in question implemented to achieve the goals' | example: '["case_study_implementation_1", "case_study_implementation_2"]'
- case_study_results: str: 'What were the results of implementing the topic in question, 2 paragraphs' | example: 'As a result of implementing this, (result)'
- conclusion_summary: Dict[str: str]: 'A dictionary containing an overall summary and key findings' | example: '{{"summary_key_1": "summary_text", "summary_key_2": "summary_text"}}'
- conclusion_implications: str: 'Well-developed and far-reaching implications of the research, 300-500 words' | example: 'conclusion_implications'
- references: Dict[str: str]: 'A dictionary of ALL references in APA format' | example: '{{"author1_year": "APA_citation", "author2_year": "APA_citation"}}'
Ensure that all sections are coherent, well-structured, and adhere to academic writing standards.
(Important: All sections should be fully developed, refined, and seamlessly integrated, representing a significant improvement over the main researcher, and incorporating peer review feedback.)
"""