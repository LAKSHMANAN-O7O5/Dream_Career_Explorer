import json
from app.models import Career, QuizQuestion, QuizOption, StudentSkill, User, QuizResult

def calculate_career_compatibility(user, answers, db_session):
    """
    Calculates compatibility scores (0-100%) for all careers based on:
    1. Quiz category weights (Personality, Technical, Creative, etc.)
    2. Answer options (direct weighted scores for careers)
    3. User academic background / department
    4. Student's existing skills compared to career requirements
    
    :param user: User model instance
    :param answers: Dict of {question_id: option_id}
    :param db_session: Active SQLAlchemy session
    :return: Tuple: (ranked_career_percentages, category_scores)
    """
    # 1. Initialize career scores dictionary
    careers = Career.query.all()
    if not careers:
        return {}, {}
        
    career_scores = {c.title: 0.0 for c in careers}
    max_possible_scores = {c.title: 1.0 for c in careers}  # Avoid division by zero
    
    # Category score buckets
    categories = [
        'personality', 'technical_interest', 'creativity', 'logical_thinking',
        'communication', 'leadership', 'business', 'problem_solving', 
        'mathematics', 'analytical_skills'
    ]
    category_scores = {cat: 0 for cat in categories}
    category_counts = {cat: 0 for cat in categories}

    # 2. Process Quiz Answers
    for q_id, opt_id in answers.items():
        print("=" * 50)
        print("ANSWERS:", answers)
        question = db_session.get(QuizQuestion, int(q_id))
        option = db_session.get(QuizOption, int(opt_id))
        
        if not question or not option:
            continue
            
        # Accumulate Category Scores
        cat = question.category
        weights = option.get_weights()  # JSON containing career scores
        print("Question:", question.question_text)
        print("Option:", option.option_text)
        print("Weights:", weights)
                
        # Each selected option carries a default score value based on the weights
        # We can extract the maximum weight for categorization
        opt_max_val = max(weights.values()) if weights else 3
        category_scores[cat] += opt_max_val
        category_counts[cat] += 1
        
        # Add weights to careers
                # Add weights to careers
        career_mapping = {
            "UI/UX Designer": "UX/UI Designer",
            "Full Stack Developer": "Software Engineer",
            "Backend Developer": "Software Engineer",
            "HR Specialist": "Business Analyst"
        }

        for career_title, weight in weights.items():

            mapped_title = career_mapping.get(career_title, career_title)

            if mapped_title in career_scores:
                career_scores[mapped_title] += float(weight)
                print("MATCH:", career_title, "→", mapped_title)
            else:
                print("NO MATCH:", career_title)
                
        # Keep track of max possible score to normalize later
        # We assume the max possible option weight for any career is 5 per question
        for c in careers:
            max_possible_scores[c.title] += 5.0

    # Normalize category scores (0-100 scale)
    for cat in categories:
        if category_counts[cat] > 0:
            category_scores[cat] = int((category_scores[cat] / (category_counts[cat] * 5)) * 100)
            category_scores[cat] = min(100, max(10, category_scores[cat]))
        else:
            category_scores[cat] = 50  # baseline

    # 3. Factor in Academic Background / Department
    dept = (user.department or "").strip().lower()
    qual = (user.qualification or "").strip().lower()
    
    dept_boosts = {
        "computer science": ["Software Engineer", "Full Stack Developer", "AI Engineer", "ML Engineer", "Data Scientist", "Cyber Security Analyst", "Cloud Engineer", "DevOps Engineer", "QA Engineer", "Mobile App Developer", "Game Developer", "Embedded Engineer", "Blockchain Developer", "Network Engineer", "Machine Learning Engineer"],
        "information technology": ["Software Engineer", "Full Stack Developer", "Cyber Security Analyst", "Cloud Engineer", "DevOps Engineer", "Network Engineer", "QA Engineer", "Mobile App Developer", "Game Developer", "Blockchain Developer"],
        "computer applications": ["Software Engineer", "Full Stack Developer", "Mobile App Developer", "QA Engineer", "UI UX Designer", "Web Developer"],
        "business": ["Product Manager", "Business Analyst", "HR Manager", "Financial Analyst", "Digital Marketer"],
        "management": ["Product Manager", "Business Analyst", "HR Manager", "Digital Marketer"],
        "commerce": ["Financial Analyst", "Business Analyst", "HR Manager"],
        "mechanical": ["Mechanical Engineer", "Embedded Engineer"],
        "civil": ["Civil Engineer"],
        "arts": ["UI UX Designer", "Graphic Designer", "Digital Marketer"],
        "design": ["UI UX Designer", "Graphic Designer"],
        "science": ["Teacher", "Professor", "Data Analyst", "Data Scientist"],
        "education": ["Teacher", "Professor"]
    }
    
    for key, boosted_careers in dept_boosts.items():
        if key in dept or key in qual:
            for c_title in boosted_careers:
                if c_title in career_scores:
                    career_scores[c_title] += 15.0 # Apply academic weight boost
                    max_possible_scores[c_title] += 15.0

    # 4. Factor in Current Skills Profile
    student_skills = StudentSkill.query.filter_by(user_id=user.id).all()
    student_skill_names = {s.skill_name.lower(): s.proficiency for s in student_skills}
    
    for c in careers:
        # Get required skills for this career
        req_skills = c.skills_required
        if not req_skills:
            continue
            
        skill_match_points = 0
        max_skill_points = 0
        
        for req in req_skills:
            req_name = req.skill_name.lower()
            importance = req.importance or 3
            max_skill_points += importance * 10
            
            if req_name in student_skill_names:
                # Add points weighted by importance and student's proficiency (1-100)
                skill_match_points += importance * (student_skill_names[req_name] / 10.0)
                
        if max_skill_points > 0:
            # We scale skill boost to a max of 20 points of total career compatibility
            skill_boost = (skill_match_points / max_skill_points) * 20.0
            career_scores[c.title] += skill_boost
            max_possible_scores[c.title] += 20.0

    # 5. Normalize Career Compatibility % (Scale 0-100%)
    career_percentages = {}
    for c in careers:
        raw_score = career_scores[c.title]
        max_score = max_possible_scores[c.title]
        # Calculate percentage
        pct = (raw_score / max_score) * 100.0
        # Add a baseline of 35% + randomized variance (scaled to look realistic) to represent general aptitudes
        print("Career:", c.title)
        print("Raw Score:", raw_score)
        print("Max Score:", max_score)
        print("Percentage:", pct)
        print("----------------")
        pct = int(min(98.0, max(30.0, pct)))
        career_percentages[str(c.id)] = pct

        # Sort results in descending compatibility percentage
        sorted_matches = dict(sorted(career_percentages.items(), key=lambda item: item[1], reverse=True))
    return sorted_matches, category_scores
