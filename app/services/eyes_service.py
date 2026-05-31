"""
Vision screening test service
Handles the logic for presenting characters and evaluating results
"""
import random
import string

# Characters to avoid confusion: O/0, I/1, Z/2, S/5
ALL_CHARS = [c for c in string.ascii_uppercase if c not in ['O', 'I', 'Z', 'S']]
ALL_DIGITS = [str(d) for d in range(10) if d not in [0, 1, 2, 5]]  # Exclude 0, 1, 2, 5

def get_device_config(device: str) -> dict:
    """Get font size and distance for selected device"""
    configs = {
        "phone": {
            "distance_cm": 50,
            "distance_steps": 0,
            "font_sizes": [60, 40, 25],  # Circle 1, 2, 3
            "description": "Hold phone at arm's length"
        },
        "laptop": {
            "distance_cm": 120,
            "distance_steps": 2,
            "font_sizes": [80, 55, 35],
            "description": "Walk approximately 2 steps (~120cm)"
        },
        "monitor": {
            "distance_cm": 180,
            "distance_steps": 3,
            "font_sizes": [100, 70, 45],
            "description": "Walk approximately 3 steps (~180cm)"
        }
    }
    return configs.get(device.lower(), configs["phone"])


def generate_test_character(is_letter: bool = True) -> str:
    """
    Generate a random character for the test
    Avoids easily confused pairs
    """
    if is_letter:
        return random.choice(ALL_CHARS)
    else:
        return random.choice(ALL_DIGITS)


def generate_multiple_choice(correct_answer: str, is_letter: bool = True) -> dict:
    """
    Generate 3 multiple choice options: 1 correct + 2 incorrect
    """
    options = [correct_answer]
    
    if is_letter:
        available = [c for c in ALL_CHARS if c != correct_answer]
    else:
        available = [d for d in ALL_DIGITS if d != correct_answer]
    
    # Get 2 random incorrect options
    incorrect = random.sample(available, 2)
    options.extend(incorrect)
    
    # Shuffle the order
    random.shuffle(options)
    
    return {
        "options": options,
        "correct": correct_answer,
        "correct_index": options.index(correct_answer)
    }


def evaluate_round(user_answer: str, correct_answer: str) -> dict:
    """
    Evaluate a single round's answer
    """
    is_correct = user_answer == correct_answer
    
    return {
        "is_correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "feedback": "Correct ✓" if is_correct else f"Incorrect ✗ — The correct answer is: {correct_answer}"
    }


def evaluate_results(correct_count: int, total_count: int = 3) -> dict:
    """
    Evaluate overall vision test results
    correct_count: number of correct answers (0-3)
    """
    score_percentage = (correct_count / total_count) * 100
    
    if correct_count == 3:
        level = "Good"
        label = "Good eyesight"
        description = "You see small characters at standard distance. Normal eyesight."
        should_see_doctor = False
        risk_level = "low"
    elif correct_count == 2:
        level = "Intermediate"
        label = "Intermediate vision"
        description = "You may experience blurriness at a distance. Further monitoring is recommended."
        should_see_doctor = False
        risk_level = "medium"
    else:  # 1 or 0
        level = "Weak"
        label = "Weak vision"
        description = "You have difficulty seeing small characters at a standard distance."
        should_see_doctor = True
        risk_level = "high"
    
    return {
        "success": True,
        "correct_count": correct_count,
        "total_count": total_count,
        "score_percentage": score_percentage,
        "level": level,
        "label": label,
        "description": description,
        "should_see_doctor": should_see_doctor,
        "risk_level": risk_level,
        "message": description,
        "disclaimer": "This is a screening test, not a substitute for ophthalmological examination."
    }
