import numpy as np
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Repository
from .serializers import RepositorySerializer

# Lazy singleton — avoids loading PyTorch/CUDA at import time
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Force CPU to avoid CUDA fork issues
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        except ImportError:
            _embedding_model = False
    return _embedding_model if _embedding_model else None

def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

class RepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer

    @action(detail=False, methods=['get'])
    def top(self, request):
        limit = min(int(request.query_params.get('limit', 500)), 500)
        top_repos = Repository.objects.order_by('-final_score')[:limit]
        serializer = self.get_serializer(top_repos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        query = request.query_params.get('query', '')
        language = request.query_params.get('language')
        limit = min(int(request.query_params.get('limit', 50)), 500)

        repos = Repository.objects.all()

        if language:
            repos = repos.filter(language__iexact=language)

        repos = list(repos)

        if query and get_embedding_model():
            query_embedding = get_embedding_model().encode(query)

            scored_repos = []
            for repo in repos:
                if repo.embedding:
                    sim = cosine_similarity(query_embedding, np.array(repo.embedding))
                    scored_repos.append((sim, repo))
                else:
                    scored_repos.append((-1.0, repo))

            scored_repos.sort(key=lambda x: x[0], reverse=True)
            repos = [repo for sim, repo in scored_repos][:limit]
        else:
            repos.sort(key=lambda x: x.final_score, reverse=True)
            repos = repos[:limit]

        serializer = self.get_serializer(repos, many=True)
        return Response(serializer.data)
