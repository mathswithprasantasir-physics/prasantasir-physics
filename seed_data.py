from app import app, db
from database import Question

def seed_database():
    with app.app_context():
        # Clear existing data
        db.session.query(Question).delete()
        db.session.commit()
        
        # Sample questions with solutions
        sample_questions = [
            {
                'topic': 'Motion in a Straight Line',
                'subtopic': 'Kinematics',
                'year': '2026',
                'question_text': 'Consider a particle moving along a straight line, whose position as a function of time is given by s(t) = αt² − βt + γ, where α = 1 m/s², β = 6 m/s and γ = 5 m. The average speed of the particle from t = 0 to t = 6 s is:',
                'option_a': '2 m/s',
                'option_b': '3 m/s',
                'option_c': '4 m/s',
                'option_d': '5 m/s',
                'correct_answer': 'A',
                'solution': 'Given: s(t) = t² - 6t + 5\n\nAt t=0: s(0) = 0 - 0 + 5 = 5m\nAt t=6: s(6) = 36 - 36 + 5 = 5m\n\nTotal distance = |s(6) - s(0)| = |5 - 5| = 0m\n\nWait! Let me check carefully:\n\ns(t) = t² - 6t + 5\nv(t) = 2t - 6\n\nVelocity changes direction at t = 3s\n\nTotal distance = ∫₀³ (6-2t)dt + ∫₃⁶ (2t-6)dt\n= [6t - t²]₀³ + [t² - 6t]₃⁶\n= (18-9) + (36-36 - 9 + 18)\n= 9 + 9 = 18m\n\nAverage speed = Total distance / Time = 18/6 = 3 m/s',
                'explanation': 'Average speed is total distance divided by total time. We need to consider the change in direction.',
                'marks': 4,
                'negative_marks': 1,
                'exam_type': 'NEET',
                'difficulty': 'Medium'
            },
            {
                'topic': 'Laws of Motion',
                'subtopic': 'Newton\'s Laws',
                'year': '2026',
                'question_text': 'A block of mass 2 kg is placed on a smooth horizontal surface. A force of 10 N is applied horizontally. What is the acceleration of the block?',
                'option_a': '2 m/s²',
                'option_b': '3 m/s²',
                'option_c': '4 m/s²',
                'option_d': '5 m/s²',
                'correct_answer': 'D',
                'solution': 'Using Newton\'s second law: F = ma\n\nF = 10 N, m = 2 kg\n\na = F/m = 10/2 = 5 m/s²',
                'explanation': 'Newton\'s second law states that acceleration is directly proportional to net force and inversely proportional to mass.',
                'marks': 4,
                'negative_marks': 1,
                'exam_type': 'NEET',
                'difficulty': 'Easy'
            },
            {
                'topic': 'Work, Energy and Power',
                'subtopic': 'Work-Energy Theorem',
                'year': '2026',
                'question_text': 'A body of mass 5 kg is moving with a velocity of 10 m/s. What is its kinetic energy?',
                'option_a': '250 J',
                'option_b': '300 J',
                'option_c': '200 J',
                'option_d': '150 J',
                'correct_answer': 'A',
                'solution': 'Kinetic Energy = ½ × m × v²\n\n= ½ × 5 × (10)²\n= ½ × 5 × 100\n= 250 J',
                'explanation': 'Kinetic energy is the energy possessed by a body due to its motion.',
                'marks': 4,
                'negative_marks': 1,
                'exam_type': 'NEET',
                'difficulty': 'Easy'
            },
            {
                'topic': 'Atoms and Nuclei',
                'subtopic': 'Nuclear Physics',
                'year': '2026',
                'question_text': 'The half-life of a radioactive substance is 10 years. How much time will it take for 75% of the substance to decay?',
                'option_a': '10 years',
                'option_b': '20 years',
                'option_c': '30 years',
                'option_d': '40 years',
                'correct_answer': 'B',
                'solution': 'If 75% decays, 25% remains.\n\nN/N₀ = (1/2)ⁿ where n = number of half-lives\n\n0.25 = (1/2)ⁿ\n(1/2)² = (1/2)ⁿ\nn = 2\n\nTime = n × half-life = 2 × 10 = 20 years',
                'explanation': 'Radioactive decay follows first-order kinetics. After n half-lives, the remaining fraction is (1/2)ⁿ.',
                'marks': 4,
                'negative_marks': 1,
                'exam_type': 'NEET',
                'difficulty': 'Hard'
            },
            {
                'topic': 'Heat and Thermodynamics',
                'subtopic': 'Thermodynamics',
                'year': '2026',
                'question_text': 'A gas expands isothermally from volume V₁ to V₂. What is the work done by the gas?',
                'option_a': 'nRT ln(V₂/V₁)',
                'option_b': 'nRT (V₂ - V₁)',
                'option_c': 'nRT ln(V₁/V₂)',
                'option_d': 'nRT/(V₂ - V₁)',
                'correct_answer': 'A',
                'solution': 'For isothermal process, work done = ∫PdV\n\nUsing ideal gas equation: P = nRT/V\n\nW = ∫(nRT/V)dV from V₁ to V₂\nW = nRT ln(V₂/V₁)',
                'explanation': 'Isothermal means constant temperature. Work done is calculated using integration of P dV.',
                'marks': 4,
                'negative_marks': 1,
                'exam_type': 'NEET',
                'difficulty': 'Medium'
            }
        ]
        
        for q_data in sample_questions:
            question = Question(**q_data)
            db.session.add(question)
        
        db.session.commit()
        print(f"✅ Added {len(sample_questions)} sample questions!")

if __name__ == '__main__':
    seed_database()