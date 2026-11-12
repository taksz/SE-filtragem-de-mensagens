"""
Sistema Especialista para Filtragem de Mensagens Indesejadas (Spam/Phishing).

Módulo simbólico: base de conhecimento, extrator de fatos e motor de inferência
com encadeamento progressivo (forward chaining).
"""

from expert_system.knowledge_base import KnowledgeBase, Rule
from expert_system.fact_extractor import FactExtractor
from expert_system.inference_engine import InferenceEngine

__all__ = ["KnowledgeBase", "Rule", "FactExtractor", "InferenceEngine"]
