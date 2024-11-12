import json


def format_to_json(raw_text):
    # Create a dictionary with the content key and the raw text as its value
    formatted_data = {"content": raw_text}
    # Convert the dictionary to a JSON string
    json_string = json.dumps(formatted_data, indent=2)
    return json_string


criteria = "Skills,Industry Specific Experience,Roles and Responsibilities,Domain Specific Experience,Experience,Certification,Technical Tools and Languages,Location Alignment,Soft Skills,Cultural Fit,Qualification,References and Recommendation"


jd = """

Are you a board-certified rheumatologist in India looking to expand your impact within the realm of immunology? Sense7ai Healthcare Division seeks a professional like you for a pivotal role with a prestigious yet confidential US-based client. This contract-based opportunity is focused on transforming patient care by shifting from broad immunosuppression to precision-targeted therapies for immune-mediated diseases, including systemic lupus erythematosus (SLE), psoriasis, and uveitis.&nbsp;
What You Will Do:&nbsp;

Lead Scientific Dialogues: Engage with top medical and scientific leaders through advanced scientific exchanges.&nbsp;
Cultivate Partnerships: Identify and establish connections with influential pre-clinical and clinical study investigators.&nbsp;
Deliver Strategic Insights: Provide strategic insights to enhance the application and value of our client&rsquo;s innovative treatments.&nbsp;
Enhance Research and Understanding: Address complex research questions and convey critical clinical and scientific information to enhance the usage and perception of products.&nbsp;

Who You Are:&nbsp;

Qualified Rheumatologist: Currently practicing with an active patient base in India and board-certified in rheumatology.&nbsp;
Experienced in Medical Affairs: At least 2 years of experience in Medical Affairs within the pharmaceutical industry, preferably with a focus on immunology.&nbsp;
Skilled Communicator: Able to effectively discuss complex scientific data with a diverse audience and contribute to clinical discussions on both regional and national levels.&nbsp;
Organized and Proactive: Known for excellent organizational, time management, and communication skills.&nbsp;
Ready to Travel: Prepared to travel frequently to meet with stakeholders and for reporting purposes (50-70% travel).&nbsp;

Why This Role?&nbsp;
This position offers a unique opportunity to apply your clinical expertise to influence global innovations in rheumatological treatments from your practice in India. Working through sense7ai as a conduit, your efforts will directly contribute to international advancements in healthcare, significantly impacting patient outcomes worldwide.&nbsp;
&nbsp;
Interested in making a global impact through local engagement? Apply now to become a driving force in the future of immunology treatments!


Jd Skills : Medical Affairs,Rheumatology





"""

jd = format_to_json(jd)

criteria = "Skills,Industry Specific Experience,Roles and Responsibilities,Domain Specific Experience,Experience,Certification,Technical Tools and Languages,Location Alignment,Soft Skills,Cultural Fit,Qualification,References and Recommendation"

criteria = format_to_json(criteria)
