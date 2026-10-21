from documents.models import DocumentChunk, Document
from django.db.models import Q, Case, IntegerField, When, Value
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