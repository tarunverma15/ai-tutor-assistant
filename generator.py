import json
from groq import Groq


class QuestionGenerator:

    def __init__(self, client: Groq, model: str):
        self.client = client
        self.model = model

    def generate_question(
        self,
        knowledge,
        difficulty,
        question_type,
        previous_questions
    ):

        system_prompt = f"""
You are an expert teacher.

Generate EXACTLY ONE question.

Difficulty Level: {difficulty}

Question Type: {question_type}

Rules:

If Question Type is MCQ:
- Four options.
- One correct option.

If Question Type is Short Answer:
- Generate one conceptual question.
- Model answer should be 2-4 lines.

If Question Type is Long Answer:
- Generate one descriptive question.
- Model answer should be around 150 words.

If Question Type is True/False:
- Generate one statement.
- Correct answer should be either True or False.
- Model answer should be a 1-2 line justification of why the statement is true or false.

If Question Type is Fill in the Blanks:
- Replace ONE important keyword using ______.
- Model answer should be a 1-2 line explanation of why that word fits.

If Question Type is One Word:
- Generate one question whose answer is exactly one word.
- Model answer should be a 1-2 line explanation of the concept behind the answer.

General Rules:
- Include a "model_answer" field in every JSON response, for every question type.
- Include a "topic" field in every JSON response.
- The topic must be the main concept from which the generated question is taken.
- Determine the topic from the provided knowledge automatically.
- Examples: Machine Learning, Neural Networks, Operating System, DBMS, Python, Java, Sorting Algorithms, Computer Networks, Data Structures, Artificial Intelligence.
- Never repeat previous questions.
- Avoid asking about the same concept.
- Choose different topics whenever possible.

Return ONLY JSON.

For MCQ

{{
    "topic":"...",
    "question_type":"MCQ",
    "question":"...",
    "options":[
        "A)...",
        "B)...",
        "C)...",
        "D)..."
    ],
    "correct_answer":"A",
    "model_answer":"..."
}}

For Short Answer

{{
    "topic":"...",
    "question_type":"Short Answer",
    "question":"...",
    "model_answer":"..."
}}

For Long Answer

{{
    "topic":"...",
    "question_type":"Long Answer",
    "question":"...",
    "model_answer":"..."
}}

For Fill in the Blanks

{{
    "topic":"...",
    "question_type":"Fill in the Blanks",
    "question":"AI is a subset of ______.",
    "correct_answer":"Computer Science",
    "model_answer":"..."
}}

For True/False

{{
    "topic":"...",
    "question_type":"True/False",
    "question":"Deep Learning requires large datasets.",
    "correct_answer":"True",
    "model_answer":"..."
}}

For One Word

{{
    "topic":"...",
    "question_type":"One Word",
    "question":"Which algorithm uses multiple decision trees?",
    "correct_answer":"Random Forest",
    "model_answer":"..."
}}
"""

        user_prompt = f"""
Knowledge:

{knowledge}

Previous Questions:

{"\n".join(previous_questions)}

Generate ONE NEW question.

Return JSON only.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            response_format={
                "type": "json_object"
            }
        )

        return json.loads(
            response.choices[0].message.content
        )