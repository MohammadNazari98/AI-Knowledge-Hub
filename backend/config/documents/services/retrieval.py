from documents.models import DocumentChunk, Document
from django.db.models import Q, Case, IntegerField, When, Value
from pgvector.django import CosineDistance
from documents.services.embedding import EmbeddingService
import re


class KeywordRetriever:
    
    
    def search(self, query: str, knowledge_id: int, limit: int= 5):
        terms = list(
            dict.fromkeys(
                re.findall(r"\w+", query.casefold())
            )
        )
        
        if not terms or limit <= 0:
            return DocumentChunk.objects.none()
        
        matching_terms = Q()
        score = Value(0, output_field=IntegerField())
        
        for term in terms:
            matching_terms |= Q(content__icontains=term)
            score += Case(
                When(content__icontains=term, then=Value(1)), 
                default=Value(0),
                output_field=IntegerField()
            )
            
        return DocumentChunk.objects.filter(
            document__knowledge_base_id = knowledge_id,
            document__status = Document.Status.PROCESSED,
        ).filter(matching_terms).annotate(score=score).select_related("document").order_by("-score","document_id", "index")[:limit]
        
class SemanticRetriever:
    def __init__(self, embedding_service: EmbeddingService=None):
        self.embedding_service = (
            embedding_service if embedding_service is not None else EmbeddingService()
        )
        
    def search(self, query: str, knowledge_id: int, limit: int= 5):
        if not query or not query.strip() or limit <= 0:
            return DocumentChunk.objects.none()

        query_embedding = self.embedding_service.get_embedding(text=query, prefix="query: ").squeeze(0).tolist()

        return DocumentChunk.objects.filter(
            document__knowledge_base_id = knowledge_id,
            document__status = Document.Status.PROCESSED,
            embedding__isnull = False
        ).annotate(distance=CosineDistance("embedding", query_embedding)).select_related("document").order_by("distance", "document_id", "index")[:limit]