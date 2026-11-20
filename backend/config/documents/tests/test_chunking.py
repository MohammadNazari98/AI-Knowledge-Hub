import pytest
from documents.services.chunking import TextChunker






def test_split_text_returns_chunks():
    text_chunker = TextChunker(10, 3)
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = text_chunker.split_text(text)
    
    assert chunks == ["abcdefghij","hijklmnopq","opqrstuvwx","vwxyz"]
    
def test_empty_text_returns_empty_list():
    text_chunker = TextChunker(10, 3)
    
    text_chunker.split_text("   ") == []
    text_chunker.split_text(" ") == []

@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    [
        (-5, -2),
        (0, 5),
    ]
)
def test_chunk_size_cannot_be_lower_than_zero_and_must_return_value_error(chunk_size, chunk_overlap):
    with pytest.raises(ValueError):
        TextChunker(chunk_size, chunk_overlap)

def test_short_text_returns_one_chunks():
    chunker = TextChunker(100, 5)
    assert chunker.split_text("Hello world!") == ["Hello world!"]
    
@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    [
        (10, -2),
        (5, -1)
    ]
)       
def test_chunk_overlap_cannot_be_lower_than_zero_and_must_return_value_error(chunk_size, chunk_overlap):
    with pytest.raises(ValueError):
        TextChunker(chunk_size, chunk_overlap)
        

def test_chunk_size_cannot_be_lower_than_chunk_overlap_and_must_return_value_error():
    
    with pytest.raises(ValueError):
        TextChunker(300, 320)