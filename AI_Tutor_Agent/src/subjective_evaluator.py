import os
import time
import json
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

def evaluate_subjective_answers(questions, user_answers, context, topic):
    """
    Evaluates subjective answers using AI agent.
    Returns: {
        "results": [{"question", "user_answer", "score", "comments"}],
        "average_score": float
    }
    """
    results = []
    
    for idx, question in enumerate(questions):
        user_answer = user_answers.get(idx, "")
        
        if not user_answer.strip():
            results.append({
                "question": question,
                "user_answer": "No answer provided",
                "score": 0,
                "comments": "Answer not submitted."
            })
            continue
        
        time.sleep(2)  # Rate limit protection
        
        system_instruction = """You are an expert educator evaluating student answers provide readable feedback that is point wised and concise.
        Provide a score (0-100) and constructive feedback.
        Consider: accuracy, depth, clarity, and completeness for each sub-question asked like what exactly the questions wants separately to specify or provide, and yeah be lenient but don't spare bad answers."""
        
        user_prompt = f"""
        TOPIC: {topic}
        REFERENCE CONTEXT: {context[:1500]}
        
        QUESTION: {question}
        STUDENT ANSWER: {user_answer}
        
        Evaluate and return JSON:
        {{
            "score": <0-100>,
            "comments": "<detailed feedback with strengths and areas for improvement>"
        }}
        """
        
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=5000,
                model=deployment,
                response_format={"type": "json_object"}
            )
            
            eval_data = json.loads(response.choices[0].message.content)
            score = eval_data.get("score", 0)
            comments = eval_data.get("comments", "Evaluation error.")
            
        except Exception as e:
            score = 0
            comments = f"Evaluation failed: {str(e)}"
        
        results.append({
            "question": question,
            "user_answer": user_answer,
            "score": score,
            "comments": comments
        })
    
    avg_score = sum(r["score"] for r in results) / len(results) if results else 0
    
    return {
        "results": results,
        "average_score": avg_score
    }