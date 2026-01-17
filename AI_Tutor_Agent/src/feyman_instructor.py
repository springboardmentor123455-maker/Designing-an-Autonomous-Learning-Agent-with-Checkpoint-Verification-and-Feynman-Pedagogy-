import os
import time
from dotenv import load_dotenv
from openai import AzureOpenAI
from langsmith.wrappers import wrap_openai

load_dotenv()

client = wrap_openai(AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
))
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def identify_knowledge_gaps(questions, user_answers, correct_answers, assessment_type="objective"):
    """
    Identify specific concepts the user struggled with based on incorrect answers.
    
    Args:
        questions: List of question texts or dicts
        user_answers: Dict mapping question index to user's answer
        correct_answers: Dict mapping question index to correct answer
        assessment_type: "objective" or "subjective"
    
    Returns:
        List of knowledge gaps (concept strings)
    """
    gaps = []
    
    for idx, question in enumerate(questions):
        user_ans = user_answers.get(idx, "")
        
        if assessment_type == "objective":
            # For MCQ, check if answer matches
            correct_ans = correct_answers.get(idx, "")
            if user_ans != correct_ans:
                # Extract concept from question
                q_text = question.get('question', '') if isinstance(question, dict) else str(question)
                gaps.append(q_text)
        
        elif assessment_type == "subjective":
            # For subjective, check if score was low (< 70)
            # correct_answers here contains the evaluation results
            eval_result = correct_answers.get(idx, {})
            score = eval_result.get('score', 0)
            if score < 70:
                q_text = question if isinstance(question, str) else question.get('question', '')
                gaps.append(q_text)
    
    return gaps


def generate_feynman_explanation(knowledge_gaps, original_context, topic):
    """
    Generate simplified Feynman-style explanation for identified knowledge gaps.
    Uses analogies, simple language, and avoids jargon.
    
    Args:
        knowledge_gaps: List of concepts user struggled with
        original_context: The formatted study material
        topic: Current checkpoint topic
    
    Returns:
        str: Simplified explanation
    """
    if not knowledge_gaps:
        return "No specific gaps identified. Review the material and try again."
    
    # Prepare gap summary
    gaps_text = "\n".join([f"- {gap}" for gap in knowledge_gaps[:3]])  # Limit to top 3
    
    system_instruction = """You are a master teacher using the Feynman Technique.
    Your goal is to explain complex concepts in the SIMPLEST possible way:
    
    - Use everyday analogies and metaphors
    - Avoid technical jargon
    - Break down into tiny, digestible steps
    - Use concrete examples from daily life
    - Speak as if teaching a curious 12-year-old
    - If you must use a technical term, immediately explain it in simple words
    
    Remember: If you can't explain it simply, you don't understand it well enough."""
    
    user_prompt = f"""
    TOPIC: {topic}
    
    ORIGINAL STUDY MATERIAL (for reference):
    {original_context[:1500]}
    
    CONCEPTS THE STUDENT STRUGGLED WITH:
    {gaps_text}
    
    Provide a simplified, Feynman-style explanation that addresses these specific gaps.
    Use analogies, simple language, and real-world examples.
    Format with clear headings and bullet points for readability.
    remember don't provide answers to questions, just the explanation.
    """
    
    try:
        time.sleep(2)  # Rate limiting
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=6000,
            model=deployment
        )
        
        feynman_explanation = response.choices[0].message.content
        return feynman_explanation
        
    except Exception as e:
        return f"Error generating explanation: {str(e)}\n\nPlease review the original material and try again."


def format_feynman_for_display(explanation, attempt_count):
    """
    Format Feynman explanation with encouraging messaging.
    """
    header = f"""
### Let's Simplify This! (Attempt {attempt_count})

Learning is a process. Let's break down the concepts you found challenging into simpler terms.

---

"""
    
    footer = """

---

**Tip:** Try explaining these concepts out loud in your own words before retaking the assessment.
    """
    
    return header + explanation + footer