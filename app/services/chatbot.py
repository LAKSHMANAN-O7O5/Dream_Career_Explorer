import json
import urllib.request
import urllib.error
from app.config import Config
from app.models import Career

def generate_chatbot_response(query, user_context=None):
    """
    Generates chatbot responses for career advice.
    If Gemini API Key is present, calls the Gemini API model.
    Otherwise, uses a robust keyword-matching local AI counsellor engine.
    """
    query_lower = query.lower().strip()
    
    # 1. Attempt Gemini API Integration if key is configured
    if Config.GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={Config.GEMINI_API_KEY}"
            
            # Formulate prompt including user profile context if available
            context_str = ""
            if user_context:
                context_str = f"Student Profile: Name: {user_context.get('name')}, Department: {user_context.get('dept')}, Qualification: {user_context.get('qual')}, Skills: {user_context.get('skills')}. "
                
            prompt = (
                f"You are an expert AI Career Counselor for the 'Dream Career Explorer' platform. "
                f"Provide concise, motivating, and actionable advice. {context_str}"
                f"User asked: {query}"
            )
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 400
                }
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=8) as response:
                res_body = json.loads(response.read().decode('utf-8'))
                text = res_body['candidates'][0]['content']['parts'][0]['text']
                return text
        except Exception as e:
            # Fallback to local rule engine on API exception
            pass

    # 2. Local AI Counselor rule-based matching engine
    # Load careers for search helper
    careers_list = []
    try:
        careers_list = Career.query.all()
    except:
        pass
        
    career_names = [c.title for c in careers_list] if careers_list else [
        "Software Engineer", "Data Analyst", "Data Scientist", "AI Engineer",
        "Cyber Security Analyst", "Cloud Engineer", "UI UX Designer", "Graphic Designer",
        "Business Analyst", "Digital Marketer", "Product Manager", "Teacher",
        "HR Manager", "Financial Analyst", "Full Stack Developer", "DevOps Engineer"
    ]

    # Check for direct career queries
    matched_career = None
    for name in career_names:
        if name.lower() in query_lower:
            matched_career = name
            break
            
    # Responses map
    if "hello" in query_lower or "hi" in query_lower or "hey" in query_lower:
        name_part = f" {user_context.get('name')}" if user_context and user_context.get('name') else ""
        return (
            f"Hello{name_part}! I am your AI Career Counsellor. "
            "How can I help you today? You can ask me about career compatibility, "
            "salaries, roadmaps, resume building, or specific job profiles like Software Engineer or UI/UX Designer!"
        )
        
    elif "salary" in query_lower or "pay" in query_lower or "package" in query_lower:
        if matched_career:
            # Find salary
            c_obj = next((c for c in careers_list if c.title.lower() == matched_career.lower()), None)
            if c_obj:
                return (
                    f"A **{matched_career}** has excellent compensation potential. "
                    f"In India, the average salary is **{c_obj.average_salary_in}** per year. "
                    f"Internationally, it averages around **{c_obj.average_salary_intl}** per year. "
                    f"The growth rate is estimated at **{c_obj.growth_rate}**."
                )
        return (
            "Salaries vary widely depending on the track! For instance, tech roles like Software Engineers, "
            "AI Engineers, and Data Scientists command ₹6,000,000 - ₹1,500,000 (INR) or $90,000 - $140,000 (USD) average packages. "
            "Management roles (Product Manager, Business Analyst) also scale very highly. Which specific role are you interested in?"
        )
        
    elif "roadmap" in query_lower or "step" in query_lower or "how to learn" in query_lower or "learn" in query_lower:
        if matched_career:
            return (
                f"To become a **{matched_career}**, follow this structured pathway:\n"
                "1. **Foundation Skills**: Master basic programming/concepts (e.g. Python, design logic).\n"
                "2. **Core Technologies**: Deep-dive into specific tools, frameworks, and databases.\n"
                "3. **Portfolio Projects**: Build 3+ projects showing end-to-end implementation.\n"
                "4. **Certifications**: Complete verified industry credentials.\n"
                "5. **Job Readiness**: Polish your resume, practice mock interviews, and apply.\n"
                "Visit our 'Learning Roadmap' tab for a step-by-step interactive checklist!"
            )
        return (
            "We provide custom stage-by-stage learning roadmaps for all 26 careers! "
            "Go to the 'Recommended Careers' on your dashboard, click 'Details' on a career, "
            "and navigate to the 'Roadmap' tab to track your step-by-step milestones."
        )

    elif "interview" in query_lower or "prep" in query_lower or "crack" in query_lower:
        tips = (
            "Here are core strategies to crack interviews:\n"
            "1. **Technical Prep**: Master fundamentals, data structures, or relevant domain tools.\n"
            "2. **Portfolio Validation**: Be ready to explain your projects using the STAR method (Situation, Task, Action, Result).\n"
            "3. **Soft Skills**: Practice communication, problem-solving reasoning out loud, and behavioral questions.\n"
            "4. **Mock Interviews**: Participate in mock interview sessions to reduce anxiety."
        )
        if matched_career:
            c_obj = next((c for c in careers_list if c.title.lower() == matched_career.lower()), None)
            if c_obj and c_obj.interview_tips:
                return f"For **{matched_career}** interviews:\n\n{c_obj.interview_tips}\n\n*General tips:*\n{tips}"
        return tips

    elif "resume" in query_lower or "cv" in query_lower:
        return (
            "Your resume must be ATS-friendly to clear screening filters. "
            "Include keywords from the job description, format as a clean single-column layout, "
            "avoid complex graphical elements, and state your achievements quantitatively (e.g., 'Improved database speed by 30%'). "
            "You can use our in-built **Resume Builder** to construct and print an ATS-ready resume instantly!"
        )

    elif "job" in query_lower or "readiness" in query_lower or "score" in query_lower:
        return (
            "Your **Job Readiness Score** tracks your progress across multiple dimensions: "
            "Verified Skills (30%), Projects (20%), Quiz Compatibility (15%), Certifications (15%), and Portfolio Profile (20%). "
            "Upload certificates, build projects, and link your GitHub in the portfolio editor to raise your score!"
        )
        
    elif matched_career:
        c_obj = next((c for c in careers_list if c.title.lower() == matched_career.lower()), None)
        if c_obj:
            return (
                f"**{c_obj.title}** is a great career pathway!\n\n"
                f"**Overview:** {c_obj.overview}\n\n"
                f"**Key Tools:** {c_obj.responsibilities[:200]}...\n\n"
                f"**Avg Salary (India):** {c_obj.average_salary_in}\n"
                f"**Avg Salary (Intl):** {c_obj.average_salary_intl}\n"
                f"Click on the career card in your dashboard to view complete guides, resources, and degrees!"
            )
            
    # General Default Answer
    return (
        "I'm here to guide you in your career journey! If you're wondering what career fits you best, "
        "I highly recommend completing the **Career Assessment Quiz** first. For specific answers, "
        "try asking about 'Software Engineer salary', 'Data Analyst roadmap', or how to improve your 'Job Readiness Score'."
    )
