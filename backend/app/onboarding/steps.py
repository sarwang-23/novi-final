from enum import Enum

class StepType(str, Enum):
    DETERMINISTIC = "deterministic"
    AI_ASSISTED = "ai_assisted"

class InputType(str, Enum):
    TEXT = "text"
    SINGLE_SELECT = "single_select"
    MULTI_SELECT = "multi_select"
    SEARCHABLE_SELECT = "searchable_select"

ONBOARDING_STEPS = [
    {"id": "name", "order": 1, "type": StepType.DETERMINISTIC, "input_type": InputType.TEXT,
     "question": "What should I call you?", "save_field": "preferred_name"},

    {"id": "country", "order": 2, "type": StepType.DETERMINISTIC, "input_type": InputType.SEARCHABLE_SELECT,
     "question": "Where do you currently live or study?",
     "options_source": "countries", "save_field": "country_code"},

    {"id": "curriculum", "order": 3, "type": StepType.DETERMINISTIC, "input_type": InputType.SINGLE_SELECT,
     "question": "Which curriculum are you studying under?",
     "options_source": "curriculums", "requires": ["country"], "save_field": "curriculum_id"},

    {"id": "grade", "order": 4, "type": StepType.DETERMINISTIC, "input_type": InputType.SINGLE_SELECT,
     "question": "Which grade/year are you in?",
     "options_source": "grades", "requires": ["country", "curriculum"], "save_field": "grade_id"},

    {"id": "saturday", "order": 5, "type": StepType.DETERMINISTIC, "input_type": InputType.MULTI_SELECT,
     "question": "What could you happily spend an entire Saturday doing?",
     "options_source": "static:saturday_activities", "save_field": "saturday_activities"},

    {"id": "strengths", "order": 6, "type": StepType.DETERMINISTIC, "input_type": InputType.MULTI_SELECT,
     "question": "Your best friend has to describe you. What would they say you're really good at?",
     "options_source": "static:strengths", "save_field": "strengths"},

    {"id": "enjoyed_subjects", "order": 7, "type": StepType.DETERMINISTIC, "input_type": InputType.MULTI_SELECT,
     "question": "Which subjects do you actually enjoy?",
     "options_source": "subjects", "requires": ["country", "curriculum", "grade"], "save_field": "enjoyed_subjects"},

    {"id": "hard_subjects", "order": 8, "type": StepType.DETERMINISTIC, "input_type": InputType.MULTI_SELECT,
     "question": "Which subjects feel hard?",
     "options_source": "subjects", "requires": ["country", "curriculum", "grade"], "save_field": "difficult_subjects"},

    {"id": "learning_style", "order": 9, "type": StepType.DETERMINISTIC, "input_type": InputType.SINGLE_SELECT,
     "question": "When you want to learn something new, what do you usually do?",
     "options_source": "static:learning_style", "save_field": "learning_preference"},

    {"id": "confidence", "order": 10, "type": StepType.DETERMINISTIC, "input_type": InputType.SINGLE_SELECT,
     "question": "Which feels most like you?",
     "options_source": "static:confidence", "save_field": "confidence_choice"},

    {"id": "university", "order": 11, "type": StepType.AI_ASSISTED, "input_type": InputType.TEXT,
     "question": "Do you have a university you'd love to study at? If yes, where is it?"},

    {"id": "career", "order": 12, "type": StepType.DETERMINISTIC, "input_type": InputType.SINGLE_SELECT,
     "question": "Do you currently have a career in mind?",
     "options_source": "static:career_stage", "save_field": "has_career_in_mind"},

    {"id": "career_name", "order": 13, "type": StepType.AI_ASSISTED, "input_type": InputType.TEXT,
     "question": "What career are you thinking about?"},

    {"id": "career_reason", "order": 14, "type": StepType.AI_ASSISTED, "input_type": InputType.TEXT,
     "question": "What makes you interested in it?"},

    {"id": "primary_goal", "order": 15, "type": StepType.AI_ASSISTED, "input_type": InputType.TEXT,
     "question": "If Novi could help you with one thing, what would you want it to be?"},
]