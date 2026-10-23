import pytest
import torch
from types import SimpleNamespace
from documents.services.embedding import EmbeddingService


@pytest.fixture
def embedding_service():
    embedding_service = EmbeddingService()
    return embedding_service

def test_embedding_get_text_and_return_embedding_dim_shape_correctly(embedding_service):
    text = "هوش مصنوعی به تشخیص بیماری کمک میکند."
    
    embed = embedding_service.get_embedding(text)
    
    assert embed.shape == torch.Size([1, 384])

def test_embedding_normalize_vector_return_1dot0_correctly(embedding_service):
    text = "هوش مصنوعی به تشخیص بیماری کمک میکند."
        
    embed = embedding_service.get_embedding(text)
    
    l2_norm = torch.linalg.vector_norm(embed, dim=1).item()
    
    assert pytest.approx(1.0) == l2_norm
    
def test_embedding_must_be_valid_finite_correctly(embedding_service):
    text = "هوش مصنوعی به تشخیص بیماری کمک میکند."
            
    embed = embedding_service.get_embedding(text)
    
    assert torch.isfinite(embed).all().item()
    
def test_embedding_must_use_passage_prefix_by_default(embedding_service, monkeypatch: pytest.MonkeyPatch):
    text = "هوش مصنوعی"
    received_text = []

    def fake_tokenize(text: str):
        received_text.append(text)

        return {
            "input_ids": torch.tensor([[1, 2]]),
            "attention_mask": torch.tensor([[1, 1]]),
        }

    def fake_model(**tokens):
        return SimpleNamespace(
            last_hidden_state=torch.ones((1, 2, 384))
        )

    monkeypatch.setattr(
        embedding_service,
        "tokenize",
        fake_tokenize,
    )

    monkeypatch.setattr(
        embedding_service,
        "model",
        fake_model,
    )

    embedding_service.get_embedding(text)

    assert received_text == ["passage: هوش مصنوعی"]

def test_embedding_must_raise_value_error_for_none(embedding_service):
    with pytest.raises(ValueError):
        embedding_service.get_embedding(None)

def test_embedding_must_raise_value_error_for_empty_text(embedding_service):
    with pytest.raises(ValueError):
            embed = embedding_service.get_embedding("")

def test_embedding_must_raise_value_error_for_whitespace_text(embedding_service):
    with pytest.raises(ValueError):
        embedding_service.get_embedding("   ")