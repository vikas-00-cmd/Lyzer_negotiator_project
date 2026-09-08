import pytest
from abc import ABC
from app.agents.base import BaseAgent


def test_base_agent_is_abstract():
    assert issubclass(BaseAgent, ABC)


def test_base_agent_cannot_instantiate():
    with pytest.raises(TypeError):
        BaseAgent("BUYER")


def test_base_agent_requires_generate_offer():
    class IncompleteAgent(BaseAgent):
        pass

    with pytest.raises(TypeError):
        IncompleteAgent("BUYER")


def test_base_agent_implements_interface():
    class CompleteAgent(BaseAgent):
        def generate_offer(self, state):
            pass

    agent = CompleteAgent("BUYER")
    assert agent.agent_type == "BUYER"
