// Comprehensive Saarland University International Programs - Based on actual offerings
const saarlandPrograms = [
    // Computer Science & Informatics (Saarland's strongest area)
    { title: 'Computer Science', degree: 'Master', fees: 'No tuition fees', faculty: 'Computer Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Cybersecurity', degree: 'Master', fees: 'No tuition fees', faculty: 'Computer Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Data Science and Artificial Intelligence', degree: 'Master', fees: 'No tuition fees', faculty: 'Computer Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Visual Computing', degree: 'Master', fees: 'No tuition fees', faculty: 'Computer Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Software Engineering', degree: 'Master', fees: 'No tuition fees', faculty: 'Computer Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Embedded Systems', degree: 'Master', fees: 'No tuition fees', faculty: 'Computer Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Bioinformatics', degree: 'Master', fees: 'No tuition fees', faculty: 'Computer Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Machine Learning', degree: 'Master', fees: 'No tuition fees', faculty: 'Computer Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    
    // Engineering
    { title: 'Mechanical Engineering', degree: 'Master', fees: 'No tuition fees', faculty: 'Engineering', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Materials Engineering', degree: 'Master', fees: 'No tuition fees', faculty: 'Engineering', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Microsystems Engineering', degree: 'Master', fees: 'No tuition fees', faculty: 'Engineering', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Systems Engineering', degree: 'Master', fees: 'No tuition fees', faculty: 'Engineering', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Automation and Robotics', degree: 'Master', fees: 'No tuition fees', faculty: 'Engineering', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    
    // Natural Sciences
    { title: 'Physics', degree: 'Master', fees: 'No tuition fees', faculty: 'Physics', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Chemistry', degree: 'Master', fees: 'No tuition fees', faculty: 'Chemistry', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Mathematics', degree: 'Master', fees: 'No tuition fees', faculty: 'Mathematics', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Molecular Biology', degree: 'Master', fees: 'No tuition fees', faculty: 'Life Sciences', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Microbiology', degree: 'Master', fees: 'No tuition fees', faculty: 'Life Sciences', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    
    // Medicine & Life Sciences  
    { title: 'Medical Informatics', degree: 'Master', fees: 'No tuition fees', faculty: 'Medicine', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Biomedical Engineering', degree: 'Master', fees: 'No tuition fees', faculty: 'Medicine', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Molecular Medicine', degree: 'Master', fees: 'No tuition fees', faculty: 'Medicine', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Drug Research and Development', degree: 'Master', fees: 'No tuition fees', faculty: 'Medicine', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    
    // Language & Cultural Studies (Saarland specialty)
    { title: 'Language Science and Technology', degree: 'Master', fees: 'No tuition fees', faculty: 'Language Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'European Literature and Media', degree: 'Master', fees: 'No tuition fees', faculty: 'Philosophy', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Multilingual Communication', degree: 'Master', fees: 'No tuition fees', faculty: 'Language Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Computational Linguistics', degree: 'Master', fees: 'No tuition fees', faculty: 'Language Science', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    
    // Business & Economics
    { title: 'Management', degree: 'Master', fees: 'No tuition fees', faculty: 'Business Administration', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Economics', degree: 'Master', fees: 'No tuition fees', faculty: 'Economics', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Information Systems', degree: 'Master', fees: 'No tuition fees', faculty: 'Business Administration', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Digital Business', degree: 'Master', fees: 'No tuition fees', faculty: 'Business Administration', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    
    // Psychology
    { title: 'Psychology', degree: 'Master', fees: 'No tuition fees', faculty: 'Psychology', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Cognitive Science', degree: 'Master', fees: 'No tuition fees', faculty: 'Psychology', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    
    // Law
    { title: 'European and International Law', degree: 'Master', fees: 'No tuition fees', faculty: 'Law', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'German and European Law', degree: 'Master', fees: 'No tuition fees', faculty: 'Law', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    
    // Education
    { title: 'Educational Technology', degree: 'Master', fees: 'No tuition fees', faculty: 'Education', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    
    // Geography & Environmental Science
    { title: 'Geography', degree: 'Master', fees: 'No tuition fees', faculty: 'Geography', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' },
    { title: 'Environmental Sciences', degree: 'Master', fees: 'No tuition fees', faculty: 'Geography', duration: '4 semesters', language: 'English', intake: 'Winter/Summer' }
];