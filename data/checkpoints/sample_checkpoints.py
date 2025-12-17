"""
Sample checkpoints for testing the Milestone 1 workflow.
These represent different subjects and difficulty levels for comprehensive testing.
"""

from datetime import datetime
from src.models import (
    Checkpoint, 
    LearningObjective, 
    SuccessCriteria,
    DifficultyLevel,
    QuestionType
)


def create_sample_checkpoints():
    """Create a variety of sample checkpoints for testing."""
    
    checkpoints = []
    
    # 1. Basic Programming Concepts
    checkpoint1 = Checkpoint(
        title="Python Variables and Data Types",
        description="Understanding fundamental concepts of variables and data types in Python programming",
        objectives=[
            LearningObjective(
                title="Variable Assignment",
                description="Understand how to create and assign values to variables in Python",
                keywords=["variables", "assignment", "naming", "python"],
                importance_weight=1.5
            ),
            LearningObjective(
                title="Data Types",
                description="Learn about basic data types: int, float, string, boolean",
                keywords=["data types", "int", "float", "string", "boolean"],
                importance_weight=1.0
            ),
            LearningObjective(
                title="Type Conversion",
                description="Convert between different data types using built-in functions",
                keywords=["type conversion", "casting", "str()", "int()", "float()"],
                importance_weight=0.8
            )
        ],
        difficulty_level=DifficultyLevel.BEGINNER,
        question_type=QuestionType.MIXED,
        estimated_duration_minutes=20,
        topic_keywords=["python", "variables", "data types", "programming", "basics"],
        context_requirements="Basic programming concepts and Python syntax examples"
    )
    checkpoints.append(checkpoint1)
    
    # 2. Mathematics - Calculus
    checkpoint2 = Checkpoint(
        title="Introduction to Derivatives",
        description="Understanding the concept of derivatives and basic differentiation rules",
        objectives=[
            LearningObjective(
                title="Derivative Definition",
                description="Understand the mathematical definition of a derivative as a limit",
                keywords=["derivative", "limit", "definition", "calculus"],
                importance_weight=2.0
            ),
            LearningObjective(
                title="Power Rule",
                description="Apply the power rule for differentiating polynomial functions",
                keywords=["power rule", "differentiation", "polynomial"],
                importance_weight=1.5
            ),
            LearningObjective(
                title="Geometric Interpretation",
                description="Understand derivatives as slopes of tangent lines to curves",
                keywords=["slope", "tangent line", "geometric", "interpretation"],
                importance_weight=1.0
            )
        ],
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        question_type=QuestionType.OPEN_ENDED,
        estimated_duration_minutes=35,
        topic_keywords=["calculus", "derivatives", "differentiation", "mathematics"],
        context_requirements="Mathematical explanations with examples and visual representations"
    )
    checkpoints.append(checkpoint2)
    
    # 3. Physics - Mechanics
    checkpoint3 = Checkpoint(
        title="Newton's Laws of Motion",
        description="Understanding and applying Newton's three fundamental laws of motion",
        objectives=[
            LearningObjective(
                title="First Law (Inertia)",
                description="Understand that objects at rest stay at rest unless acted upon by force",
                keywords=["first law", "inertia", "rest", "motion"],
                importance_weight=1.0
            ),
            LearningObjective(
                title="Second Law (F=ma)",
                description="Apply the relationship between force, mass, and acceleration",
                keywords=["second law", "force", "mass", "acceleration", "F=ma"],
                importance_weight=2.0
            ),
            LearningObjective(
                title="Third Law (Action-Reaction)",
                description="Understand that every action has an equal and opposite reaction",
                keywords=["third law", "action", "reaction", "equal", "opposite"],
                importance_weight=1.5
            )
        ],
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        question_type=QuestionType.MIXED,
        estimated_duration_minutes=30,
        topic_keywords=["physics", "newton", "laws", "motion", "mechanics", "force"],
        context_requirements="Physics concepts with real-world examples and mathematical applications"
    )
    checkpoints.append(checkpoint3)
    
    # 4. History - World War II
    checkpoint4 = Checkpoint(
        title="Causes of World War II",
        description="Analyzing the political, economic, and social factors that led to World War II",
        objectives=[
            LearningObjective(
                title="Treaty of Versailles Impact",
                description="Understand how the Treaty of Versailles contributed to German resentment",
                keywords=["treaty", "versailles", "germany", "resentment", "wwi"],
                importance_weight=1.5
            ),
            LearningObjective(
                title="Economic Factors",
                description="Analyze the role of the Great Depression in destabilizing Europe",
                keywords=["great depression", "economic", "instability", "europe"],
                importance_weight=1.0
            ),
            LearningObjective(
                title="Rise of Fascism",
                description="Examine the rise of fascist movements in Germany, Italy, and Japan",
                keywords=["fascism", "hitler", "mussolini", "nazism", "authoritarianism"],
                importance_weight=2.0
            )
        ],
        difficulty_level=DifficultyLevel.ADVANCED,
        question_type=QuestionType.OPEN_ENDED,
        estimated_duration_minutes=40,
        topic_keywords=["world war 2", "history", "causes", "politics", "economics"],
        context_requirements="Historical analysis with primary sources and multiple perspectives"
    )
    checkpoints.append(checkpoint4)
    
    # 5. Biology - Cell Structure
    checkpoint5 = Checkpoint(
        title="Cell Membrane and Transport",
        description="Understanding cell membrane structure and mechanisms of molecular transport",
        objectives=[
            LearningObjective(
                title="Membrane Structure",
                description="Understand the phospholipid bilayer and fluid mosaic model",
                keywords=["phospholipid", "bilayer", "fluid mosaic", "membrane"],
                importance_weight=1.5
            ),
            LearningObjective(
                title="Passive Transport",
                description="Explain diffusion, osmosis, and facilitated diffusion",
                keywords=["diffusion", "osmosis", "passive transport", "gradient"],
                importance_weight=1.0
            ),
            LearningObjective(
                title="Active Transport",
                description="Understand energy-requiring transport mechanisms",
                keywords=["active transport", "ATP", "pump", "energy"],
                importance_weight=1.2
            )
        ],
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        question_type=QuestionType.MULTIPLE_CHOICE,
        estimated_duration_minutes=25,
        topic_keywords=["biology", "cell", "membrane", "transport", "molecular"],
        context_requirements="Biological concepts with diagrams and molecular explanations"
    )
    checkpoints.append(checkpoint5)
    
    # 6. Computer Science - Algorithms
    checkpoint6 = Checkpoint(
        title="Big O Notation and Algorithm Analysis",
        description="Understanding time complexity analysis and Big O notation for algorithm efficiency",
        objectives=[
            LearningObjective(
                title="Big O Definition",
                description="Understand what Big O notation represents in algorithm analysis",
                keywords=["big o", "time complexity", "algorithm", "analysis"],
                importance_weight=2.0
            ),
            LearningObjective(
                title="Common Complexities",
                description="Recognize O(1), O(n), O(n²), O(log n) patterns",
                keywords=["constant", "linear", "quadratic", "logarithmic", "complexity"],
                importance_weight=1.5
            ),
            LearningObjective(
                title="Analysis Examples",
                description="Analyze time complexity of simple algorithms and loops",
                keywords=["analysis", "loops", "examples", "calculation"],
                importance_weight=1.0
            )
        ],
        difficulty_level=DifficultyLevel.ADVANCED,
        question_type=QuestionType.MIXED,
        estimated_duration_minutes=45,
        topic_keywords=["computer science", "algorithms", "big o", "complexity", "analysis"],
        context_requirements="Technical explanations with code examples and mathematical notation"
    )
    checkpoints.append(checkpoint6)
    
    # 7. Chemistry - Basic Concepts
    checkpoint7 = Checkpoint(
        title="Atomic Structure and Periodic Table",
        description="Understanding atomic structure and organization of the periodic table",
        objectives=[
            LearningObjective(
                title="Atomic Components",
                description="Identify protons, neutrons, and electrons in atomic structure",
                keywords=["proton", "neutron", "electron", "nucleus", "atomic"],
                importance_weight=1.0
            ),
            LearningObjective(
                title="Electron Configuration",
                description="Understand electron shells and orbital arrangements",
                keywords=["electron", "shells", "orbitals", "configuration"],
                importance_weight=1.5
            ),
            LearningObjective(
                title="Periodic Trends",
                description="Recognize patterns in atomic radius, ionization energy, and electronegativity",
                keywords=["periodic", "trends", "radius", "ionization", "electronegativity"],
                importance_weight=1.8
            )
        ],
        difficulty_level=DifficultyLevel.BEGINNER,
        question_type=QuestionType.MULTIPLE_CHOICE,
        estimated_duration_minutes=30,
        topic_keywords=["chemistry", "atomic", "structure", "periodic table", "elements"],
        context_requirements="Chemistry fundamentals with visual representations of atomic models"
    )
    checkpoints.append(checkpoint7)
    
    # 8. Economics - Supply and Demand
    checkpoint8 = Checkpoint(
        title="Market Equilibrium and Price Determination",
        description="Understanding how supply and demand interact to determine market prices",
        objectives=[
            LearningObjective(
                title="Supply Curve",
                description="Understand the relationship between price and quantity supplied",
                keywords=["supply", "curve", "price", "quantity", "producers"],
                importance_weight=1.0
            ),
            LearningObjective(
                title="Demand Curve",
                description="Analyze the relationship between price and quantity demanded",
                keywords=["demand", "curve", "consumers", "price", "quantity"],
                importance_weight=1.0
            ),
            LearningObjective(
                title="Market Equilibrium",
                description="Identify equilibrium price and quantity where supply meets demand",
                keywords=["equilibrium", "intersection", "market", "clearing"],
                importance_weight=2.0
            )
        ],
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        question_type=QuestionType.MIXED,
        estimated_duration_minutes=35,
        topic_keywords=["economics", "supply", "demand", "market", "equilibrium", "price"],
        context_requirements="Economic theory with graphs and real-world market examples"
    )
    checkpoints.append(checkpoint8)
    
    return checkpoints


def get_checkpoint_by_title(title: str):
    """Get a specific checkpoint by its title."""
    checkpoints = create_sample_checkpoints()
    for checkpoint in checkpoints:
        if checkpoint.title == title:
            return checkpoint
    return None


def get_checkpoints_by_difficulty(difficulty: DifficultyLevel):
    """Get checkpoints filtered by difficulty level."""
    checkpoints = create_sample_checkpoints()
    return [cp for cp in checkpoints if cp.difficulty_level == difficulty]


def get_checkpoint_titles():
    """Get list of all checkpoint titles for easy reference."""
    checkpoints = create_sample_checkpoints()
    return [cp.title for cp in checkpoints]