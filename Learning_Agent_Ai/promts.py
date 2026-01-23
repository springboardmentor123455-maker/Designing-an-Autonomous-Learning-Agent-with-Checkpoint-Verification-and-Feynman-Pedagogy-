from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from structureOut import (FeynmanTeachingStruc, GapDetectionOutput,
                          PerQuestionScore, QuestionGeneratorStruc,
                          ValidatorStructure)

validator_parser = PydanticOutputParser(pydantic_object=ValidatorStructure)
validatorTemplate = PromptTemplate(
    template="""
You are an expert evaluator.

TASK:
Evaluate the learner's understanding of the topic "{topic}"
based strictly on the learning objective below.

LEARNING OBJECTIVE:
Below is a list of objectives the learner is expected to meet.
Evaluate EACH objective independently.
{objective}

GIVEN CONTEXT (AUTHORITATIVE REFERENCE):
Use ONLY this context as the source of truth.
Do NOT rely on external knowledge.
{context}


EVALUATION CRITERIA:
1. Conceptual correctness
2. Completeness relative to the objective
3. Clarity and logical reasoning
4. Ability to apply the concept (if applicable)

SCORING:
- Score from 0 to 10
- Be strict and consistent
- Do NOT assume missing knowledge

{format_instruction}
""",
    input_variables=["topic", "objective" , "context"],
    partial_variables={"format_instruction": validator_parser.get_format_instructions()}
)




question_parser = PydanticOutputParser(pydantic_object=QuestionGeneratorStruc)
question_temp = PromptTemplate(
    template="""
You are designing assessment questions for a learner.
Learning Topic:
{topic}

Learning objectives:
Below is a list of objectives the learner is expected to meet.
Evaluate EACH objective independently.
{objectives}

Learning material:
{context_chunks}

Instructions:
- Generate exactly 3 questions
- Not Generate numrical question and coding question
- Questions must be strictly based on the learning material
- Each question must test at least one learning objective
- Avoid vague or ambiguous wording

{format_instructions}
""",
input_variables=['topic','objectives' ,'context_chunks'],
partial_variables={
        "format_instructions": question_parser.get_format_instructions()
    }
)


answer_parser = PydanticOutputParser(pydantic_object=PerQuestionScore) 
answer_templete = PromptTemplate(
        template="""
You are evaluating a learner's understanding.

Questions:
{questions}

Learner answers:
{answers}

Reference material:
{context}

Evaluation rules:
- Evaluate EACH question-answer pair independently
- Score each answer from 0 to 100
- 0 = no understanding
- 100 = complete understanding
- Be strict but fair
- Judge conceptual correctness, not wording
- The number of scores MUST equal the number of questions
- Scores must follow the same order as the questions

{format_instructions}
""",
    input_variables=["questions", "answers", "context"],
    partial_variables={
        "format_instructions": answer_parser.get_format_instructions()
    }
)

gap_parser = PydanticOutputParser(pydantic_object=GapDetectionOutput)
gap_detection_prompt = PromptTemplate(
    template="""
You are diagnosing learning gaps.

Questions (numbered list in text form):
{questions}

Learner answers (corresponding numbered list):
{answers}

Reference material:
{context}

Instructions:
- Treat the questions and answers as ordered lists based on their numbering
- Identify ONLY questions where the learner misunderstood or missed a concept
- Use the question numbers exactly as shown in the questions text
- Describe the missing or incorrect concept briefly
- If understanding is correct, do NOT include that question

{format_instructions}
""",
    input_variables=["questions", "answers", "context"],
    partial_variables={
        "format_instructions": gap_parser.get_format_instructions()
    }
)

feynman_parser = PydanticOutputParser(pydantic_object=FeynmanTeachingStruc)
feynman_promt = PromptTemplate(
    template="""
You are teaching using the Feynman Technique.

The learner is confused about:
{gaps}

Learning context:
{context}

Teaching rules:
- Use very simple language
- Use everyday analogies
- Keep paragraphs short
- Avoid technical jargon
- Explain as if teaching a beginner

{format_instructions}
""",
    input_variables=["gaps" , "context"],
    partial_variables={"format_instructions": feynman_parser.get_format_instructions()
    }
)