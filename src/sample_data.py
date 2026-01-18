"""
Sample data and utility functions for the Learning Agent System.

This module provides sample checkpoints, materials, and utility functions
for demonstration and testing purposes.
"""

from typing import List
from .models import Checkpoint, Material, LearningPath, LearningPath

def create_sample_checkpoint() -> Checkpoint:
    """Create a sample learning checkpoint."""
    return {
        "id": "ml_fundamentals",
        "title": "Machine Learning Fundamentals",
        "description": "Understanding the core concepts of machine learning, including supervised learning, unsupervised learning, neural networks, and evaluation metrics.",
        "requirements": [
            "Explain the difference between supervised and unsupervised learning",
            "Understand how neural networks process information", 
            "Know key evaluation metrics for ML models",
            "Apply ML concepts to real-world scenarios"
        ]
    }

def create_multiple_checkpoints() -> List[Checkpoint]:
    """Create multiple checkpoint options for user selection."""
    checkpoints = [
        {
            "id": "ml_fundamentals",
            "title": "Machine Learning Fundamentals",
            "description": "Understanding the core concepts of machine learning, including supervised learning, unsupervised learning, neural networks, and evaluation metrics.",
            "requirements": [
                "Explain the difference between supervised and unsupervised learning",
                "Understand how neural networks process information", 
                "Know key evaluation metrics for ML models",
                "Apply ML concepts to real-world scenarios"
            ]
        },
        {
            "id": "deep_learning", 
            "title": "Deep Learning Essentials",
            "description": "Master neural networks, backpropagation, and deep learning architectures.",
            "requirements": [
                "Understand neural network architecture",
                "Explain backpropagation algorithm",
                "Identify different activation functions",
                "Describe CNN and RNN applications"
            ]
        },
        {
            "id": "data_science",
            "title": "Data Science Pipeline", 
            "description": "Learn data collection, cleaning, analysis, and visualization techniques.",
            "requirements": [
                "Understand data collection methods",
                "Explain data preprocessing techniques",
                "Perform exploratory data analysis",
                "Create effective data visualizations"
            ]
        },
        {
            "id": "nlp_basics",
            "title": "Natural Language Processing",
            "description": "Explore text processing, sentiment analysis, and language models.",
            "requirements": [
                "Understand text preprocessing",
                "Explain tokenization and stemming",
                "Perform sentiment analysis",
                "Describe language model applications"
            ]
        }
    ]
    return checkpoints

