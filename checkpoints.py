# checkpoints.py
from dataclasses import dataclass
from typing import List

@dataclass
class Checkpoint:
    id: int
    topic: str
    objectives: List[str]
    success_criteria: str

CHECKPOINTS: List[Checkpoint] = [
    Checkpoint(
        id=1,
        topic="Introduction to Cybersecurity",
        objectives=[
            "Understand what cybersecurity means",
            "Know why cybersecurity is important",
            "Identify basic cyber threats"
        ],
        success_criteria="Can explain cybersecurity and common threats."
    ),
    Checkpoint(
        id=2,
        topic="Threats and Vulnerabilities",
        objectives=[
            "Understand the difference between threats and vulnerabilities",
            "Recognize malware, phishing, ransomware"
        ],
        success_criteria="Can classify and explain threat types."
    ),
    Checkpoint(
        id=3,
        topic="Authentication and Authorization",
        objectives=[
            "Understand authentication vs authorization",
            "Know MFA, biometrics, passwords"
        ],
        success_criteria="Can explain auth methods with examples."
    ),
    Checkpoint(
        id=4,
        topic="Network Security Basics",
        objectives=[
            "Understand firewalls, proxies, VPNs",
            "Know secure network architecture basics"
        ],
        success_criteria="Can explain network security components."
    ),
    Checkpoint(
        id=5,
        topic="Cryptography Basics",
        objectives=[
            "Understand encryption and decryption",
            "Know symmetric vs asymmetric keys"
        ],
        success_criteria="Can explain how encryption protects data."
    ),
]
