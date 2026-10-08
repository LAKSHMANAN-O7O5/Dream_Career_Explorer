import os
import json
from datetime import datetime, date
from app import create_app, db
from app.models import User, Career, CareerSkill, Course, Roadmap, QuizQuestion, QuizOption, Blog, Portfolio

def seed_database():
    app = create_app()
    with app.app_context():
        print("Recreating database tables...")
        db.create_all()
        QuizOption.query.delete()
        QuizQuestion.query.delete()
        db.session.commit()

        # 1. Seed Users if they don't exist
        if User.query.filter_by(username='admin').first() is None:
            print("Seeding admin account...")
            admin = User(
                username='admin',
                email='admin@dreamcareer.edu',
                full_name='System Admin',
                role='admin',
                department='Administration',
                qualification='PhD in CS'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        student_user = User.query.filter_by(username='student').first()
        if student_user is None:
            print("Seeding student account...")
            student_user = User(
                username='student',
                email='student@dreamcareer.edu',
                full_name='MRahima',
                role='student',
                department='Computer Science & Engineering',
                qualification='B.Tech'
            )
            student_user.set_password('student123')
            db.session.add(student_user)
            db.session.commit()
            
            # Initialise student portfolio
            pf = Portfolio(
                user_id=student_user.id,
                bio="Aspiring full-stack software engineer and final year student passionate about scalable web architectures, AI integration, and systems design.",
                github_profile="https://github.com/rahima",
                linkedin_profile="https://linkedin.com/in/rahima",
                website="https://rahima.dev",
                achievements="First Place at HackIndia 2025; Google Cloud Certified Associate Cloud Engineer."
            )
            db.session.add(pf)
            db.session.commit()

        # 2. Seed Careers if they don't exist
        if Career.query.count() == 0:
            print("Seeding 26 industry-level careers...")
            
            # Define 26 careers data
            careers_data = [
                {
                    "title": "Software Engineer",
                    "overview": "Design, build, and deploy robust web applications and backend services. Software engineers work on core business logic, scalability, and code maintainability.",
                    "responsibilities": "Develop modular code, collaborate with cross-functional product teams, write tests, and debug microservices.",
                    "average_salary_in": "₹800,000 - ₹2,500,000",
                    "average_salary_intl": "$95,000 - $160,000",
                    "growth_rate": "22%",
                    "future_scope": "Increasing dependency on cloud platforms and automated frameworks guarantees sustained high demand.",
                    "top_companies": "Google, Microsoft, Amazon, TCS, Infosys",
                    "required_certifications": "AWS Certified Developer; Microsoft Certified Azure Developer",
                    "required_degrees": "B.Tech (CS); Bachelor of Science (IT); MCA",
                    "interview_tips": "Review data structures, algorithms, system design patterns, and practice writing unit tests.",
                    "success_story": "Rahul transitioned from ECE to Software Engineering via open-source project contributions.",
                    "skills": [
                        ("Python", "technical", 5),
                        ("Data Structures", "technical", 5),
                        ("Git", "technical", 4),
                        ("Team Collaboration", "soft", 4)
                    ]
                },
                {
                    "title": "Data Scientist",
                    "overview": "Analyze complex datasets to discover patterns, train machine learning models, and provide mathematical trends to solve business problems.",
                    "responsibilities": "Train predictive models, clean unstructured datasets, build data visualizations, and present reports to leadership.",
                    "average_salary_in": "₹900,000 - ₹3,000,000",
                    "average_salary_intl": "$110,000 - $180,000",
                    "growth_rate": "35%",
                    "future_scope": "Big data analytics and AI scaling ensure massive requirements across healthcare, finance, and ecommerce.",
                    "top_companies": "IBM, Meta, Amazon, Accenture, Fractal Analytics",
                    "required_certifications": "Google Cloud Professional Data Engineer; IBM Data Science Certificate",
                    "required_degrees": "Bachelor of Science (Math/Stats); B.Tech (CS); M.Sc (Data Science)",
                    "interview_tips": "Focus on probability, linear algebra, SQL joins, machine learning algorithms, and explainability of models.",
                    "success_story": "Sneha mastered python and statistics, joining a top fintech firm as a Junior Data Scientist.",
                    "skills": [
                        ("Python", "technical", 5),
                        ("Machine Learning", "technical", 5),
                        ("SQL", "technical", 4),
                        ("Data Visualisation", "technical", 4)
                    ]
                },
                {
                    "title": "UX/UI Designer",
                    "overview": "Design user interfaces, layouts, and user journeys that are beautiful, intuitive, and highly functional.",
                    "responsibilities": "Create wireframes, build high-fidelity mockups, conduct user testing, and collaborate with frontend developers.",
                    "average_salary_in": "₹600,000 - ₹1,800,000",
                    "average_salary_intl": "$80,000 - $140,000",
                    "growth_rate": "18%",
                    "future_scope": "Design-centric engineering is crucial for modern applications, driving sustained demand for user experience researchers.",
                    "top_companies": "Google, Adobe, Flipkart, Uber, Zomato",
                    "required_certifications": "Google UX Design Certificate; Interaction Design Foundation Credentials",
                    "required_degrees": "Bachelor of Design; B.Sc (Animation); B.Tech (CS)",
                    "interview_tips": "Prepare a portfolio showing 3 detailed case studies tracking research, sketches, iterations, and final UI components.",
                    "success_story": "Rohit moved from Graphic Design to UI/UX, doubling his salary within 18 months.",
                    "skills": [
                        ("Figma", "technical", 5),
                        ("User Research", "technical", 4),
                        ("Wireframing", "technical", 5),
                        ("Empathy", "soft", 5)
                    ]
                },
                {
                    "title": "Product Manager",
                    "overview": "Define the vision, roadmap, and core features of a digital product, aligning engineering teams with business objectives.",
                    "responsibilities": "Write product specification sheets, coordinate sprint milestones, gather market research, and evaluate user feedback.",
                    "average_salary_in": "₹1,200,000 - ₹3,500,000",
                    "average_salary_intl": "$120,000 - $200,000",
                    "growth_rate": "24%",
                    "future_scope": "Crucial role across tech start-ups and multinational product firms to guide strategic product market fit.",
                    "top_companies": "Microsoft, Amazon, Paytm, PhonePe, Jio",
                    "required_certifications": "Product School Certificate; Agile Product Owner (CSPO)",
                    "required_degrees": "MBA; B.Tech; BBA",
                    "interview_tips": "Practice product estimation questions, product case study analysis, and behavioral conflict management styles.",
                    "success_story": "Divya transitioned from software engineer to PM by taking charge of release documentation.",
                    "skills": [
                        ("Product Strategy", "technical", 5),
                        ("Agile Methods", "technical", 4),
                        ("Communication", "soft", 5),
                        ("User Analytics", "technical", 4)
                    ]
                },
                {
                    "title": "Cloud Solutions Architect",
                    "overview": "Design, plan, and deploy resilient and cost-effective cloud systems using AWS, Google Cloud, or Azure.",
                    "responsibilities": "Optimize cloud configurations, design containerized orchestrations, migration of data centers, and monitor service availability.",
                    "average_salary_in": "₹1,400,000 - ₹4,000,000",
                    "average_salary_intl": "$130,000 - $210,000",
                    "growth_rate": "28%",
                    "future_scope": "Enterprise migrations to multi-cloud architectures command elite certifications and design engineers.",
                    "top_companies": "Amazon Web Services, Microsoft, IBM, Wipro, HCL",
                    "required_certifications": "AWS Certified Solutions Architect - Professional; GCP Cloud Architect",
                    "required_degrees": "B.Tech (CS/IT); BCA; Master of Science",
                    "interview_tips": "Focus on high-availability concepts, disaster recovery, cloud costing parameters, and subnet networking rules.",
                    "success_story": "Vijay earned his AWS Solutions Architect certification during college and landed an associate architect job.",
                    "skills": [
                        ("AWS", "technical", 5),
                        ("Cloud Security", "technical", 5),
                        ("Networking", "technical", 4),
                        ("System Architecture", "technical", 5)
                    ]
                },
                {
                    "title": "DevOps Engineer",
                    "overview": "Bridge development and IT operations to automate software delivery pipelines, monitoring, and cloud infrastructure scaling.",
                    "responsibilities": "Construct CI/CD pipelines, configure Terraform infrastructure, manage Kubernetes containers, and automate backups.",
                    "average_salary_in": "₹1,000,000 - ₹3,000,000",
                    "average_salary_intl": "$115,000 - $185,000",
                    "growth_rate": "26%",
                    "future_scope": "Continuous integration and rapid cloud-based microservices development require robust automation tooling.",
                    "top_companies": "Red Hat, Oracle, TCS, Dell, Cognizant",
                    "required_certifications": "Docker Certified Associate; Kubernetes Administrator (CKA)",
                    "required_degrees": "B.Tech; B.Sc (IT); MCA",
                    "interview_tips": "Demonstrate expertise in Bash scripting, Docker containers, Kubernetes, Jenkins pipelines, and Git workflows.",
                    "success_story": "Manish automated manual deployment tasks at his internship, securing a full-time DevOps role.",
                    "skills": [
                        ("Docker", "technical", 5),
                        ("Kubernetes", "technical", 5),
                        ("CI/CD", "technical", 5),
                        ("Linux Administration", "technical", 4)
                    ]
                },
                {
                    "title": "Cybersecurity Analyst",
                    "overview": "Protect organization networks, databases, and servers from breaches, malwares, and unauthorized access.",
                    "responsibilities": "Monitor system access, perform vulnerability checks, write security patches, and audit protocol compliance.",
                    "average_salary_in": "₹800,000 - ₹2,200,000",
                    "average_salary_intl": "$98,000 - $165,000",
                    "growth_rate": "31%",
                    "future_scope": "Global rise in cyberattacks and data privacy regulations mandates robust corporate cybersecurity setups.",
                    "top_companies": "Cisco, Palo Alto Networks, Deloitte, EY, PwC",
                    "required_certifications": "CompTIA Security+; Certified Ethical Hacker (CEH)",
                    "required_degrees": "B.Tech; B.Sc; Cyber Law Certifications",
                    "interview_tips": "Practice diagnosing network packet captures, explain SSL handshake, and standard cryptographic algorithms.",
                    "success_story": "Amit identified a critical security vulnerability in a college app, paving his path into threat intelligence.",
                    "skills": [
                        ("Network Security", "technical", 5),
                        ("Ethical Hacking", "technical", 4),
                        ("Linux", "technical", 4),
                        ("Analytical Thinking", "soft", 5)
                    ]
                },
                {
                    "title": "AI / Machine Learning Engineer",
                    "overview": "Research, design, build, and deploy AI models, deep learning frameworks, and Natural Language Processing pipelines.",
                    "responsibilities": "Design neural networks, optimize model training parameters, clean raw inputs, and deploy models as scalable API endpoints.",
                    "average_salary_in": "₹1,200,000 - ₹3,800,000",
                    "average_salary_intl": "$125,000 - $220,000",
                    "growth_rate": "40%",
                    "future_scope": "Generative AI, Large Language Models (LLMs), and autonomous systems drive exponential career creation.",
                    "top_companies": "OpenAI, Google DeepMind, NVIDIA, Amazon, Adobe",
                    "required_certifications": "TensorFlow Developer Certificate; AWS Machine Learning Specialty",
                    "required_degrees": "B.Tech; M.Tech (AI/ML); PhD in Computer Science",
                    "interview_tips": "Expect derivations of gradient descent, neural network architecture design, and system deployment details.",
                    "success_story": "Priya published a paper on computer vision during her B.Tech, landing a research engineer role at Nvidia.",
                    "skills": [
                        ("Python", "technical", 5),
                        ("Deep Learning", "technical", 5),
                        ("TensorFlow", "technical", 5),
                        ("Mathematics", "technical", 4)
                    ]
                },
                {
                    "title": "Blockchain Developer",
                    "overview": "Develop decentralized applications, configure smart contracts, and build cryptography architectures.",
                    "responsibilities": "Write Ethereum Solidity contracts, manage consensus algorithms, secure coin operations, and deploy decentralized dApps.",
                    "average_salary_in": "₹1,000,000 - ₹3,200,000",
                    "average_salary_intl": "$120,000 - $190,000",
                    "growth_rate": "25%",
                    "future_scope": "Decentralization protocols, digital currencies, and distributed ledger systems require advanced cryptography developers.",
                    "top_companies": "ConsenSys, Polygon, Coinbase, IBM, Wipro",
                    "required_certifications": "Ethereum Developer Certification; Certified Blockchain Developer",
                    "required_degrees": "B.Tech (CS); Bachelor of Science (IT)",
                    "interview_tips": "Understand Ethereum Virtual Machine (EVM), gas optimization, smart contract security vulnerabilities, and consensus.",
                    "success_story": "Vikram won a blockchain hackathon and transitioned to writing smart contracts professionally.",
                    "skills": [
                        ("Solidity", "technical", 5),
                        ("Cryptography", "technical", 5),
                        ("JavaScript", "technical", 4),
                        ("Smart Contracts", "technical", 5)
                    ]
                },
                {
                    "title": "Data Engineer",
                    "overview": "Build robust data pipelines, architecture, and ETL systems to aggregate big data databases for analytics pipelines.",
                    "responsibilities": "Write SQL pipelines, orchestrate workflows via Airflow, configure Spark clusters, and database schemas setups.",
                    "average_salary_in": "₹900,000 - ₹2,800,000",
                    "average_salary_intl": "$110,000 - $175,000",
                    "growth_rate": "30%",
                    "future_scope": "Efficient big data warehousing is essential to enable analytical reporting and predictive modeling.",
                    "top_companies": "Meta, Snowflake, Amazon, Cognizant, Infosys",
                    "required_certifications": "Google Professional Data Engineer; Databricks Certified Associate",
                    "required_degrees": "B.Tech; MCA; M.Sc (CS/IT)",
                    "interview_tips": "Master SQL window functions, explain Spark execution plans, database partitioning, and indexes design.",
                    "success_story": "Ramesh transitioned from DBA to Data Engineer by learning Apache Spark and Airflow.",
                    "skills": [
                        ("SQL", "technical", 5),
                        ("Apache Spark", "technical", 5),
                        ("ETL Pipelines", "technical", 5),
                        ("Python", "technical", 4)
                    ]
                },
                {
                    "title": "Mobile App Developer",
                    "overview": "Create high-performance native and cross-platform application layouts for iOS and Android smartphones.",
                    "responsibilities": "Develop iOS Swift or Flutter app layouts, connect to restful APIs, monitor crash analytics, and launch on stores.",
                    "average_salary_in": "₹700,000 - ₹2,200,000",
                    "average_salary_intl": "$90,000 - $155,000",
                    "growth_rate": "20%",
                    "future_scope": "Ubiquitous smartphone operations mandate intuitive and secure corporate mobile platforms.",
                    "top_companies": "Flipkart, Paytm, Swiggy, Accenture, Tech Mahindra",
                    "required_certifications": "Google Associate Android Developer; Apple iOS Development Tutorials",
                    "required_degrees": "B.Tech (CS); BCA; B.Sc (IT)",
                    "interview_tips": "Explain UI threading models, restful connection, memory leaks diagnostics, and state management solutions.",
                    "success_story": "Harini built a personal finance app that got 50,000 downloads, getting hired immediately.",
                    "skills": [
                        ("Flutter", "technical", 5),
                        ("Swift", "technical", 5),
                        ("API Integration", "technical", 4),
                        ("Problem Solving", "soft", 4)
                    ]
                },
                {
                    "title": "Full Stack Developer",
                    "overview": "Build both consumer-facing layouts and underlying database services, handling the entire application stack.",
                    "responsibilities": "Design UI screens via React, construct backend APIs, write database migrations, and deploy applications.",
                    "average_salary_in": "₹800,000 - ₹2,600,000",
                    "average_salary_intl": "$100,000 - $165,000",
                    "growth_rate": "24%",
                    "future_scope": "Versatile developers who handle database work and UI are highly valued by agile tech companies.",
                    "top_companies": "Amazon, Paytm, TCS, Infosys, Capgemini",
                    "required_certifications": "Meta Full Stack Developer Professional Certificate",
                    "required_degrees": "B.Tech; MCA; BCA",
                    "interview_tips": "Focus on API architectures, SQL vs. NoSQL database designs, React Hooks, and CSS frameworks.",
                    "success_story": "Kiran built an open-source project matching students to study groups, and got recruited.",
                    "skills": [
                        ("JavaScript", "technical", 5),
                        ("Python", "technical", 4),
                        ("SQL", "technical", 4),
                        ("React", "technical", 5)
                    ]
                },
                {
                    "title": "Embedded Systems Engineer",
                    "overview": "Write low-level code for microcontrollers and embedded processors powering hardware devices.",
                    "responsibilities": "Write C/C++ firmware, interface with physical sensors, write hardware drivers, and debug electronic chips.",
                    "average_salary_in": "₹700,000 - ₹2,000,000",
                    "average_salary_intl": "$95,000 - $150,000",
                    "growth_rate": "15%",
                    "future_scope": "IoT (Internet of Things) expansion and electric vehicles engineering drive demand for low-level software engineers.",
                    "top_companies": "Intel, Bosch, Qualcomm, Samsung, Tata Motors",
                    "required_certifications": "ARM Certified Engineer; Embedded Systems Associate",
                    "required_degrees": "B.Tech (ECE/EEE); M.Tech (Embedded Systems)",
                    "interview_tips": "Review microcontrollers registers, pointer manipulation in C, real-time operating systems (RTOS), and oscilloscope usage.",
                    "success_story": "Anil built a customized smart home automation hub using Raspberry Pi, getting hired at Bosch.",
                    "skills": [
                        ("C Programming", "technical", 5),
                        ("Microcontrollers", "technical", 5),
                        ("RTOS", "technical", 4),
                        ("Hardware Interfacing", "technical", 4)
                    ]
                },
                {
                    "title": "QA Automation Engineer",
                    "overview": "Build automated script pipelines to test software quality, security, performance, and functionality.",
                    "responsibilities": "Write Selenium/Playwright script pipelines, perform load tests, write test plans, and verify bugs.",
                    "average_salary_in": "₹600,000 - ₹1,800,000",
                    "average_salary_intl": "$85,000 - $135,000",
                    "growth_rate": "16%",
                    "future_scope": "Rapid agile release cycles necessitate deep automation of quality assurance testing models.",
                    "top_companies": "Cognizant, Wipro, Oracle, IBM, Infosys",
                    "required_certifications": "ISTQB Certified Tester; Selenium Certified Specialist",
                    "required_degrees": "B.Tech (CS/IT); BCA; MCA",
                    "interview_tips": "Practice writing selectors, explain Page Object Model design, API testing steps, and load testing configurations.",
                    "success_story": "Pooja transitioned from manual testing to automation, automating tests for an ERP cloud product.",
                    "skills": [
                        ("Selenium", "technical", 5),
                        ("Python", "technical", 4),
                        ("Test Automation", "technical", 5),
                        ("Analytical Skills", "soft", 4)
                    ]
                },
                {
                    "title": "Technical Writer",
                    "overview": "Author technical documentation, user guides, API manuals, and whitepapers describing complex architectures.",
                    "responsibilities": "Write developer API references, compose software guides, structure support knowledge bases, and review layouts.",
                    "average_salary_in": "₹500,000 - ₹1,500,000",
                    "average_salary_intl": "$75,000 - $120,000",
                    "growth_rate": "12%",
                    "future_scope": "Explosion of open-source frameworks and API products highlights documentation as a developer utility.",
                    "top_companies": "Google, Oracle, Red Hat, Siemens, Tech Mahindra",
                    "required_certifications": "Technical Writing Certificate; Agile Project Management",
                    "required_degrees": "Bachelor of Arts (English/Comm); B.Tech (CS); B.Sc",
                    "interview_tips": "Provide 3 writing samples explaining a complex script or API operation to a beginner audience.",
                    "success_story": "Arjun combined his English major with code hobby, joining Google as a Technical Writer.",
                    "skills": [
                        ("Technical Writing", "technical", 5),
                        ("Markdown", "technical", 4),
                        ("Git", "technical", 3),
                        ("Communication", "soft", 5)
                    ]
                },
                {
                    "title": "IT Consultant",
                    "overview": "Advise enterprise organizations on the integration of software architectures, systems upgrades, and IT strategies.",
                    "responsibilities": "Audit corporate workflows, draft system migrations proposals, organize software vendors, and manage client stakeholders.",
                    "average_salary_in": "₹900,000 - ₹2,500,000",
                    "average_salary_intl": "$105,000 - $170,000",
                    "growth_rate": "18%",
                    "future_scope": "Rapid digitization of traditional businesses requires seasoned advisory architects and engineers.",
                    "top_companies": "Deloitte, Accenture, Capgemini, EY, McKinsey",
                    "required_certifications": "ITIL Foundation; PMP Project Manager Professional",
                    "required_degrees": "B.Tech; MBA; BBA",
                    "interview_tips": "Prepare business case analysis scenarios, market estimation, and stakeholder communication case studies.",
                    "success_story": "Rajesh helped a family manufacturing company migrate to Cloud ERP, landing a consultant job at EY.",
                    "skills": [
                        ("Business Strategy", "technical", 4),
                        ("Project Management", "technical", 4),
                        ("Communication", "soft", 5),
                        ("Requirements Analysis", "technical", 5)
                    ]
                },
                {
                    "title": "Network Engineer",
                    "overview": "Design, setup, maintain, and secure the physical and virtual computer networks of an organization.",
                    "responsibilities": "Configure Cisco routers, design subnet architectures, manage firewalls, and audit package transfers.",
                    "average_salary_in": "₹600,000 - ₹1,800,000",
                    "average_salary_intl": "$85,000 - $140,000",
                    "growth_rate": "12%",
                    "future_scope": "Modern hardware and virtual network infrastructures depend heavily on network engineers for network security.",
                    "top_companies": "Cisco, Juniper Networks, HCL, Airtel, Jio",
                    "required_certifications": "Cisco Certified Network Associate (CCNA); CCNP Enterprise",
                    "required_degrees": "B.Tech (ECE/EE); B.Sc (Computer Science)",
                    "interview_tips": "Explain TCP/IP model layers, subnet masking computations, routing protocols, and DNS resolutions.",
                    "success_story": "Kunal configured routing setups in his college lab, helping him clear his CCNA exams.",
                    "skills": [
                        ("Networking", "technical", 5),
                        ("Cisco Routing", "technical", 5),
                        ("Network Security", "technical", 4),
                        ("Problem Solving", "soft", 4)
                    ]
                },
                {
                    "title": "Salesforce Administrator",
                    "overview": "Configure, manage, and optimize Salesforce CRM setups to streamline sales operations and marketing campaigns.",
                    "responsibilities": "Define CRM profiles, write automation workflows, build analytics dashboards, and manage integrations.",
                    "average_salary_in": "₹600,000 - ₹1,600,000",
                    "average_salary_intl": "$80,000 - $130,000",
                    "growth_rate": "15%",
                    "future_scope": "Salesforce remains the top cloud CRM platform worldwide, driving consistent support requirements.",
                    "top_companies": "Accenture, Salesforce, Wipro, Tech Mahindra, Cognizant",
                    "required_certifications": "Salesforce Certified Administrator; Platform App Builder",
                    "required_degrees": "BBA; BCA; B.Tech",
                    "interview_tips": "Demonstrate knowledge of permission sets, sharing rules, flows builder, and custom objects configuration.",
                    "success_story": "Tanya completed Salesforce trailhead badges in college, landing a job as CRM Administrator.",
                    "skills": [
                        ("Salesforce CRM", "technical", 5),
                        ("Data Management", "technical", 4),
                        ("Agile Methods", "technical", 3),
                        ("Problem Solving", "soft", 4)
                    ]
                },
                {
                    "title": "Game Developer",
                    "overview": "Write interactive graphics code, gameplay logic, physics modeling, and multiplayer configurations for console/mobile games.",
                    "responsibilities": "Develop graphics logic in Unity or Unreal, write C# / C++ code, configure textures, and optimize memory layouts.",
                    "average_salary_in": "₹700,000 - ₹2,400,000",
                    "average_salary_intl": "$90,000 - $160,000",
                    "growth_rate": "22%",
                    "future_scope": "Interactive visual entertainment, mobile gaming, and VR integrations generate billions of dollars in software demand.",
                    "top_companies": "Ubisoft, EA Games, Rockstar Games, Zynga, Rockstar India",
                    "required_certifications": "Unity Certified Developer; Unreal Engine Design Credentials",
                    "required_degrees": "B.Tech (CS); B.Sc (Animation & Game Design)",
                    "interview_tips": "Focus on 3D vector math, physics calculations, memory constraints in consoles, and C# programming syntax.",
                    "success_story": "Siddharth built 3 indie mobile games using Unity, landing an engineering role at Ubisoft.",
                    "skills": [
                        ("Unity", "technical", 5),
                        ("C# Programming", "technical", 5),
                        ("Vector Math", "technical", 4),
                        ("Creativity", "soft", 5)
                    ]
                },
                {
                    "title": "Digital Marketing Specialist",
                    "overview": "Plan, execute, and analyze search engine optimization (SEO), social campaigns, and performance marketing pipelines.",
                    "responsibilities": "Optimize website SEO, run Google ads campaigns, analyze traffic logs, and coordinate content layout.",
                    "average_salary_in": "₹500,000 - ₹1,500,000",
                    "average_salary_intl": "$70,000 - $120,000",
                    "growth_rate": "14%",
                    "future_scope": "Sustained ecommerce and online branding require analytics-driven marketing campaigns.",
                    "top_companies": "Flipkart, Amazon, GroupM, dentsu, Dentsu India",
                    "required_certifications": "Google Ads Certification; HubSpot Inbound Marketing Certification",
                    "required_degrees": "BBA; MBA (Marketing); B.Sc",
                    "interview_tips": "Present campaign audit case studies, explain CPC, CAC, and conversion rate calculations.",
                    "success_story": "Nisha grew a college club Instagram account by 400%, converting that into a specialist role.",
                    "skills": [
                        ("SEO", "technical", 5),
                        ("Google Ads", "technical", 5),
                        ("Data Visualisation", "technical", 3),
                        ("Communication", "soft", 5)
                    ]
                },
                {
                    "title": "Business Analyst",
                    "overview": "Analyze corporate datasets, document product requirements, and recommend data-driven operational upgrades.",
                    "responsibilities": "Perform stakeholder interviews, compose UML process flows, query databases via SQL, and build PowerBI charts.",
                    "average_salary_in": "₹700,000 - ₹1,800,000",
                    "average_salary_intl": "$85,000 - $140,000",
                    "growth_rate": "16%",
                    "future_scope": "Critical link bridging engineering structures with commercial operations across large companies.",
                    "top_companies": "EY, Deloitte, Paytm, HCL, Wipro",
                    "required_certifications": "Certified Business Analysis Professional (CBAP)",
                    "required_degrees": "B.Tech; MBA; B.Sc (Economics/Finance)",
                    "interview_tips": "Demonstrate knowledge of writing clear SRS documentation, SQL joins, and case analysis estimation.",
                    "success_story": "Aarav leveraged his engineering coding logic and Excel analysis skills, entering EY as a Business Analyst.",
                    "skills": [
                        ("SQL", "technical", 4),
                        ("Data Visualisation", "technical", 4),
                        ("Requirements Analysis", "technical", 5),
                        ("Analytical Thinking", "soft", 5)
                    ]
                },
                {
                    "title": "HR Analytics Specialist",
                    "overview": "Analyze student and staff metrics to optimize recruiting pipeline velocity and retention metrics.",
                    "responsibilities": "Clean onboarding datasets, evaluate performance indicators, configure HR databases, and design reports.",
                    "average_salary_in": "₹600,000 - ₹1,500,000",
                    "average_salary_intl": "$80,000 - $130,000",
                    "growth_rate": "11%",
                    "future_scope": "Modern corporate organizations depend heavily on metrics-driven talent acquisition models.",
                    "top_companies": "Accenture, TCS, Cognizant, Wipro, EY",
                    "required_certifications": "HR Analytics Certificate; SAP SuccessFactors Certified",
                    "required_degrees": "MBA (HR); BBA; B.Sc (Stats)",
                    "interview_tips": "Understand attrition rates formulas, employee satisfaction indices, and standard analytics tools.",
                    "success_story": "Pooja specialized in HR data dashboard analytics, getting hired at Accenture.",
                    "skills": [
                        ("Data Visualisation", "technical", 4),
                        ("SQL", "technical", 3),
                        ("Agile Methods", "technical", 2),
                        ("Communication", "soft", 5)
                    ]
                },
                {
                    "title": "High School Computer Science Teacher",
                    "overview": "Teach students baseline computational theory, programming logic (Python, Java), and basic databases.",
                    "responsibilities": "Create lesson curriculums, organize software labs sessions, grade programming assignments, and organize coding contests.",
                    "average_salary_in": "₹400,000 - ₹1,000,000",
                    "average_salary_intl": "$60,000 - $95,000",
                    "growth_rate": "8%",
                    "future_scope": "Global rise in computational curricula mandates skilled instructors capable of training baseline algorithms.",
                    "top_companies": "Kendriya Vidyalaya, DAV Schools, Delhi Public School",
                    "required_certifications": "B.Ed (Bachelor of Education); CTET (Central Teacher Eligibility Test)",
                    "required_degrees": "B.Sc (CS); B.Ed; MCA; B.Tech (CS)",
                    "interview_tips": "Present a demo lesson explaining concepts like loops or variables to high school students.",
                    "success_story": "Manoj transitioned from IT support to teaching, guiding his students to build robotics code.",
                    "skills": [
                        ("Python", "technical", 4),
                        ("C Programming", "technical", 3),
                        ("Communication", "soft", 5),
                        ("Empathy", "soft", 5)
                    ]
                },
                {
                    "title": "Database Administrator (DBA)",
                    "overview": "Coordinate security access, indexes, backups, and structural health of database engines.",
                    "responsibilities": "Optimize slow queries, manage database privileges, restore backup points, and structure database replication.",
                    "average_salary_in": "₹700,000 - ₹1,800,000",
                    "average_salary_intl": "$90,000 - $145,000",
                    "growth_rate": "10%",
                    "future_scope": "Ensuring secure, high-uptime operations of transaction databases is a mission-critical utility for banks and IT hubs.",
                    "top_companies": "Oracle, IBM, Tech Mahindra, Infosys, Wipro",
                    "required_certifications": "Oracle Database Administrator Certified Associate; Microsoft SQL Server Cert",
                    "required_degrees": "B.Tech (CS/IT); BCA; MCA",
                    "interview_tips": "Practice diagnosing deadlock issues, index configurations, query execution plans, and clustering.",
                    "success_story": "Rohan optimized slow query response times at a regional bank, securing a Lead DBA position.",
                    "skills": [
                        ("SQL", "technical", 5),
                        ("Database Management", "technical", 5),
                        ("Linux Administration", "technical", 4),
                        ("Problem Solving", "soft", 4)
                    ]
                },
                {
                    "title": "Systems Administrator",
                    "overview": "Manage physical/virtual server configurations, security protocols, user permissions, and networks.",
                    "responsibilities": "Install security patches, configure virtual machines (VMs), manage active directory logs, and monitor server health.",
                    "average_salary_in": "₹600,000 - ₹1,500,000",
                    "average_salary_intl": "$80,000 - $135,000",
                    "growth_rate": "9%",
                    "future_scope": "Sustained corporate infrastructure requires sysadmins capable of managing modern hybrid configurations.",
                    "top_companies": "HCL, Wipro, TCS, HP, Lenovo",
                    "required_certifications": "Red Hat Certified System Administrator (RHCSA); Microsoft Windows Server Cert",
                    "required_degrees": "B.Sc (IT); B.Tech (ECE/CS); Diploma in Computer Science",
                    "interview_tips": "Focus on Bash scripting, active directory configurations, file permission structures, and firewall troubleshooting.",
                    "success_story": "Preeti setup secure servers for a local clinic, earning her RHCSA and landing an HCL role.",
                    "skills": [
                        ("Linux Administration", "technical", 5),
                        ("Networking", "technical", 4),
                        ("Cloud Security", "technical", 4),
                        ("Problem Solving", "soft", 4)
                    ]
                },
                {
                    "title": "Hardware Design Engineer",
                    "overview": "Design, prototype, and test electronic layouts, circuit boards, and silicon microchip systems.",
                    "responsibilities": "Draw circuit schemas, model thermal limits, write VHDL/Verilog simulations, and evaluate chip prototypes.",
                    "average_salary_in": "₹800,000 - ₹2,400,000",
                    "average_salary_intl": "$100,000 - $170,000",
                    "growth_rate": "14%",
                    "future_scope": "Semiconductor manufacturing expansions and AI silicon development spark elite opportunities.",
                    "top_companies": "Intel, AMD, Qualcomm, NVIDIA, Texas Instruments",
                    "required_certifications": "VLSI Design Certificate; PCB Layout Professional Credentials",
                    "required_degrees": "B.Tech (ECE/EEE); M.Tech (VLSI Design/Micro-electronics)",
                    "interview_tips": "Explain digital design logic, setups/hold times parameters, PCB noise optimization, and Verilog coding.",
                    "success_story": "Vikram designed a low-power digital filter chip for his M.Tech project, getting hired at Qualcomm.",
                    "skills": [
                        ("VHDL", "technical", 5),
                        ("Microcontrollers", "technical", 4),
                        ("System Architecture", "technical", 4),
                        ("Mathematics", "technical", 4)
                    ]
                }
            ]
            
            # Create Careers
            for c_data in careers_data:
                # Mock projects JSON structure
                projs = [
                    {"title": f"Capstone: Build a {c_data['title']} Platform", "description": "Construct an end-to-end framework applying standard design patterns, API integrations, and robust database layers."},
                    {"title": f"Simulation: {c_data['title']} Case Study", "description": "Conduct analytical profiling and research targeting scalability constraints and write optimization recommendations."}
                ]
                
                new_career = Career(
                    title=c_data["title"],
                    overview=c_data["overview"],
                    responsibilities=c_data["responsibilities"],
                    average_salary_in=c_data["average_salary_in"],
                    average_salary_intl=c_data["average_salary_intl"],
                    growth_rate=c_data["growth_rate"],
                    future_scope=c_data["future_scope"],
                    top_companies=c_data["top_companies"],
                    required_certifications=c_data["required_certifications"],
                    required_degrees=c_data["required_degrees"],
                    portfolio_projects=json.dumps(projs),
                    interview_tips=c_data["interview_tips"],
                    success_story=c_data["success_story"]
                )
                db.session.add(new_career)
                db.session.commit() # Save to database to get career.id
                
                # Seed Career Skills
                for sk_name, sk_type, imp in c_data["skills"]:
                    c_skill = CareerSkill(
                        career_id=new_career.id,
                        skill_name=sk_name,
                        skill_type=sk_type,
                        importance=imp
                    )
                    db.session.add(c_skill)
                
                # Seed 5 Roadmap Stages
                stages = [
                    ("Beginner Phase", "Learn fundamentals, language syntax, database queries, and basic software conventions.", "Master basic loops and simple algorithms."),
                    ("Core Foundation", "Understand architecture structures, MVC design patterns, API integration rules, and data structures.", "Construct 3 small baseline programs."),
                    ("Intermediate Project", "Build an end-to-end functional application integrating databases, testing, and authentication features.", "Deploy your project live on hosting providers."),
                    ("Professional Certification", "Prepare for industry-standard certification exams to validate domain expertise to recruiters.", "Register AWS/Google/Cisco study materials."),
                    ("Interview Readiness", "Practice mock coding assessments, system design interviews, and behavioral STAR models.", "Mock interview questions with peers or bots.")
                ]
                for order, (stg_name, stg_desc, stg_res) in enumerate(stages, 1):
                    stage_record = Roadmap(
                        career_id=new_career.id,
                        stage_order=order,
                        stage_name=stg_name,
                        description=stg_desc,
                        recommended_resources=stg_res
                    )
                    db.session.add(stage_record)
                
                # Seed 3 Course recommendation
                # Seed 3 Course recommendations
                search = c_data['title'].replace(" ", "+")

                courses = [
                    (
                        f"Introduction to {c_data['title']} Fundamentals",
                        "free_course",
                        "beginner",
                        f"https://www.coursera.org/search?query={search}",
                        "Coursera"
                    ),
                    (
                        f"{c_data['title']} Masterclass Suite",
                        "paid_course",
                        "intermediate",
                        f"https://www.udemy.com/courses/search/?q={search}",
                        "Udemy"
                    ),
                    (
                        f"Complete {c_data['title']} Crash Course",
                        "youtube_tutorial",
                        "beginner",
                        f"https://www.youtube.com/results?search_query={search}",
                        "YouTube"
                    ),
                    (
    f"{c_data['title']} Practice Platform",
    "coding_platform",
    "intermediate",
    "https://leetcode.com/",
    "LeetCode"
),

(
    f"{c_data['title']} Official Documentation",
    "documentation",
    "beginner",
    "https://developer.mozilla.org/",
    "MDN Docs"
),

(
    f"{c_data['title']} Reference Book",
    "book",
    "beginner",
    f"https://www.amazon.in/s?k={search}",
    "Amazon Books"
)
                ]
                
                for title, cat, level, link, plat in courses:
                    c_record = Course(
                        career_id=new_career.id,
                        title=title,
                        category=cat,
                        level=level,
                        link=link,
                        platform_name=plat
                    )
                    db.session.add(c_record)
            
            db.session.commit()
            print("Successfully seeded 26 careers, skills, roadmaps, and courses!")

        # 3. Seed 45 Quiz Questions if empty
        if QuizQuestion.query.count() == 0:
            print("Seeding 45 quiz questions and options...")
            
            # Categories mapping
            categories = [
                'personality', 'technical_interest', 'creativity', 'logical_thinking', 
                'communication', 'leadership', 'business', 'problem_solving', 
                'mathematics', 'analytical_skills'
            ]
            
            # Fetch career ids for option weights mapping
            all_careers = Career.query.all()
            c_names = [c.title for c in all_careers]
            
            # Simple helper to build weights maps based on index
            def make_weights(c1, c2, c3):
                res = {}
                if c1 in c_names: res[c1] = 4
                if c2 in c_names: res[c2] = 3
                if c3 in c_names: res[c3] = 2
                return json.dumps(res)

            # Generate 45 questions
            if QuizQuestion.query.count() == 0:
                print("Seeding 45 quiz questions and options...")
                # Question 1
                q1 = QuizQuestion(question_text="What kind of work excites you most?", category="personality")
                db.session.add(q1)
                db.session.flush()
                db.session.add(QuizOption(question_id=q1.id, option_text="Building software products", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q1.id, option_text="Designing user interfaces", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q1.id, option_text="Analyzing data and patterns", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q1.id, option_text="Helping and coordinating people", score_value=json.dumps({"HR Specialist": 4, "Business Analyst": 3})))

        

                # Question 2
                q2 = QuizQuestion(question_text="Which activity do you enjoy the most?", category="personality")
                db.session.add(q2)
                db.session.flush()
                db.session.add(QuizOption(question_id=q2.id, option_text="Writing code", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 4})))
                db.session.add(QuizOption(question_id=q2.id, option_text="Creating visuals", score_value=json.dumps({"Graphic Designer": 4, "UI/UX Designer": 4})))
                db.session.add(QuizOption(question_id=q2.id, option_text="Solving math problems", score_value=json.dumps({"Data Scientist": 4, "ML Engineer": 3})))
                db.session.add(QuizOption(question_id=q2.id, option_text="Talking to people", score_value=json.dumps({"HR Specialist": 4, "Sales Executive": 3})))

                # Question 3
                q3 = QuizQuestion(question_text="When you get a new task, what do you prefer?", category="personality")
                db.session.add(q3)
                db.session.flush()
                db.session.add(QuizOption(question_id=q3.id, option_text="Start building immediately", score_value=json.dumps({"Full Stack Developer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q3.id, option_text="Plan the user journey first", score_value=json.dumps({"UI/UX Designer": 4, "Product Manager": 4})))
                db.session.add(QuizOption(question_id=q3.id, option_text="Study the data first", score_value=json.dumps({"Data Analyst": 4, "Data Scientist": 3})))
                db.session.add(QuizOption(question_id=q3.id, option_text="Discuss it with the team", score_value=json.dumps({"Team Lead": 4, "HR Specialist": 4})))

                # Question 4
                q4 = QuizQuestion(question_text="Which type of problem do you like solving?", category="logical_thinking")
                db.session.add(q4)
                db.session.flush()
                db.session.add(QuizOption(question_id=q4.id, option_text="Debugging code issues", score_value=json.dumps({"Full Stack Developer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q4.id, option_text="Improving product experience", score_value=json.dumps({"Product Manager": 4, "UI/UX Designer": 3})))
                db.session.add(QuizOption(question_id=q4.id, option_text="Finding data trends", score_value=json.dumps({"Data Analyst": 4, "Data Scientist": 3})))
                db.session.add(QuizOption(question_id=q4.id, option_text="Handling people-related conflicts", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 4})))

                # Question 5
                q5 = QuizQuestion(question_text="What best describes your working style?", category="personality")
                db.session.add(q5)
                db.session.flush()
                db.session.add(QuizOption(question_id=q5.id, option_text="Independent and technical", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 4})))
                db.session.add(QuizOption(question_id=q5.id, option_text="Creative and visual", score_value=json.dumps({"Graphic Designer": 4, "UI/UX Designer": 4})))
                db.session.add(QuizOption(question_id=q5.id, option_text="Analytical and precise", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 4})))
                db.session.add(QuizOption(question_id=q5.id, option_text="People-focused and supportive", score_value=json.dumps({"HR Specialist": 4, "Counselor": 3})))

                # Question 6
                q6 = QuizQuestion(question_text="Which tool sounds most interesting to you?", category="technical_interest")
                db.session.add(q6)
                db.session.flush()
                db.session.add(QuizOption(question_id=q6.id, option_text="Programming frameworks", score_value=json.dumps({"Full Stack Developer": 4, "Software Engineer": 3})))
                db.session.add(QuizOption(question_id=q6.id, option_text="Design tools", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q6.id, option_text="Analytics dashboards", score_value=json.dumps({"Data Analyst": 5, "Business Analyst": 3})))
                db.session.add(QuizOption(question_id=q6.id, option_text="Interview and survey methods", score_value=json.dumps({"HR Specialist": 4, "Recruiter": 3})))

                # Question 7
                q7 = QuizQuestion(question_text="What kind of output do you enjoy creating?", category="creativity")
                db.session.add(q7)
                db.session.flush()
                db.session.add(QuizOption(question_id=q7.id, option_text="Working software", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 4})))
                db.session.add(QuizOption(question_id=q7.id, option_text="Beautiful designs", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q7.id, option_text="Insightful reports", score_value=json.dumps({"Data Analyst": 4, "Business Analyst": 3})))
                db.session.add(QuizOption(question_id=q7.id, option_text="Strong team communication", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 8
                q8 = QuizQuestion(question_text="Which challenge feels most rewarding?", category="problem_solving")
                db.session.add(q8)
                db.session.flush()
                db.session.add(QuizOption(question_id=q8.id, option_text="Fixing a broken feature", score_value=json.dumps({"Backend Developer": 4, "Software Engineer": 3})))
                db.session.add(QuizOption(question_id=q8.id, option_text="Improving a design layout", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q8.id, option_text="Explaining data insights", score_value=json.dumps({"Data Analyst": 4, "Business Analyst": 3})))
                db.session.add(QuizOption(question_id=q8.id, option_text="Resolving team issues", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 9
                q9 = QuizQuestion(question_text="Which type of the Work Would you enjoy the most?", category="analytical_skills")
                db.session.add(q9)
                db.session.flush()
                db.session.add(QuizOption(question_id=q9.id, option_text="Building software system and managing technical data", score_value=json.dumps({"Software Engineer": 3, "Data Engineer": 4})))
                db.session.add(QuizOption(question_id=q9.id, option_text="Desinging attractive and user-friendly digital products", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q9.id, option_text="analysing data and discovering useful insights", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q9.id, option_text="helping people and supporting their personal or professional needs", score_value=json.dumps({"HR Specialist": 4, "Counselor": 3})))

                # Question 10
                q10 = QuizQuestion(question_text="What kind of class or subject did you like most?", category="mathematics")
                db.session.add(q10)
                db.session.flush()
                db.session.add(QuizOption(question_id=q10.id, option_text="Computer science", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q10.id, option_text="Art and design", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q10.id, option_text="Math and statistics", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q10.id, option_text="Communication and management", score_value=json.dumps({"HR Specialist": 4, "Business Analyst": 3})))

                # Question 11
                q11 = QuizQuestion(question_text="Which task would you choose at work?", category="technical_interest")
                db.session.add(q11)
                db.session.flush()
                db.session.add(QuizOption(question_id=q11.id, option_text="Build a feature", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q11.id, option_text="Create a prototype", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q11.id, option_text="Analyze user behavior", score_value=json.dumps({"Data Analyst": 4, "Product Analyst": 3})))
                db.session.add(QuizOption(question_id=q11.id, option_text="Interview team members", score_value=json.dumps({"HR Specialist": 4, "Recruiter": 3})))

                # Question 12
                q12 = QuizQuestion(question_text="Which skill would you like to use most at work?", category="personality")
                db.session.add(q12)
                db.session.flush()
                db.session.add(QuizOption(question_id=q12.id, option_text="Programming", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 4})))
                db.session.add(QuizOption(question_id=q12.id, option_text="Designing", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q12.id, option_text="Data analysis", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q12.id, option_text="Leadership", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 13
                q13 = QuizQuestion(question_text="How do you like to solve a tough issue?", category="logical_thinking")
                db.session.add(q13)
                db.session.flush()
                db.session.add(QuizOption(question_id=q13.id, option_text="Test and debug", score_value=json.dumps({"Full Stack Developer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q13.id, option_text="Sketch and compare ideas", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q13.id, option_text="Measure and analyze", score_value=json.dumps({"Data Scientist": 4, "Business Analyst": 3})))
                db.session.add(QuizOption(question_id=q13.id, option_text="Talk and coordinate", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 14
                q14 = QuizQuestion(question_text="Which project would you enjoy most?", category="creativity")
                db.session.add(q14)
                db.session.flush()
                db.session.add(QuizOption(question_id=q14.id, option_text="A web application", score_value=json.dumps({"Full Stack Developer": 4, "Software Engineer": 3})))
                db.session.add(QuizOption(question_id=q14.id, option_text="A mobile app design", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q14.id, option_text="A data dashboard", score_value=json.dumps({"Data Analyst": 5, "Data Scientist": 3})))
                db.session.add(QuizOption(question_id=q14.id, option_text="A hiring process plan", score_value=json.dumps({"HR Specialist": 4, "Recruiter": 3})))

                # Question 15
                q15 = QuizQuestion(question_text="What pace suits you best?", category="personality")
                db.session.add(q15)
                db.session.flush()
                db.session.add(QuizOption(question_id=q15.id, option_text="Fast technical execution", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 4})))
                db.session.add(QuizOption(question_id=q15.id, option_text="Thoughtful design iteration", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q15.id, option_text="Careful analysis", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q15.id, option_text="People coordination", score_value=json.dumps({"HR Specialist": 4, "Operations Manager": 3})))

                # Question 16
                q16 = QuizQuestion(question_text="What would you rather learn?", category="technical_interest")
                db.session.add(q16)
                db.session.flush()
                db.session.add(QuizOption(question_id=q16.id, option_text="APIs and backend systems", score_value=json.dumps({"Backend Developer": 4, "Software Engineer": 3})))
                db.session.add(QuizOption(question_id=q16.id, option_text="Color and layout design", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q16.id, option_text="Statistics and ML models", score_value=json.dumps({"Data Scientist": 4, "ML Engineer": 3})))
                db.session.add(QuizOption(question_id=q16.id, option_text="People and policies", score_value=json.dumps({"HR Specialist": 4, "Recruiter": 5})))

                # Question 17
                q17 = QuizQuestion(question_text="Which statement feels most like you?", category="personality")
                db.session.add(q17)
                db.session.flush()
                db.session.add(QuizOption(question_id=q17.id, option_text="I like building useful systems", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q17.id, option_text="I like making experiences better", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q17.id, option_text="I like finding hidden insights", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 4})))
                db.session.add(QuizOption(question_id=q17.id, option_text="I like supporting people", score_value=json.dumps({"HR Specialist": 4, "Counselor": 4})))

                # Question 18
                q18 = QuizQuestion(question_text="Which mistake bothers you most?", category="logical_thinking")
                db.session.add(q18)
                db.session.flush()
                db.session.add(QuizOption(question_id=q18.id, option_text="Broken code logic", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q18.id, option_text="Ugly or confusing design", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q18.id, option_text="Wrong data interpretation", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q18.id, option_text="Poor communication", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 5})))

                # Question 19
                q19 = QuizQuestion(question_text="What kind of success feels best?", category="personality")
                db.session.add(q19)
                db.session.flush()
                db.session.add(QuizOption(question_id=q19.id, option_text="Shipping a working feature", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q19.id, option_text="Improving user satisfaction", score_value=json.dumps({"UI/UX Designer": 4, "Product Manager": 4})))
                db.session.add(QuizOption(question_id=q19.id, option_text="Finding a strong pattern in data", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 4})))
                db.session.add(QuizOption(question_id=q19.id, option_text="Helping the team work smoothly", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 5})))

                # Question 20
                q20 = QuizQuestion(question_text="What do you prefer in teamwork?", category="communication")
                db.session.add(q20)
                db.session.flush()
                db.session.add(QuizOption(question_id=q20.id, option_text="Technical contribution", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 4})))
                db.session.add(QuizOption(question_id=q20.id, option_text="Creative contribution", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q20.id, option_text="Analytical contribution", score_value=json.dumps({"Data Analyst": 4, "Data Scientist": 3})))
                db.session.add(QuizOption(question_id=q20.id, option_text="Coordination contribution", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 4})))
                
                                # Question 21
                q21 = QuizQuestion(question_text="Which work environment suits you?", category="personality")
                db.session.add(q21)
                db.session.flush()
                db.session.add(QuizOption(question_id=q21.id, option_text="Engineering team", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q21.id, option_text="Creative studio", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q21.id, option_text="Data team", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 4})))
                db.session.add(QuizOption(question_id=q21.id, option_text="People operations team", score_value=json.dumps({"HR Specialist": 4, "Operations Manager": 5})))

                # Question 22
                q22 = QuizQuestion(question_text="Which output would you proudly show others?", category="creativity")
                db.session.add(q22)
                db.session.flush()
                db.session.add(QuizOption(question_id=q22.id, option_text="An app feature", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q22.id, option_text="A prototype screen", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 5})))
                db.session.add(QuizOption(question_id=q22.id, option_text="A data report", score_value=json.dumps({"Data Analyst": 4, "Business Analyst": 3})))
                db.session.add(QuizOption(question_id=q22.id, option_text="A team improvement plan", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 4})))

                # Question 23
                q23 = QuizQuestion(question_text="What kind of thinking comes naturally?", category="logical_thinking")
                db.session.add(q23)
                db.session.flush()
                db.session.add(QuizOption(question_id=q23.id, option_text="System thinking", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q23.id, option_text="Visual thinking", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q23.id, option_text="Data thinking", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q23.id, option_text="People thinking", score_value=json.dumps({"HR Specialist": 4, "Counselor": 3})))

                # Question 24
                q24 = QuizQuestion(question_text="Which task feels least boring?", category="technical_interest")
                db.session.add(q24)
                db.session.flush()
                db.session.add(QuizOption(question_id=q24.id, option_text="Writing backend logic", score_value=json.dumps({"Backend Developer": 5, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q24.id, option_text="Choosing colors and spacing", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q24.id, option_text="Cleaning and visualizing data", score_value=json.dumps({"Data Analyst": 5, "Data Scientist": 3})))
                db.session.add(QuizOption(question_id=q24.id, option_text="Helping a new teammate", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 4})))

                # Question 25
                q25 = QuizQuestion(question_text="What type of feedback do you prefer?", category="communication")
                db.session.add(q25)
                db.session.flush()
                db.session.add(QuizOption(question_id=q25.id, option_text="Technical feedback", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q25.id, option_text="Design feedback", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q25.id, option_text="Data feedback", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q25.id, option_text="People feedback", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 4})))

                # Question 26
                q26 = QuizQuestion(question_text="Which area sounds most fun to explore?", category="technical_interest")
                db.session.add(q26)
                db.session.flush()
                db.session.add(QuizOption(question_id=q26.id, option_text="System architecture", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q26.id, option_text="Brand visuals", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q26.id, option_text="Predictive analytics", score_value=json.dumps({"Data Scientist": 4, "ML Engineer": 3})))
                db.session.add(QuizOption(question_id=q26.id, option_text="Employee engagement", score_value=json.dumps({"HR Specialist": 4, "Operations Manager": 4})))

                # Question 27
                q27 = QuizQuestion(question_text="What do you do first when something goes wrong?", category="problem_solving")
                db.session.add(q27)
                db.session.flush()
                db.session.add(QuizOption(question_id=q27.id, option_text="Check the technical cause", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q27.id, option_text="Check the user impact", score_value=json.dumps({"UI/UX Designer": 4, "Product Manager": 3})))
                db.session.add(QuizOption(question_id=q27.id, option_text="Check the data", score_value=json.dumps({"Data Analyst": 5, "Data Scientist": 3})))
                db.session.add(QuizOption(question_id=q27.id, option_text="Check the people side", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 28
                q28 = QuizQuestion(question_text="Which kind of task do you avoid the least?", category="personality")
                db.session.add(q28)
                db.session.flush()
                db.session.add(QuizOption(question_id=q28.id, option_text="Long coding sessions", score_value=json.dumps({"Full Stack Developer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q28.id, option_text="Design revisions", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q28.id, option_text="Data cleaning", score_value=json.dumps({"Data Analyst": 4, "Data Scientist": 3})))
                db.session.add(QuizOption(question_id=q28.id, option_text="Team discussions", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 4})))

                # Question 29
                q29 = QuizQuestion(question_text="Which skill do you want to improve most?", category="mathematics")
                db.session.add(q29)
                db.session.flush()
                db.session.add(QuizOption(question_id=q29.id, option_text="Programming", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q29.id, option_text="Designing", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q29.id, option_text="Analytics", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q29.id, option_text="Leadership", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 30
                q30 = QuizQuestion(question_text="What do people usually ask your help for?", category="communication")
                db.session.add(q30)
                db.session.flush()
                db.session.add(QuizOption(question_id=q30.id, option_text="Tech issues", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q30.id, option_text="Visual ideas", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q30.id, option_text="Data interpretation", score_value=json.dumps({"Data Analyst": 4, "Data Scientist": 3})))
                db.session.add(QuizOption(question_id=q30.id, option_text="People handling", score_value=json.dumps({"HR Specialist": 4, "Counselor": 3})))

                # Question 31
                q31 = QuizQuestion(question_text="What sounds most satisfying?", category="problem_solving")
                db.session.add(q31)
                db.session.flush()
                db.session.add(QuizOption(question_id=q31.id, option_text="A working product", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q31.id, option_text="A beautiful interface", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q31.id, option_text="A useful insight", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q31.id, option_text="A happier team", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 32
                q32 = QuizQuestion(question_text="Which kind of meeting would you enjoy most?", category="communication")
                db.session.add(q32)
                db.session.flush()
                db.session.add(QuizOption(question_id=q32.id, option_text="Technical planning", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q32.id, option_text="Design review", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q32.id, option_text="Data review", score_value=json.dumps({"Data Analyst": 4, "Business Analyst": 3})))
                db.session.add(QuizOption(question_id=q32.id, option_text="Team support meeting", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 33
                q33 = QuizQuestion(question_text="What would you rather build?", category="creativity")
                db.session.add(q33)
                db.session.flush()
                db.session.add(QuizOption(question_id=q33.id, option_text="A backend service", score_value=json.dumps({"Backend Developer": 4, "Software Engineer": 3})))
                db.session.add(QuizOption(question_id=q33.id, option_text="A brand identity", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q33.id, option_text="A prediction model", score_value=json.dumps({"Data Scientist": 4, "ML Engineer": 5})))
                db.session.add(QuizOption(question_id=q33.id, option_text="A hiring process", score_value=json.dumps({"HR Specialist": 4, "Recruiter": 3})))

                # Question 34
                q34 = QuizQuestion(question_text="Which task feels most natural under pressure?", category="logical_thinking")
                db.session.add(q34)
                db.session.flush()
                db.session.add(QuizOption(question_id=q34.id, option_text="Fixing code fast", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q34.id, option_text="Adjusting a design quickly", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q34.id, option_text="Finding the key metric", score_value=json.dumps({"Data Analyst": 4, "Data Scientist": 3})))
                db.session.add(QuizOption(question_id=q34.id, option_text="Calming the team", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 35
                q35 = QuizQuestion(question_text="What kind of work feels meaningful?", category="business")
                db.session.add(q35)
                db.session.flush()
                db.session.add(QuizOption(question_id=q35.id, option_text="Building useful systems", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 4})))
                db.session.add(QuizOption(question_id=q35.id, option_text="Making life easier for users", score_value=json.dumps({"UI/UX Designer": 4, "Product Manager": 3})))
                db.session.add(QuizOption(question_id=q35.id, option_text="Using data to decide better", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q35.id, option_text="Supporting people directly", score_value=json.dumps({"HR Specialist": 4, "Counselor": 3})))
               
                                # Question 36
                q36 = QuizQuestion(question_text="What do you like to optimize?", category="problem_solving")
                db.session.add(q36)
                db.session.flush()
                db.session.add(QuizOption(question_id=q36.id, option_text="System performance", score_value=json.dumps({"Full Stack Developer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q36.id, option_text="User experience", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q36.id, option_text="Data accuracy", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q36.id, option_text="Team harmony", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 37
                q37 = QuizQuestion(question_text="Which kind of work gives you energy?", category="personality")
                db.session.add(q37)
                db.session.flush()
                db.session.add(QuizOption(question_id=q37.id, option_text="Coding and building", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 4})))
                db.session.add(QuizOption(question_id=q37.id, option_text="Designing and creating", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q37.id, option_text="Analyzing and interpreting", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q37.id, option_text="Organizing and guiding", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 38
                q38 = QuizQuestion(question_text="Which sentence fits you best?", category="personality")
                db.session.add(q38)
                db.session.flush()
                db.session.add(QuizOption(question_id=q38.id, option_text="I enjoy technical challenges", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q38.id, option_text="I enjoy visual challenges", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q38.id, option_text="I enjoy analytical challenges", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q38.id, option_text="I enjoy people challenges", score_value=json.dumps({"HR Specialist": 4, "Operations Manager": 3})))

                # Question 39
                q39 = QuizQuestion(question_text="What do you focus on first in a project?", category="business")
                db.session.add(q39)
                db.session.flush()
                db.session.add(QuizOption(question_id=q39.id, option_text="The structure", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q39.id, option_text="The appearance", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q39.id, option_text="The numbers", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q39.id, option_text="The people", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 4})))

                # Question 40
                q40 = QuizQuestion(question_text="Which outcome matters most to you?", category="business")
                db.session.add(q40)
                db.session.flush()
                db.session.add(QuizOption(question_id=q40.id, option_text="A stable system", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q40.id, option_text="A pleasing experience", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 4})))
                db.session.add(QuizOption(question_id=q40.id, option_text="A smart decision", score_value=json.dumps({"Data Scientist": 4, "Business Analyst": 3})))
                db.session.add(QuizOption(question_id=q40.id, option_text="A healthy team", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 41
                q41 = QuizQuestion(question_text="How do you prefer to communicate ideas?", category="communication")
                db.session.add(q41)
                db.session.flush()
                db.session.add(QuizOption(question_id=q41.id, option_text="Through code", score_value=json.dumps({"Full Stack Developer": 4, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q41.id, option_text="Through visuals", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q41.id, option_text="Through data", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q41.id, option_text="Through conversation", score_value=json.dumps({"HR Specialist": 4, "Sales Executive": 3})))

                # Question 42
                q42 = QuizQuestion(question_text="Which kind of decision do you trust most?", category="logical_thinking")
                db.session.add(q42)
                db.session.flush()
                db.session.add(QuizOption(question_id=q42.id, option_text="Technical decision", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q42.id, option_text="Design decision", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q42.id, option_text="Data-driven decision", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q42.id, option_text="People-first decision", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))

                # Question 43
                q43 = QuizQuestion(question_text="What would you rather spend a weekend doing?", category="creativity")
                db.session.add(q43)
                db.session.flush()
                db.session.add(QuizOption(question_id=q43.id, option_text="Building an app", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q43.id, option_text="Designing a poster", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q43.id, option_text="Exploring a dataset", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q43.id, option_text="Organizing a group event", score_value=json.dumps({"HR Specialist": 4, "Event Coordinator": 3})))

                # Question 44
                q44 = QuizQuestion(question_text="What feels like a strong match for your personality?", category="personality")
                db.session.add(q44)
                db.session.flush()
                db.session.add(QuizOption(question_id=q44.id, option_text="Logical and technical", score_value=json.dumps({"Software Engineer": 4, "Backend Developer": 3})))
                db.session.add(QuizOption(question_id=q44.id, option_text="Creative and visual", score_value=json.dumps({"UI/UX Designer": 4, "Graphic Designer": 3})))
                db.session.add(QuizOption(question_id=q44.id, option_text="Curious and analytical", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q44.id, option_text="Friendly and supportive", score_value=json.dumps({"HR Specialist": 4, "Counselor": 3})))

                # Question 45
                q45 = QuizQuestion(question_text="Which career direction sounds most like your future?", category="business")
                db.session.add(q45)
                db.session.flush()
                db.session.add(QuizOption(question_id=q45.id, option_text="Software development", score_value=json.dumps({"Software Engineer": 4, "Full Stack Developer": 3})))
                db.session.add(QuizOption(question_id=q45.id, option_text="Design and creativity", score_value=json.dumps({"UI/UX Designer": 4, "Product Designer": 3})))
                db.session.add(QuizOption(question_id=q45.id, option_text="Data and analytics", score_value=json.dumps({"Data Scientist": 4, "Data Analyst": 3})))
                db.session.add(QuizOption(question_id=q45.id, option_text="People and management", score_value=json.dumps({"HR Specialist": 4, "Team Lead": 3})))
                db.session.commit()

            print("Successfully seeded 45 quiz questions and options!")

        # 4. Seed 3 Blog posts if empty
        if Blog.query.count() == 0:
            print("Seeding guides blog posts...")
            b1 = Blog(
                title="Mastering Technical Placements: An Alumnus Handbook",
                content="The key to landing software developer or architect positions at tier-1 innovators lies in building a strong computational foundation. Focus on mastering: \n\n1. Data Structures & Algorithms: Focus on array, string, dynamic programming, and binary trees. Practice regularly on LeetCode.\n2. System Design: Understand how web systems scale. Study caching, databases, CDN, and load balancer placements.\n3. Open Source contributions: Contributions demonstrate collaborative coding skills and version control expertise.",
                author_name="System Admin",
                tags="Technical Placement,Career Guide",
                read_time=6
            )
            b2 = Blog(
                title="Succeeding in UI/UX Design Case Studies",
                content="To clear recruiter filters in design agencies, a basic certificate is rarely enough. A complete UI/UX portfolio must tell a structured story:\n\n1. Define the Problem: Highlight why the project matters, tracking user statistics.\n2. Iterative Wireframes: Show sketches and low-fidelity prototypes. Explain why you discarded specific designs.\n3. User Validation: Explain how testing feedback helped refine the final design.",
                author_name="System Admin",
                tags="UIUX Design,Portfolio Guide",
                read_time=5
            )
            b3 = Blog(
                title="DevOps Toolchain Roadmap: A Beginner Guide",
                content="DevOps is currently one of the fastest growing fields in engineering. If you are starting out, follow this linear toolchain roadmap:\n\n1. Linux Administration: Understand the command line, ssh configurations, and process controls.\n2. Docker: Learn how container configuration files are written.\n3. Git & CI/CD Pipelines: Build pipelines automatically running testing scripts on push triggers.",
                author_name="System Admin",
                tags="DevOps,Cloud Systems",
                read_time=8
            )
            db.session.add(b1)
            db.session.add(b2)
            db.session.add(b3)
            db.session.commit()
            print("Successfully seeded guides blog posts!")

        print("Database Seeding Finished Successfully!")

if __name__ == "__main__":
    seed_database()