def create_sample_materials() -> List[Material]:
    """Create sample learning materials."""
    return [
        {
            "id": "ml_intro",
            "title": "Introduction to Machine Learning",
            "content": """Machine learning is a subset of artificial intelligence (AI) that enables computers to learn and make decisions from data without being explicitly programmed for every task. It represents a paradigm shift from traditional programming where we write specific instructions, to a system where algorithms improve their performance on a task through experience.

There are three main categories of machine learning:

1. Supervised Learning: This approach uses labeled training data to learn a mapping function from inputs to outputs. The algorithm learns from example input-output pairs and can then make predictions on new, unseen data. Common supervised learning algorithms include:
   - Linear Regression: Predicts continuous numerical values
   - Decision Trees: Creates a model that predicts target values by learning simple decision rules
   - Support Vector Machines: Finds optimal boundaries between different classes
   - Random Forest: Combines multiple decision trees for better accuracy

Applications of supervised learning include email spam detection, medical diagnosis, price prediction, and image classification.

2. Unsupervised Learning: This type works with data that has no labeled examples. The algorithm tries to find hidden patterns, structures, or relationships in the data without knowing the correct answers. Key techniques include:
   - Clustering (like K-means): Groups similar data points together
   - Dimensionality Reduction (like PCA): Reduces the number of features while preserving important information
   - Association Rules: Finds relationships between different items
   - Anomaly Detection: Identifies unusual patterns or outliers

Common applications include customer segmentation, market basket analysis, data compression, and fraud detection.

3. Reinforcement Learning: This approach learns through interaction with an environment, receiving rewards or penalties for actions taken. The algorithm learns to maximize cumulative rewards over time. It's particularly useful for sequential decision-making problems like game playing, robotics, autonomous vehicles, and resource management.""",
            "source": "ml_textbook"
        },
        {
            "id": "neural_networks",
            "title": "Neural Networks and Deep Learning",
            "content": """Neural networks are computing systems inspired by biological neural networks that constitute animal brains. They form the foundation of deep learning and have revolutionized many fields including computer vision, natural language processing, and speech recognition.

A neural network consists of interconnected nodes (neurons) organized in layers:

1. Input Layer: Receives the initial data (features)
2. Hidden Layers: Process the data through weighted connections and activation functions
3. Output Layer: Produces the final predictions or classifications

Each connection between neurons has an associated weight that determines the strength of the signal. During training, these weights are adjusted to minimize the difference between predicted and actual outcomes.

Key Concepts:

Activation Functions: Mathematical functions that determine whether a neuron should be activated. Common examples include:
- ReLU (Rectified Linear Unit): Outputs the input if positive, zero otherwise
- Sigmoid: Maps any real value to a value between 0 and 1
- Tanh: Maps values to a range between -1 and 1

Backpropagation: The learning algorithm that adjusts weights by propagating errors backward through the network. It uses calculus (chain rule) to compute gradients and update weights to minimize loss.

Deep Learning: Refers to neural networks with multiple hidden layers (typically more than 2-3 layers). Deep networks can learn complex, hierarchical representations of data, automatically discovering features that are useful for the task.

Applications of neural networks include:
- Image Recognition: Convolutional Neural Networks (CNNs) excel at processing visual data
- Natural Language Processing: Recurrent Neural Networks (RNNs) and Transformers handle sequential text data
- Speech Recognition: Converting audio signals to text
- Game Playing: Systems like AlphaGo use deep reinforcement learning
- Medical Diagnosis: Analyzing medical images and patient data""",
            "source": "deep_learning_guide"
        },
        {
            "id": "evaluation_metrics",
            "title": "Model Evaluation and Metrics", 
            "content": """Evaluating machine learning models is crucial for understanding their performance and ensuring they work well on new, unseen data. Different types of problems require different evaluation metrics.

For Classification Problems:

1. Accuracy: The proportion of correct predictions out of total predictions. While intuitive, it can be misleading with imbalanced datasets.
   Formula: (True Positives + True Negatives) / Total Predictions

2. Precision: Of all positive predictions, how many were actually correct? High precision means few false positives.
   Formula: True Positives / (True Positives + False Positives)

3. Recall (Sensitivity): Of all actual positive cases, how many did we correctly identify? High recall means few false negatives.
   Formula: True Positives / (True Positives + False Negatives)

4. F1-Score: Harmonic mean of precision and recall, providing a single score that balances both.
   Formula: 2 × (Precision × Recall) / (Precision + Recall)

5. ROC-AUC: Area Under the Receiver Operating Characteristic curve, measuring the model's ability to distinguish between classes across all classification thresholds.

For Regression Problems:

1. Mean Squared Error (MSE): Average of squared differences between predicted and actual values. Penalizes large errors more heavily.

2. Root Mean Squared Error (RMSE): Square root of MSE, expressed in the same units as the target variable.

3. Mean Absolute Error (MAE): Average of absolute differences between predicted and actual values. Less sensitive to outliers than MSE.

4. R-squared (Coefficient of Determination): Proportion of variance in the target variable explained by the model. Values range from 0 to 1, where 1 indicates perfect fit.

Cross-Validation: A technique to assess how well a model generalizes to unseen data by splitting the dataset into multiple folds, training on some folds and testing on others, then averaging the results.

The choice of metric depends on the specific problem, business requirements, and the cost of different types of errors. For example, in medical diagnosis, false negatives (missing a disease) might be more costly than false positives (incorrectly diagnosing a disease).""",
            "source": "evaluation_handbook"
        }
    ]

def create_learning_paths():
    """Create multiple complete learning paths."""
    from .models import LearningPath
    
    # NLP Learning Path
    nlp_path = {
        "id": "nlp_complete",
        "title": "Natural Language Processing Mastery",
        "description": "Complete NLP learning journey from basics to advanced applications", 
        "checkpoints": [
            {
                "id": "nlp_basics",
                "title": "NLP Fundamentals",
                "description": "Understanding core NLP concepts and text preprocessing",
                "requirements": [
                    "Understand text preprocessing",
                    "Explain tokenization and stemming", 
                    "Identify common NLP tasks"
                ]
            },
            {
                "id": "nlp_intermediate", 
                "title": "Sentiment Analysis",
                "description": "Building sentiment analysis systems",
                "requirements": [
                    "Perform sentiment analysis",
                    "Evaluate sentiment models", 
                    "Handle different text types"
                ]
            },
            {
                "id": "nlp_advanced",
                "title": "Language Models",
                "description": "Understanding and applying language models",
                "requirements": [
                    "Describe language model applications",
                    "Compare different model architectures",
                    "Implement language model solutions"
                ]
            }
        ]
    }
    
    # Machine Learning Path
    ml_path = {
        "id": "ml_complete",
        "title": "Machine Learning Mastery", 
        "description": "Complete ML journey from fundamentals to advanced techniques",
        "checkpoints": [
            {
                "id": "ml_fundamentals",
                "title": "ML Fundamentals",
                "description": "Core machine learning concepts",
                "requirements": [
                    "Explain supervised vs unsupervised learning",
                    "Understand basic algorithms",
                    "Know evaluation metrics"
                ]
            },
            {
                "id": "ml_algorithms",
                "title": "ML Algorithms", 
                "description": "Specific machine learning algorithms",
                "requirements": [
                    "Implement classification algorithms",
                    "Apply regression techniques",
                    "Use clustering methods"
                ]
            },
            {
                "id": "ml_optimization",
                "title": "Model Optimization",
                "description": "Advanced model tuning and optimization",
                "requirements": [
                    "Perform hyperparameter tuning",
                    "Apply cross-validation", 
                    "Optimize model performance"
                ]
            }
        ]
    }
    
    return [nlp_path, ml_path]

