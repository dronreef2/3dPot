"""
Routers FastAPI - Marketplace Platform (Sprint 6+)
=================================================

Rotas para marketplace de modelos 3D, incluindo:
- Listagens de produtos (MarketplaceListing)
- Processamento de transações (Transaction)
- Sistema de avaliações (Review)
- Gerenciamento de licenças (License)
- Wishlist e promoções

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
Sprint 8: RBAC integration for seller and admin permissions
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import stripe

from ..database import get_db
from ..core.config import settings
from ..services.marketplace_service import MarketplaceService
from ..middleware.auth import get_current_user
from ..models import User

# Sprint 8: Import RBAC helpers
from backend.core.authorization import (
    Role, Permission, require_role, has_role, has_permission
)

router = APIRouter()

# Instância do serviço
marketplace_service = MarketplaceService()

# =============================================================================
# ROTAS DE CATEGORIAS
# =============================================================================

@router.post("/categories/", response_model=dict)
async def create_category(
    category_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar nova categoria (apenas administradores)
    Sprint 8: Protected with ADMIN role requirement
    """
    # Sprint 8: Use RBAC instead of is_superuser check
    user_role = getattr(current_user, 'role', Role.USER)
    if not has_role(user_role, [Role.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied. Admin role required."
        )
    
    try:
        category = await marketplace_service.create_category(db, category_data)
        return {
            "success": True,
            "message": "Categoria criada com sucesso",
            "data": {
                "id": str(category.id),
                "nome": category.nome,
                "slug": category.slug,
                "categoria_pai_id": str(category.categoria_pai_id) if category.categoria_pai_id else None,
                "nivel_hierarquia": category.nivel_hierarquia
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/categories/", response_model=dict)
async def list_categories(
    active_only: bool = Query(True, description="Apenas categorias ativas"),
    include_children: bool = Query(True, description="Incluir subcategorias"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar categorias"""
    try:
        categories = await marketplace_service.list_categories(db, active_only, include_children)
        return {
            "success": True,
            "data": {
                "categories": [
                    {
                        "id": str(c.id),
                        "nome": c.nome,
                        "slug": c.slug,
                        "descricao": c.descricao,
                        "categoria_pai_id": str(c.categoria_pai_id) if c.categoria_pai_id else None,
                        "nivel_hierarquia": c.nivel_hierarquia,
                        "ativa": c.ativa,
                        "ordem_exibicao": c.ordem_exibicao,
                        "icone": c.icone
                    }
                    for c in categories
                ],
                "total": len(categories)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE TAGS
# =============================================================================

@router.post("/tags/", response_model=dict)
async def create_tag(
    tag_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova tag (apenas administradores)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        tag = await marketplace_service.create_tag(db, tag_data)
        return {
            "success": True,
            "message": "Tag criada com sucesso",
            "data": {
                "id": str(tag.id),
                "nome": tag.nome,
                "slug": tag.slug,
                "uso_count": tag.uso_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tags/search/", response_model=dict)
async def search_tags(
    q: str = Query(..., description="Termo de busca"),
    limit: int = Query(20, description="Limite de resultados"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar tags"""
    try:
        tags = await marketplace_service.search_tags(db, q, limit)
        return {
            "success": True,
            "data": {
                "tags": [
                    {
                        "id": str(tag.id),
                        "nome": tag.nome,
                        "slug": tag.slug,
                        "uso_count": tag.uso_count
                    }
                    for tag in tags
                ],
                "total": len(tags)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE LISTAGENS
# =============================================================================

@router.post("/listings/", response_model=dict)
async def create_listing(
    titulo: str = Form(..., description="Título da listagem"),
    category_id: UUID = Form(..., description="ID da categoria"),
    arquivo_modelo: UploadFile = File(..., description="Arquivo do modelo 3D"),
    descricao_curta: Optional[str] = Form(None, description="Descrição curta"),
    descricao_completa: Optional[str] = Form(None, description="Descrição completa"),
    preco_original: float = Form(..., description="Preço original"),
    formato_arquivo: str = Form(..., description="Formato do arquivo (ex: .stl)"),
    tags: Optional[List[str]] = Form(None, description="Tags do produto"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova listagem"""
    try:
        # Salvar arquivo temporário
        upload_dir = "/tmp/uploads/marketplace"
        import os
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, arquivo_modelo.filename)
        with open(file_path, "wb") as buffer:
            content = await arquivo_modelo.read()
            buffer.write(content)
        
        # Preparar dados da listagem
        listing_data = {
            "titulo": titulo,
            "category_id": str(category_id),
            "descricao_curta": descricao_curta,
            "descricao_completa": descricao_completa,
            "preco_original": preco_original,
            "arquivo_modelo_path": file_path,
            "formato_arquivo": formato_arquivo,
            "tags": tags or []
        }
        
        listing = await marketplace_service.create_listing(db, current_user.id, listing_data)
        return {
            "success": True,
            "message": "Listagem criada com sucesso",
            "data": {
                "id": str(listing.id),
                "titulo": listing.titulo,
                "slug": listing.slug,
                "status": listing.status,
                "preco_original": float(listing.preco_original),
                "arquivo_tamanho_mb": listing.arquivo_tamanho_mb
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/listings/", response_model=dict)
async def list_listings(
    category_id: Optional[UUID] = Query(None, description="Filtrar por categoria"),
    price_min: Optional[float] = Query(None, description="Preço mínimo"),
    price_max: Optional[float] = Query(None, description="Preço máximo"),
    seller_id: Optional[UUID] = Query(None, description="Filtrar por vendedor"),
    featured_only: bool = Query(False, description="Apenas listagens em destaque"),
    premium_only: bool = Query(False, description="Apenas listagens premium"),
    search_query: Optional[str] = Query(None, description="Termo de busca"),
    sort_by: str = Query("created_desc", description="Ordenação (price_asc, price_desc, rating, popularity, created_desc)"),
    limit: int = Query(20, description="Limite de resultados"),
    offset: int = Query(0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar listagens com filtros"""
    try:
        # Preparar filtros
        filters = {}
        if category_id:
            filters['category_id'] = str(category_id)
        if price_min is not None:
            filters['price_min'] = price_min
        if price_max is not None:
            filters['price_max'] = price_max
        if seller_id:
            filters['seller_id'] = str(seller_id)
        if featured_only:
            filters['featured_only'] = True
        if premium_only:
            filters['premium_only'] = True
        if search_query:
            filters['search_query'] = search_query
        
        listings, total = await marketplace_service.list_listings(db, filters, limit, offset, sort_by)
        
        return {
            "success": True,
            "data": {
                "listings": [
                    {
                        "id": str(l.id),
                        "titulo": l.titulo,
                        "slug": l.slug,
                        "descricao_curta": l.descricao_curta,
                        "preco_original": float(l.preco_original),
                        "preco_promocional": float(l.preco_promocional) if l.preco_promocional else None,
                        "moeda": l.moeda,
                        "rating_medio": l.rating_medio,
                        "total_reviews": l.total_reviews,
                        "downloads_count": l.downloads_count,
                        "vendas_count": l.vendas_count,
                        "featured": l.featured,
                        "premium": l.premium,
                        "categoria": {
                            "id": str(l.category.id),
                            "nome": l.category.nome
                        } if l.category else None,
                        "vendedor": {
                            "id": str(l.seller.id),
                            "username": l.seller.username,
                            "full_name": l.seller.full_name
                        },
                        "tags": [tag.nome for tag in l.tags],
                        "created_at": l.created_at.isoformat()
                    }
                    for l in listings
                ],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/listings/search/", response_model=dict)
async def search_listings(
    q: str = Query(..., description="Termo de busca"),
    limit: int = Query(20, description="Limite de resultados"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar listagens"""
    try:
        filters = {"search_query": q}
        listings, total = await marketplace_service.list_listings(db, filters, limit, 0, "relevance")
        
        return {
            "success": True,
            "data": {
                "listings": [
                    {
                        "id": str(l.id),
                        "titulo": l.titulo,
                        "slug": l.slug,
                        "descricao_curta": l.descricao_curta,
                        "preco_original": float(l.preco_original),
                        "rating_medio": l.rating_medio,
                        "categoria": l.category.nome if l.category else None,
                        "tags": [tag.nome for tag in l.tags]
                    }
                    for l in listings
                ],
                "total": total
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/listings/{listing_id}", response_model=dict)
async def get_listing(
    listing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes da listagem"""
    try:
        listing = await marketplace_service.get_listing(db, listing_id, None, current_user.id)
        
        if not listing:
            raise HTTPException(status_code=404, detail="Listagem não encontrada")
        
        return {
            "success": True,
            "data": {
                "id": str(listing.id),
                "titulo": listing.titulo,
                "slug": listing.slug,
                "descricao_curta": listing.descricao_curta,
                "descricao_completa": listing.descricao_completa,
                "preco_original": float(listing.preco_original),
                "preco_promocional": float(listing.preco_promocional) if listing.preco_promocional else None,
                "moeda": listing.moeda,
                "arquivo_tamanho_mb": listing.arquivo_tamanho_mb,
                "formato_arquivo": listing.formato_arquivo,
                "software_compativel": listing.software_compativel,
                "software_necessario": listing.software_necessario,
                "dimensoes": {
                    "x": listing.dimensao_x,
                    "y": listing.dimensao_y,
                    "z": listing.dimensao_z,
                    "unidade": listing.unidade_medida
                },
                "volume_estimado_cm3": listing.volume_estimado_cm3,
                "peso_estimado_g": listing.peso_estimado_g,
                "complexidade": listing.complexidade,
                "download_licenca": listing.download_licenca,
                "permissoes_uso": listing.permissoes_uso,
                "rating_medio": listing.rating_medio,
                "total_reviews": listing.total_reviews,
                "visualizacoes_count": listing.visualizacoes_count,
                "downloads_count": listing.downloads_count,
                "vendas_count": listing.vendas_count,
                "featured": listing.featured,
                "premium": listing.premium,
                "categoria": {
                    "id": str(listing.category.id),
                    "nome": listing.category.nome,
                    "slug": listing.category.slug
                } if listing.category else None,
                "vendedor": {
                    "id": str(listing.seller.id),
                    "username": listing.seller.username,
                    "full_name": listing.seller.full_name,
                    "company": listing.seller.company
                },
                "tags": [tag.nome for tag in listing.tags],
                "reviews": [
                    {
                        "rating_geral": review.rating_geral,
                        "comentario": review.comentario,
                        "buyer": {
                            "username": review.buyer.username,
                            "full_name": review.buyer.full_name
                        },
                        "created_at": review.created_at.isoformat()
                    }
                    for review in listing.reviews[:5]  # Últimas 5 avaliações
                ],
                "timestamps": {
                    "created_at": listing.created_at.isoformat(),
                    "updated_at": listing.updated_at.isoformat(),
                    "published_at": listing.published_at.isoformat() if listing.published_at else None
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/listings/{listing_id}", response_model=dict)
async def update_listing(
    listing_id: UUID,
    listing_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar listagem"""
    try:
        listing = await marketplace_service.update_listing(db, listing_id, current_user.id, listing_data)
        return {
            "success": True,
            "message": "Listagem atualizada com sucesso",
            "data": {
                "id": str(listing.id),
                "titulo": listing.titulo,
                "status": listing.status,
                "updated_at": listing.updated_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/listings/{listing_id}/publish", response_model=dict)
async def publish_listing(
    listing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publicar listagem (enviar para análise)"""
    try:
        success = await marketplace_service.publish_listing(db, listing_id, current_user.id)
        return {
            "success": success,
            "message": "Listagem enviada para análise"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE TRANSAÇÕES E PAGAMENTOS
# =============================================================================

@router.post("/transactions/", response_model=dict)
async def create_transaction(
    transaction_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova transação"""
    try:
        transaction = await marketplace_service.create_transaction(
            db, current_user.id, transaction_data['listing_id'], transaction_data
        )
        return {
            "success": True,
            "message": "Transação criada com sucesso",
            "data": {
                "transaction_id": str(transaction.id),
                "numero_pedido": transaction.numero_pedido,
                "valor_total": float(transaction.valor_total),
                "moeda": transaction.moeda,
                "status": transaction.status,
                "requires_payment": transaction.valor_total > 0,
                "stripe_payment_intent_id": transaction.stripe_payment_intent_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/transactions/{transaction_id}/process-payment", response_model=dict)
async def process_payment(
    transaction_id: UUID,
    payment_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Processar pagamento via Stripe"""
    try:
        transaction = await marketplace_service.process_payment(
            db, transaction_id, payment_data['payment_method_id'], current_user.id
        )
        
        return {
            "success": True,
            "message": "Pagamento processado com sucesso",
            "data": {
                "transaction_id": str(transaction.id),
                "status": transaction.status,
                "processed_at": transaction.processed_at.isoformat() if transaction.processed_at else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhooks/stripe", response_model=dict)
async def stripe_webhook(
    webhook_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Webhook do Stripe para processar eventos de pagamento"""
    try:
        success = await marketplace_service.handle_stripe_webhook(db, webhook_data)
        return {
            "success": success,
            "message": "Webhook processado com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE AVALIAÇÕES
# =============================================================================

@router.post("/listings/{listing_id}/reviews/", response_model=dict)
async def create_review(
    listing_id: UUID,
    review_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar avaliação de produto"""
    try:
        review = await marketplace_service.create_review(db, listing_id, current_user.id, review_data)
        return {
            "success": True,
            "message": "Avaliação criada com sucesso",
            "data": {
                "review_id": str(review.id),
                "rating_geral": review.rating_geral,
                "comentario": review.comentario,
                "created_at": review.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/listings/{listing_id}/reviews/", response_model=dict)
async def get_reviews(
    listing_id: UUID,
    limit: int = Query(20, description="Limite de resultados"),
    offset: int = Query(0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter avaliações da listagem"""
    try:
        reviews, total = await marketplace_service.get_reviews(db, listing_id, limit, offset)
        return {
            "success": True,
            "data": {
                "reviews": [
                    {
                        "id": str(r.id),
                        "rating_geral": r.rating_geral,
                        "rating_qualidade": r.rating_qualidade,
                        "rating_facilidade_uso": r.rating_facilidade_uso,
                        "rating_documentacao": r.rating_documentacao,
                        "rating_suporte": r.rating_suporte,
                        "comentario": r.comentario,
                        "titulo": r.titulo,
                        "helpful_votes": r.helpful_votes,
                        "buyer": {
                            "username": r.buyer.username,
                            "full_name": r.buyer.full_name
                        },
                        "created_at": r.created_at.isoformat()
                    }
                    for r in reviews
                ],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE WISHLIST
# =============================================================================

@router.post("/wishlist/", response_model=dict)
async def add_to_wishlist(
    wishlist_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adicionar item à wishlist"""
    try:
        wishlist_item = await marketplace_service.add_to_wishlist(
            db, current_user.id, wishlist_data['listing_id'], wishlist_data.get('notes')
        )
        return {
            "success": True,
            "message": "Item adicionado à wishlist",
            "data": {
                "wishlist_id": str(wishlist_item.id),
                "listing_id": str(wishlist_item.listing_id),
                "prioridade": wishlist_item.prioridade
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/wishlist/", response_model=dict)
async def get_wishlist(
    limit: int = Query(50, description="Limite de resultados"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter wishlist do usuário"""
    try:
        wishlist_items = await marketplace_service.get_wishlist(db, current_user.id, limit)
        return {
            "success": True,
            "data": {
                "wishlist": [
                    {
                        "id": str(item.id),
                        "listing": {
                            "id": str(item.listing.id),
                            "titulo": item.listing.titulo,
                            "slug": item.listing.slug,
                            "preco_original": float(item.listing.preco_original),
                            "rating_medio": item.listing.rating_medio,
                            "categoria": item.listing.category.nome if item.listing.category else None
                        },
                        "prioridade": item.prioridade,
                        "notas": item.notas,
                        "added_at": item.created_at.isoformat()
                    }
                    for item in wishlist_items
                ],
                "total": len(wishlist_items)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE ESTATÍSTICAS
# =============================================================================

@router.get("/statistics/", response_model=dict)
async def get_marketplace_statistics(
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter estatísticas do marketplace"""
    try:
        stats = await marketplace_service.get_marketplace_statistics(db, current_user.id if current_user else None)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))