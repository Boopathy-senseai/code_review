import json


def format_to_json(raw_text):
    # Create a dictionary with the content key and the raw text as its value
    formatted_data = {"content": raw_text}
    # Convert the dictionary to a JSON string
    json_string = json.dumps(formatted_data, indent=2)
    return json_string


raw_text = """



 
JOVITA MENON 
 
 
 +91- 9704607245
 
 menonjovita.054@gmail.com
 
 
 
JOB OBJECTIVE
Pursue an opportunity in HR operations or team management within a multinational corporation, drawing on over a decade of experience in driving operational success, ensuring quality, and delivering exceptional customer service.
CORE COMPETENCIES
 Employee Engagement 
 Performance Management
 Diversity & Inclusion 
 Process Optimization/ Change Management 
 Employee Relations
 Succession Planning 
 Talent Development 
 Organizational Development 
 Team Building & Leadership 
EDUCATION 
 Bachelor of Commerce & Computers, Osmania University
CERTIFICATION 
 Certified Scrum Master, Scrum Alliance
 
PROFILE SUMMARY
 Nearly 12 years of experience in spearheading operations, ensuring quality, and delivering exceptional customer service within multi-national corporations.
 Orchestrated the leadership of a high-performing team, administering regular audits, addressing performance issues, directing process upgrades, and collaborating with expertise centers to address business problems.
 Currently spearheading HR operations and team management, overseeing a high-performing team of analysts/specialists, and driving process improvements to ensure top-quality service delivery for stakeholders.
 Spearheaded all phases of recruitment lifecycle for identifying the best talent from diverse sources after identification of manpower requirements starting from initial sourcing, screening, selection through offer negotiations, behavioral interviewing, placement, onboarding and relationship management.
 Strategy Architect & Change Agent; credited with implementation of innovative technology-based HR initiatives to streamline processes and capitalize on organizational growth opportunities.
 Proficient in project management, stakeholder collaboration, and effective time management, with a demonstrated ability to drive operational excellence and foster cross-departmental alignment and collaboration.
 Achieved reduction in customer complaints through a proactive escalation process and targeted training initiatives, leading to improved service delivery and customer satisfaction.
 
WORK EXPERIENCE
Sep15- Jul23 | Amazon, Hyderabad | Team Manager- Quality & HR Operations 
Growth Path:
Key Result Areas:
 Orchestrated the leadership of a high-performing team, administering regular audits and addressing performance issues.
 Directed process upgrades, identified and implemented improvements, streamlining operations and ensuring efficiency.
 Managed complex escalations, monitored resolutions, and prepared monthly dashboards and performance scorecards.
 Collaborated with expertise centers to address business problems and execute corporate-wide talent initiatives.
 Managed employee recognition programs, resolved grievances, and facilitated conflict resolutions to cultivate a collaborative and supportive work environment.
 Assessed business challenges, delivered clear observations, and offered targeted recommendations for business improvement.
 Provided 1:1 quality feedback, identified failure modes, and initiated projects on key metric improvements.
 Assisted Amazon employees in resolving complex issues, with expertise in US payroll, and provided mentorship to new hires.
Highlights:
 Spearheaded the reduction of customer complaints by 35% and increased first call resolution rate from 65% to 80% within a year.
 Conducted in-depth analyses of CSAT data sets resulting in a 15% improvement in overall team performance.
Jul14- Jul15 | Dell Technologies | Senior Advisor 
Key Results Areas:
 Implemented an escalated resolution process and conducted targeted training for team members, resulting in a notable 35% reduction in customer complaints.
 Elevated the first-call resolution rate from 65% to an impressive 80% within a year, enhancing overall customer satisfaction and optimizing the efficiency of customer service operations.
PREVIOUS EXPERIENCE 
Nov12- Jun14 | HSBC, Location | Customer Care Associate 
Jun11- Jun12 | Deloitte, Location | Customer Care Associate 
PROJECTS 
Data Analysis for CSAT Improvement 
Roles & Responsibilities:
 Thorough analysis of CSAT data revealed crucial insights, driving a 15% boost in team performance.
Data Visualization Tool Implementation 
Roles & Responsibilities:
 Introduced a novel data visualization tool for monitoring and analyzing HMD.
Cross- functional Collaboration 
Roles & Responsibilities:
 Teamed up with cross-functional groups to develop and execute customer satisfaction strategies utilizing SWOT analysis.
Communication Metrics
Roles & Responsibilities:
 Implemented comprehensive written communication metrics on Excel, resulting in a 20% surge in documenting correspondence and emails within the initial three months of project launch.
Pattern Recognitions & Recommendations 
Roles & Responsibilities:
 Performed in-depth analysis, extracting data to identify and analyze pattern recognition, and subsequently provided leadership with actionable insights and recommendations.
 
Employee Experience Specialist 
(Sep'15- Sep'17)
Senior Specialist- Training & Quality 
(Oct'17- Jun'20)
Team Manager- Quality & HR Operations
(Jun'20- Jul'23)


"""

json_data = format_to_json(raw_text)
