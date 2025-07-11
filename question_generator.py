import random
import numpy as np
from typing import List, Tuple, Dict, Any
from math_utils import RationalFunction

class Question:
    """Represents a single question about rational functions"""
    def __init__(self, function: RationalFunction, question: str, correct_answer: str, 
                 question_type: str = "text", options: List[str] = None):
        self.function = function
        self.question = question
        self.correct_answer = correct_answer
        self.question_type = question_type
        self.options = options or []
    
    def check_answer(self, answer: str) -> bool:
        """Check if the provided answer is correct"""
        if self.question_type == "multiple_choice":
            return answer == self.correct_answer
        else:
            # For text answers, be flexible with formatting
            answer = answer.strip().lower()
            correct = self.correct_answer.strip().lower()
            
            # Handle common mathematical expressions
            answer = answer.replace(" ", "").replace("y=", "").replace("x=", "")
            correct = correct.replace(" ", "").replace("y=", "").replace("x=", "")
            
            return answer == correct

class QuestionGenerator:
    """Generates questions about rational functions"""
    def __init__(self):
        self.difficulty_level = 1
        self.questions_answered = 0
    
    def generate_question(self) -> Question:
        """Generate a new question based on current difficulty"""
        # Increase difficulty every 5 questions
        self.difficulty_level = min(5, 1 + self.questions_answered // 5)
        
        # Generate a random rational function
        function = self._generate_random_function()
        
        # Choose question type
        question_types = [
            "vertical_asymptote",
            "horizontal_asymptote", 
            "hole",
            "y_intercept",
            "x_intercept",
            "end_behavior"
        ]
        
        question_type = random.choice(question_types)
        question = self._generate_question_by_type(function, question_type)
        
        self.questions_answered += 1
        return question
    
    def _generate_random_function(self) -> RationalFunction:
        """Generate a random rational function based on difficulty"""
        if self.difficulty_level == 1:
            # Simple functions: (ax + b) / (cx + d)
            a, b = random.randint(-5, 5), random.randint(-5, 5)
            c, d = random.randint(-5, 5), random.randint(-5, 5)
            if c == 0:
                c = 1
            numerator = [a, b]
            denominator = [c, d]
        
        elif self.difficulty_level == 2:
            # Medium functions: (ax^2 + bx + c) / (dx + e)
            a, b, c = random.randint(-3, 3), random.randint(-5, 5), random.randint(-5, 5)
            d, e = random.randint(-5, 5), random.randint(-5, 5)
            if a == 0:
                a = 1
            if d == 0:
                d = 1
            numerator = [a, b, c]
            denominator = [d, e]
        
        else:
            # Complex functions: (ax^2 + bx + c) / (dx^2 + ex + f)
            a, b, c = random.randint(-3, 3), random.randint(-5, 5), random.randint(-5, 5)
            d, e, f = random.randint(-3, 3), random.randint(-5, 5), random.randint(-5, 5)
            if a == 0:
                a = 1
            if d == 0:
                d = 1
            numerator = [a, b, c]
            denominator = [d, e, f]
        
        return RationalFunction(numerator, denominator)
    
    def _generate_question_by_type(self, function: RationalFunction, question_type: str) -> Question:
        """Generate a specific type of question"""
        if question_type == "vertical_asymptote":
            return self._vertical_asymptote_question(function)
        elif question_type == "horizontal_asymptote":
            return self._horizontal_asymptote_question(function)
        elif question_type == "hole":
            return self._hole_question(function)
        elif question_type == "y_intercept":
            return self._y_intercept_question(function)
        elif question_type == "x_intercept":
            return self._x_intercept_question(function)
        elif question_type == "end_behavior":
            return self._end_behavior_question(function)
        else:
            return self._vertical_asymptote_question(function)
    
    def _vertical_asymptote_question(self, function: RationalFunction) -> Question:
        """Generate a vertical asymptote question"""
        va = function.vertical_asymptotes()
        
        if len(va) == 0:
            correct = "none"
            question = "What is the vertical asymptote of this function?"
        elif len(va) == 1:
            correct = f"x = {va[0]}"
            question = "What is the vertical asymptote of this function?"
        else:
            correct = f"x = {va[0]}, x = {va[1]}"
            question = "What are the vertical asymptotes of this function?"
        
        # Create multiple choice options
        options = [correct]
        for _ in range(3):
            fake_x = random.randint(-5, 5)
            while fake_x in va:
                fake_x = random.randint(-5, 5)
            options.append(f"x = {fake_x}")
        
        if len(va) == 0:
            options = ["none", "x = 0", "x = 1", "x = -1"]
        
        random.shuffle(options)
        
        return Question(function, question, correct, "multiple_choice", options)
    
    def _horizontal_asymptote_question(self, function: RationalFunction) -> Question:
        """Generate a horizontal asymptote question"""
        ha = function.horizontal_asymptote()
        
        if ha is None:
            correct = "none"
            question = "What is the horizontal asymptote of this function?"
            options = ["none", "y = 0", "y = 1", "y = -1"]
        else:
            correct = f"y = {ha}"
            question = "What is the horizontal asymptote of this function?"
            options = [correct]
            for _ in range(3):
                fake_y = random.randint(-3, 3)
                while fake_y == ha:
                    fake_y = random.randint(-3, 3)
                options.append(f"y = {fake_y}")
        
        random.shuffle(options)
        
        return Question(function, question, correct, "multiple_choice", options)
    
    def _hole_question(self, function: RationalFunction) -> Question:
        """Generate a hole question"""
        holes = function.holes()
        
        if len(holes) == 0:
            correct = "none"
            question = "Does this function have any holes? If so, where?"
            options = ["none", "(0, 0)", "(1, 1)", "(-1, -1)"]
        else:
            hole_x, hole_y = holes[0]
            correct = f"({hole_x}, {hole_y})"
            question = "Where is the hole in this function?"
            options = [correct]
            for _ in range(3):
                fake_x = random.randint(-3, 3)
                fake_y = random.randint(-3, 3)
                options.append(f"({fake_x}, {fake_y})")
        
        random.shuffle(options)
        
        return Question(function, question, correct, "multiple_choice", options)
    
    def _y_intercept_question(self, function: RationalFunction) -> Question:
        """Generate a y-intercept question"""
        y_int = function.y_intercept()
        
        if y_int is None:
            correct = "none"
            question = "What is the y-intercept of this function?"
            options = ["none", "(0, 0)", "(0, 1)", "(0, -1)"]
        else:
            correct = f"(0, {y_int})"
            question = "What is the y-intercept of this function?"
            options = [correct]
            for _ in range(3):
                fake_y = random.randint(-5, 5)
                while fake_y == y_int:
                    fake_y = random.randint(-5, 5)
                options.append(f"(0, {fake_y})")
        
        random.shuffle(options)
        
        return Question(function, question, correct, "multiple_choice", options)
    
    def _x_intercept_question(self, function: RationalFunction) -> Question:
        """Generate an x-intercept question"""
        x_ints = function.x_intercepts()
        
        if len(x_ints) == 0:
            correct = "none"
            question = "What are the x-intercepts of this function?"
            options = ["none", "(0, 0)", "(1, 0)", "(-1, 0)"]
        elif len(x_ints) == 1:
            correct = f"({x_ints[0]}, 0)"
            question = "What is the x-intercept of this function?"
            options = [correct]
            for _ in range(3):
                fake_x = random.randint(-5, 5)
                while fake_x == x_ints[0]:
                    fake_x = random.randint(-5, 5)
                options.append(f"({fake_x}, 0)")
        else:
            correct = f"({x_ints[0]}, 0), ({x_ints[1]}, 0)"
            question = "What are the x-intercepts of this function?"
            options = [correct]
            for _ in range(3):
                fake_x1 = random.randint(-5, 5)
                fake_x2 = random.randint(-5, 5)
                options.append(f"({fake_x1}, 0), ({fake_x2}, 0)")
        
        random.shuffle(options)
        
        return Question(function, question, correct, "multiple_choice", options)
    
    def _end_behavior_question(self, function: RationalFunction) -> Question:
        """Generate an end behavior question"""
        end_behavior = function.end_behavior()
        
        question = "What is the end behavior of this function as x approaches infinity?"
        correct = end_behavior
        
        options = [correct]
        behaviors = ["approaches 0", "approaches 1", "approaches -1", "approaches infinity", "approaches -infinity"]
        
        for behavior in behaviors:
            if behavior != correct and len(options) < 4:
                options.append(behavior)
        
        random.shuffle(options)
        
        return Question(function, question, correct, "multiple_choice", options)
