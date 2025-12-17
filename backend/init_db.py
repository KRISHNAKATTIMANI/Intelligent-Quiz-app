"""
Database initialization script
Run this to create default roles and sample data
"""
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.models import db, Role, User, Category, Subcategory, Topic
from app.utils.password import hash_password
from datetime import datetime


def init_roles():
    """Create default roles"""
    roles = ['Admin', 'Teacher', 'Student']
    
    for role_name in roles:
        role = Role.query.filter_by(role_name=role_name).first()
        if not role:
            role = Role(role_name=role_name)
            db.session.add(role)
            print(f"Created role: {role_name}")
    
    db.session.commit()
    print("Roles initialized successfully")


def create_admin_user():
    """Create default admin user"""
    admin_role = Role.query.filter_by(role_name='Admin').first()
    
    if not admin_role:
        print("Error: Admin role not found. Run init_roles first.")
        return
    
    # Check if admin already exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("Admin user already exists")
        return
    
    admin = User(
        username='admin',
        email='admin@quizapp.com',
        password_hash=hash_password('Admin@123'),
        full_name='System Administrator',
        role_id=admin_role.role_id,
        is_active=True
    )
    
    db.session.add(admin)
    db.session.commit()
    print("Admin user created: username=admin, password=Admin@123")


def init_sample_categories():
    """Create comprehensive categories from beginner to professional level"""
    
    categories_data = [
        # Elementary/Primary Level (Ages 6-10)
        {
            'name': 'Basic Mathematics',
            'description': 'Elementary math concepts for young learners',
            'icon': '🔢',
            'subcategories': [
                {'name': 'Counting & Numbers', 'topics': ['Numbers 1-100', 'Skip Counting', 'Place Value', 'Number Patterns']},
                {'name': 'Addition & Subtraction', 'topics': ['Single Digit', 'Double Digit', 'Word Problems', 'Mental Math']},
                {'name': 'Shapes & Geometry', 'topics': ['2D Shapes', '3D Shapes', 'Symmetry', 'Patterns']},
            ]
        },
        {
            'name': 'Basic English',
            'description': 'Foundational English language skills',
            'icon': '📚',
            'subcategories': [
                {'name': 'Alphabet & Phonics', 'topics': ['Letter Recognition', 'Letter Sounds', 'Vowels & Consonants', 'Blending']},
                {'name': 'Reading Comprehension', 'topics': ['Short Stories', 'Picture Books', 'Main Ideas', 'Sequencing']},
                {'name': 'Grammar Basics', 'topics': ['Nouns', 'Verbs', 'Adjectives', 'Sentence Formation']},
            ]
        },
        
        # Middle School Level (Ages 11-14)
        {
            'name': 'Mathematics',
            'description': 'Mathematical concepts and problem solving',
            'icon': '📐',
            'subcategories': [
                {'name': 'Algebra', 'topics': ['Linear Equations', 'Quadratic Equations', 'Polynomials', 'Functions', 'Inequalities']},
                {'name': 'Geometry', 'topics': ['Angles', 'Triangles', 'Circles', 'Area & Perimeter', 'Volume', 'Pythagorean Theorem']},
                {'name': 'Statistics', 'topics': ['Mean Median Mode', 'Probability', 'Data Analysis', 'Graphs & Charts']},
                {'name': 'Number Theory', 'topics': ['Fractions', 'Decimals', 'Percentages', 'Ratios', 'Prime Numbers']},
            ]
        },
        {
            'name': 'Science',
            'description': 'Scientific concepts and discoveries',
            'icon': '🔬',
            'subcategories': [
                {'name': 'Physics', 'topics': ['Motion', 'Force', 'Energy', 'Light', 'Sound', 'Electricity', 'Magnetism']},
                {'name': 'Chemistry', 'topics': ['Atoms & Molecules', 'Chemical Reactions', 'Acids & Bases', 'Periodic Table', 'States of Matter']},
                {'name': 'Biology', 'topics': ['Cell Structure', 'Human Body', 'Plants', 'Ecology', 'Genetics', 'Evolution']},
                {'name': 'Earth Science', 'topics': ['Weather', 'Climate', 'Rocks & Minerals', 'Water Cycle', 'Solar System']},
            ]
        },
        
        # High School Level (Ages 15-18)
        {
            'name': 'Advanced Mathematics',
            'description': 'Higher level mathematical concepts',
            'icon': '🧮',
            'subcategories': [
                {'name': 'Calculus', 'topics': ['Limits', 'Derivatives', 'Integration', 'Differential Equations', 'Series']},
                {'name': 'Trigonometry', 'topics': ['Sine Cosine Tangent', 'Unit Circle', 'Identities', 'Graphs', 'Applications']},
                {'name': 'Linear Algebra', 'topics': ['Matrices', 'Vectors', 'Systems of Equations', 'Eigenvalues', 'Transformations']},
                {'name': 'Discrete Math', 'topics': ['Set Theory', 'Logic', 'Combinatorics', 'Graph Theory', 'Algorithms']},
            ]
        },
        {
            'name': 'Programming',
            'description': 'Computer programming and software development',
            'icon': '💻',
            'subcategories': [
                {'name': 'Python', 'topics': ['Basics & Syntax', 'Data Structures', 'OOP', 'Functions', 'File Handling', 'Libraries']},
                {'name': 'JavaScript', 'topics': ['ES6+ Features', 'DOM Manipulation', 'Async Programming', 'React.js', 'Node.js']},
                {'name': 'Java', 'topics': ['Core Java', 'Collections', 'Multithreading', 'Spring Framework', 'Design Patterns']},
                {'name': 'Web Development', 'topics': ['HTML', 'CSS', 'Responsive Design', 'APIs', 'Databases']},
            ]
        },
        {
            'name': 'English Literature',
            'description': 'Literary analysis and composition',
            'icon': '📖',
            'subcategories': [
                {'name': 'Poetry', 'topics': ['Types of Poetry', 'Figurative Language', 'Analysis', 'Famous Poets']},
                {'name': 'Prose', 'topics': ['Short Stories', 'Novels', 'Drama', 'Literary Devices', 'Themes']},
                {'name': 'Writing', 'topics': ['Essay Writing', 'Creative Writing', 'Grammar', 'Vocabulary', 'Citation']},
            ]
        },
        {
            'name': 'History',
            'description': 'World and regional history',
            'icon': '🏛️',
            'subcategories': [
                {'name': 'World History', 'topics': ['Ancient Civilizations', 'Medieval Period', 'Renaissance', 'World Wars', 'Modern Era']},
                {'name': 'American History', 'topics': ['Colonial Period', 'Revolutionary War', 'Civil War', 'Industrial Age', 'Cold War']},
                {'name': 'Indian History', 'topics': ['Ancient India', 'Mughal Empire', 'British Rule', 'Independence Movement', 'Modern India']},
            ]
        },
        
        # College/University Level
        {
            'name': 'Data Science',
            'description': 'Data analysis and machine learning',
            'icon': '📊',
            'subcategories': [
                {'name': 'Statistics', 'topics': ['Descriptive Statistics', 'Inferential Statistics', 'Hypothesis Testing', 'Regression', 'ANOVA']},
                {'name': 'Machine Learning', 'topics': ['Supervised Learning', 'Unsupervised Learning', 'Neural Networks', 'Deep Learning', 'NLP']},
                {'name': 'Data Visualization', 'topics': ['Matplotlib', 'Seaborn', 'Plotly', 'Tableau', 'Power BI']},
                {'name': 'Big Data', 'topics': ['Hadoop', 'Spark', 'Data Warehousing', 'ETL', 'Cloud Computing']},
            ]
        },
        {
            'name': 'Computer Science',
            'description': 'Theoretical and applied computing',
            'icon': '🖥️',
            'subcategories': [
                {'name': 'Data Structures', 'topics': ['Arrays', 'Linked Lists', 'Trees', 'Graphs', 'Hash Tables', 'Heaps']},
                {'name': 'Algorithms', 'topics': ['Sorting', 'Searching', 'Dynamic Programming', 'Greedy', 'Divide & Conquer']},
                {'name': 'Operating Systems', 'topics': ['Process Management', 'Memory Management', 'File Systems', 'Threading', 'Scheduling']},
                {'name': 'Computer Networks', 'topics': ['TCP/IP', 'HTTP', 'DNS', 'Security', 'Protocols']},
            ]
        },
        {
            'name': 'Artificial Intelligence',
            'description': 'AI and intelligent systems',
            'icon': '🤖',
            'subcategories': [
                {'name': 'AI Fundamentals', 'topics': ['Search Algorithms', 'Knowledge Representation', 'Planning', 'Reasoning', 'Expert Systems']},
                {'name': 'Computer Vision', 'topics': ['Image Processing', 'Object Detection', 'Face Recognition', 'CNN', 'Image Segmentation']},
                {'name': 'Natural Language Processing', 'topics': ['Tokenization', 'NER', 'Sentiment Analysis', 'Transformers', 'BERT', 'GPT']},
                {'name': 'Robotics', 'topics': ['Kinematics', 'Control Systems', 'Sensors', 'Path Planning', 'ROS']},
            ]
        },
        {
            'name': 'Business & Management',
            'description': 'Business administration and management',
            'icon': '💼',
            'subcategories': [
                {'name': 'Marketing', 'topics': ['Market Research', 'Digital Marketing', 'Branding', 'SEO', 'Social Media', 'Content Marketing']},
                {'name': 'Finance', 'topics': ['Accounting', 'Financial Analysis', 'Investment', 'Risk Management', 'Valuation']},
                {'name': 'Human Resources', 'topics': ['Recruitment', 'Training', 'Performance Management', 'Employee Relations', 'Compensation']},
                {'name': 'Operations', 'topics': ['Supply Chain', 'Logistics', 'Quality Management', 'Project Management', 'Lean Six Sigma']},
            ]
        },
        
        # Professional/Certification Level
        {
            'name': 'Cloud Computing',
            'description': 'Cloud platforms and services',
            'icon': '☁️',
            'subcategories': [
                {'name': 'AWS', 'topics': ['EC2', 'S3', 'Lambda', 'RDS', 'VPC', 'IAM', 'CloudFormation']},
                {'name': 'Azure', 'topics': ['Virtual Machines', 'Storage', 'Functions', 'SQL Database', 'Active Directory']},
                {'name': 'Google Cloud', 'topics': ['Compute Engine', 'Cloud Storage', 'BigQuery', 'Kubernetes Engine', 'App Engine']},
                {'name': 'DevOps', 'topics': ['CI/CD', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'Ansible']},
            ]
        },
        {
            'name': 'Cybersecurity',
            'description': 'Information security and ethical hacking',
            'icon': '🔐',
            'subcategories': [
                {'name': 'Network Security', 'topics': ['Firewalls', 'VPN', 'IDS/IPS', 'Network Protocols', 'Wireless Security']},
                {'name': 'Application Security', 'topics': ['OWASP Top 10', 'SQL Injection', 'XSS', 'CSRF', 'Authentication', 'Encryption']},
                {'name': 'Ethical Hacking', 'topics': ['Penetration Testing', 'Vulnerability Assessment', 'Exploit Development', 'Social Engineering']},
                {'name': 'Cryptography', 'topics': ['Symmetric Encryption', 'Asymmetric Encryption', 'Hash Functions', 'Digital Signatures', 'PKI']},
            ]
        },
        {
            'name': 'Database Management',
            'description': 'Database design and administration',
            'icon': '🗄️',
            'subcategories': [
                {'name': 'SQL', 'topics': ['SELECT Queries', 'JOINs', 'Indexes', 'Views', 'Stored Procedures', 'Triggers']},
                {'name': 'NoSQL', 'topics': ['MongoDB', 'Cassandra', 'Redis', 'DynamoDB', 'Document Stores']},
                {'name': 'Database Design', 'topics': ['ER Diagrams', 'Normalization', 'Schema Design', 'Optimization', 'Transactions']},
                {'name': 'Data Warehousing', 'topics': ['OLAP', 'Data Modeling', 'ETL', 'Star Schema', 'Snowflake Schema']},
            ]
        },
        {
            'name': 'Mobile Development',
            'description': 'iOS and Android app development',
            'icon': '📱',
            'subcategories': [
                {'name': 'Android', 'topics': ['Kotlin', 'Java', 'Activities', 'Fragments', 'Material Design', 'Firebase']},
                {'name': 'iOS', 'topics': ['Swift', 'SwiftUI', 'UIKit', 'Core Data', 'Networking', 'App Store']},
                {'name': 'React Native', 'topics': ['Components', 'Navigation', 'State Management', 'APIs', 'Deployment']},
                {'name': 'Flutter', 'topics': ['Dart', 'Widgets', 'State Management', 'Animations', 'Platform Integration']},
            ]
        },
        {
            'name': 'Blockchain',
            'description': 'Blockchain technology and cryptocurrency',
            'icon': '⛓️',
            'subcategories': [
                {'name': 'Fundamentals', 'topics': ['Distributed Ledger', 'Consensus', 'Mining', 'Cryptography', 'Smart Contracts']},
                {'name': 'Ethereum', 'topics': ['Solidity', 'Web3', 'DApps', 'ERC Standards', 'Gas Optimization']},
                {'name': 'Cryptocurrency', 'topics': ['Bitcoin', 'Altcoins', 'Wallets', 'Exchanges', 'Trading']},
                {'name': 'DeFi', 'topics': ['DEX', 'Lending', 'Staking', 'Yield Farming', 'NFTs']},
            ]
        },
        
        # Specialized Professional Fields
        {
            'name': 'Digital Marketing',
            'description': 'Online marketing strategies',
            'icon': '📢',
            'subcategories': [
                {'name': 'SEO', 'topics': ['On-Page SEO', 'Off-Page SEO', 'Technical SEO', 'Keyword Research', 'Link Building']},
                {'name': 'Social Media', 'topics': ['Facebook Ads', 'Instagram Marketing', 'LinkedIn', 'Twitter', 'TikTok', 'Analytics']},
                {'name': 'Content Marketing', 'topics': ['Blogging', 'Video Marketing', 'Email Marketing', 'Copywriting', 'Lead Generation']},
                {'name': 'PPC', 'topics': ['Google Ads', 'Display Ads', 'Remarketing', 'Conversion Optimization', 'A/B Testing']},
            ]
        },
        {
            'name': 'Graphic Design',
            'description': 'Visual design and creativity',
            'icon': '🎨',
            'subcategories': [
                {'name': 'Adobe Suite', 'topics': ['Photoshop', 'Illustrator', 'InDesign', 'After Effects', 'Premiere Pro']},
                {'name': 'UI/UX Design', 'topics': ['User Research', 'Wireframing', 'Prototyping', 'Figma', 'User Testing']},
                {'name': 'Branding', 'topics': ['Logo Design', 'Brand Identity', 'Color Theory', 'Typography', 'Style Guides']},
                {'name': '3D Design', 'topics': ['Blender', 'Maya', '3D Modeling', 'Texturing', 'Rendering']},
            ]
        },
        {
            'name': 'Project Management',
            'description': 'Project planning and execution',
            'icon': '📋',
            'subcategories': [
                {'name': 'Agile', 'topics': ['Scrum', 'Kanban', 'Sprint Planning', 'User Stories', 'Retrospectives']},
                {'name': 'PMP', 'topics': ['Initiation', 'Planning', 'Execution', 'Monitoring', 'Closing']},
                {'name': 'Tools', 'topics': ['Jira', 'Trello', 'Asana', 'MS Project', 'Gantt Charts']},
                {'name': 'Leadership', 'topics': ['Team Management', 'Communication', 'Risk Management', 'Stakeholder Management']},
            ]
        },
        {
            'name': 'Data Engineering',
            'description': 'Data pipeline and infrastructure',
            'icon': '⚙️',
            'subcategories': [
                {'name': 'ETL', 'topics': ['Data Integration', 'Data Quality', 'Data Transformation', 'Airflow', 'Luigi']},
                {'name': 'Streaming', 'topics': ['Kafka', 'Spark Streaming', 'Flink', 'Real-time Processing']},
                {'name': 'Data Lakes', 'topics': ['S3', 'HDFS', 'Delta Lake', 'Data Catalog', 'Partitioning']},
                {'name': 'Orchestration', 'topics': ['Workflow Management', 'Scheduling', 'Monitoring', 'Data Lineage']},
            ]
        },
        {
            'name': 'IoT (Internet of Things)',
            'description': 'Connected devices and embedded systems',
            'icon': '🌐',
            'subcategories': [
                {'name': 'Embedded Systems', 'topics': ['Microcontrollers', 'Arduino', 'Raspberry Pi', 'Sensors', 'Actuators']},
                {'name': 'Protocols', 'topics': ['MQTT', 'CoAP', 'Zigbee', 'Bluetooth', 'LoRaWAN']},
                {'name': 'IoT Platforms', 'topics': ['AWS IoT', 'Azure IoT', 'Google IoT', 'ThingSpeak', 'Node-RED']},
                {'name': 'Applications', 'topics': ['Smart Home', 'Industrial IoT', 'Wearables', 'Agriculture', 'Healthcare']},
            ]
        },
        
        # Language & Culture
        {
            'name': 'Foreign Languages',
            'description': 'Learn new languages',
            'icon': '🌍',
            'subcategories': [
                {'name': 'Spanish', 'topics': ['Grammar', 'Vocabulary', 'Conversation', 'Reading', 'Writing']},
                {'name': 'French', 'topics': ['Grammar', 'Vocabulary', 'Pronunciation', 'Culture', 'Literature']},
                {'name': 'German', 'topics': ['Grammar', 'Vocabulary', 'Articles', 'Cases', 'Conversation']},
                {'name': 'Mandarin', 'topics': ['Characters', 'Pinyin', 'Grammar', 'Tones', 'Culture']},
            ]
        },
        {
            'name': 'Music Theory',
            'description': 'Understanding music fundamentals',
            'icon': '🎵',
            'subcategories': [
                {'name': 'Basics', 'topics': ['Notes', 'Scales', 'Chords', 'Rhythm', 'Time Signatures']},
                {'name': 'Advanced', 'topics': ['Harmony', 'Counterpoint', 'Orchestration', 'Composition', 'Analysis']},
                {'name': 'Instruments', 'topics': ['Piano', 'Guitar', 'Violin', 'Drums', 'Voice']},
            ]
        },
        {
            'name': 'Photography',
            'description': 'Photography techniques and editing',
            'icon': '📷',
            'subcategories': [
                {'name': 'Fundamentals', 'topics': ['Exposure', 'Aperture', 'Shutter Speed', 'ISO', 'Composition']},
                {'name': 'Genres', 'topics': ['Portrait', 'Landscape', 'Street', 'Wildlife', 'Product']},
                {'name': 'Post-Processing', 'topics': ['Lightroom', 'Color Grading', 'Retouching', 'RAW Processing']},
            ]
        },
        
        # Health & Wellness
        {
            'name': 'Health & Fitness',
            'description': 'Physical and mental wellness',
            'icon': '💪',
            'subcategories': [
                {'name': 'Nutrition', 'topics': ['Macronutrients', 'Meal Planning', 'Supplements', 'Diet Plans', 'Weight Management']},
                {'name': 'Exercise', 'topics': ['Strength Training', 'Cardio', 'Flexibility', 'HIIT', 'Yoga']},
                {'name': 'Mental Health', 'topics': ['Stress Management', 'Meditation', 'Mindfulness', 'Sleep', 'Work-Life Balance']},
            ]
        },
        {
            'name': 'Medical Science',
            'description': 'Healthcare and medicine',
            'icon': '⚕️',
            'subcategories': [
                {'name': 'Anatomy', 'topics': ['Skeletal System', 'Muscular System', 'Nervous System', 'Cardiovascular', 'Respiratory']},
                {'name': 'Physiology', 'topics': ['Cell Biology', 'Metabolism', 'Endocrine', 'Immune System', 'Homeostasis']},
                {'name': 'Pharmacology', 'topics': ['Drug Classes', 'Mechanisms', 'Interactions', 'Dosage', 'Side Effects']},
                {'name': 'Clinical', 'topics': ['Diagnosis', 'Treatment', 'Patient Care', 'Medical Ethics', 'Evidence-Based Medicine']},
            ]
        },
        
        # Legal & Compliance
        {
            'name': 'Law & Legal Studies',
            'description': 'Legal principles and practice',
            'icon': '⚖️',
            'subcategories': [
                {'name': 'Constitutional Law', 'topics': ['Rights', 'Powers', 'Amendments', 'Judicial Review', 'Federalism']},
                {'name': 'Criminal Law', 'topics': ['Elements of Crime', 'Defenses', 'Procedures', 'Sentencing', 'Evidence']},
                {'name': 'Corporate Law', 'topics': ['Business Formation', 'Contracts', 'Mergers', 'Compliance', 'Securities']},
                {'name': 'Intellectual Property', 'topics': ['Patents', 'Trademarks', 'Copyrights', 'Trade Secrets', 'Licensing']},
            ]
        },
        {
            'name': 'Economics',
            'description': 'Economic theory and practice',
            'icon': '💰',
            'subcategories': [
                {'name': 'Microeconomics', 'topics': ['Supply & Demand', 'Elasticity', 'Market Structures', 'Consumer Theory', 'Game Theory']},
                {'name': 'Macroeconomics', 'topics': ['GDP', 'Inflation', 'Unemployment', 'Monetary Policy', 'Fiscal Policy']},
                {'name': 'International Economics', 'topics': ['Trade', 'Exchange Rates', 'Balance of Payments', 'Globalization']},
                {'name': 'Behavioral Economics', 'topics': ['Decision Making', 'Biases', 'Nudging', 'Prospect Theory']},
            ]
        },
        
        # Engineering
        {
            'name': 'Mechanical Engineering',
            'description': 'Mechanical systems and design',
            'icon': '⚙️',
            'subcategories': [
                {'name': 'Mechanics', 'topics': ['Statics', 'Dynamics', 'Kinematics', 'Strength of Materials', 'Fluid Mechanics']},
                {'name': 'Thermodynamics', 'topics': ['Laws', 'Heat Transfer', 'Engines', 'Refrigeration', 'Power Plants']},
                {'name': 'Design', 'topics': ['CAD', 'Manufacturing', 'Materials', 'Machine Design', 'Automation']},
            ]
        },
        {
            'name': 'Electrical Engineering',
            'description': 'Electrical systems and circuits',
            'icon': '⚡',
            'subcategories': [
                {'name': 'Circuits', 'topics': ['DC Circuits', 'AC Circuits', 'Network Theory', 'Circuit Analysis', 'Filters']},
                {'name': 'Electronics', 'topics': ['Diodes', 'Transistors', 'Op-Amps', 'Digital Electronics', 'Microcontrollers']},
                {'name': 'Power Systems', 'topics': ['Generation', 'Transmission', 'Distribution', 'Transformers', 'Motors']},
                {'name': 'Control Systems', 'topics': ['Feedback', 'Stability', 'PID', 'State Space', 'Modern Control']},
            ]
        },
        {
            'name': 'Civil Engineering',
            'description': 'Infrastructure and construction',
            'icon': '🏗️',
            'subcategories': [
                {'name': 'Structures', 'topics': ['Beams', 'Columns', 'Frames', 'Trusses', 'Foundations', 'Steel Design']},
                {'name': 'Geotechnical', 'topics': ['Soil Mechanics', 'Foundation Design', 'Slope Stability', 'Retaining Walls']},
                {'name': 'Transportation', 'topics': ['Highway Design', 'Traffic Engineering', 'Railways', 'Airport Design']},
                {'name': 'Environmental', 'topics': ['Water Supply', 'Wastewater', 'Solid Waste', 'Air Quality', 'Sustainability']},
            ]
        },
    ]
    
    for cat_data in categories_data:
        category = Category.query.filter_by(category_name=cat_data['name']).first()
        if not category:
            category = Category(
                category_name=cat_data['name'],
                description=cat_data['description'],
                icon=cat_data['icon']
            )
            db.session.add(category)
            db.session.flush()
            
            for subcat_data in cat_data['subcategories']:
                subcategory = Subcategory(
                    category_id=category.category_id,
                    subcategory_name=subcat_data['name'],
                    description=f"{cat_data['name']} - {subcat_data['name']}"
                )
                db.session.add(subcategory)
                db.session.flush()
                
                for topic_name in subcat_data['topics']:
                    topic = Topic(
                        subcategory_id=subcategory.subcategory_id,
                        topic_name=topic_name,
                        description=f"{subcat_data['name']} - {topic_name}"
                    )
                    db.session.add(topic)
    
    db.session.commit()
    print(f"Created {len(categories_data)} categories with comprehensive subcategories and topics")


def init_database():
    """Initialize complete database with default data"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully")
        
        print("\nInitializing roles...")
        init_roles()
        
        print("\nCreating admin user...")
        create_admin_user()
        
        print("\nCreating sample categories...")
        init_sample_categories()
        
        print("\n✅ Database initialization complete!")
        print("\nDefault credentials:")
        print("  Username: admin")
        print("  Password: Admin@123")
        print("\nYou can now start the Flask server with: python run.py")


if __name__ == '__main__':
    init_database()
