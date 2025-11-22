"""
3dPot v2.0 - Serviço de Marketplace (Sprint 6+)
==============================================

Serviço para marketplace de modelos 3D e serviços, incluindo:
- Gestão de listagens (MarketplaceListing)
- Processamento de transações (Transaction)
- Sistema de avaliações (Review)
- Gerenciamento de licenças (License)
- Integração com Stripe para pagamentos
- Sistema de wishlist e promoções

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

import os
import json
import logging
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from decimal import Decimal
from pathlib import Path

import stripe
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from sqlalchemy.orm import joinedload

from backend.core.config import settings
from backend.models import (
    Category, Tag, MarketplaceListing, ListingTag, Transaction, Review,
    License, PaymentMethod, Wishlist, Promotion,
    User
)

logger = logging.getLogger(__name__)


class MarketplaceService:
    """Serviço principal do marketplace"""
    
    def __init__(self):
        # Configurar Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe_config = {
            'api_key': settings.STRIPE_SECRET_KEY,
            'api_version': '2023-10-16',
        }
        
        # Configurações de taxas
        self.platform_fee_rate = 0.05  # 5% taxa da plataforma
        self.tax_rate = 0.0  # Configurar conforme localização
        
        # Status mapping para Stripe
        self.stripe_status_mapping = {
            'pending': 'pending',
            'processing': 'processing',
            'completed': 'succeeded',
            'failed': 'failed',
            'cancelled': 'canceled',
            'refunded': 'refunded',
            'disputed': 'requires_review'
        }
    
    # =============================================================================
    # GESTÃO DE CATEGORIAS
    # =============================================================================
    
    async def create_category(
        self,
        db: Session,
        category_data: Dict[str, Any]
    ) -> Category:
        """Criar nova categoria"""
        try:
            # Verificar se categoria com mesmo nome já existe
            existing = db.query(Category).filter(
                Category.nome == category_data['nome']
            ).first()
            
            if existing:
                raise ValueError("Categoria já existe")
            
            # Gerar slug
            slug = self._generate_slug(category_data['nome'])
            
            # Verificar categoria pai se fornecida
            parent = None
            if category_data.get('categoria_pai_id'):
                parent = db.query(Category).filter(
                    Category.id == category_data['categoria_pai_id']
                ).first()
                
                if not parent:
                    raise ValueError("Categoria pai não encontrada")
                
                category_data['nivel_hierarquia'] = parent.nivel_hierarquia + 1
            
            # Criar categoria
            category = Category(
                nome=category_data['nome'],
                slug=slug,
                descricao=category_data.get('descricao'),
                categoria_pai_id=category_data.get('categoria_pai_id'),
                nivel_hierarquia=category_data.get('nivel_hierarquia', 0),
                ativa=category_data.get('ativa', True),
                ordem_exibicao=category_data.get('ordem_exibicao', 0),
                icone=category_data.get('icone'),
                meta_titulo=category_data.get('meta_titulo'),
                meta_descricao=category_data.get('meta_descricao')
            )
            
            db.add(category)
            db.commit()
            db.refresh(category)
            
            logger.info(f"Categoria criada: {category.id}")
            return category
            
        except Exception as e:
            logger.error(f"Erro ao criar categoria: {e}")
            raise
    
    async def list_categories(
        self,
        db: Session,
        active_only: bool = True,
        include_children: bool = True
    ) -> List[Category]:
        """Listar categorias"""
        try:
            query = db.query(Category)
            
            if active_only:
                query = query.filter(Category.ativa == True)
            
            categories = query.order_by(Category.ordem_exibicao, Category.nome).all()
            
            if not include_children:
                # Filtrar apenas categorias de nível 0
                categories = [cat for cat in categories if cat.nivel_hierarquia == 0]
            
            return categories
            
        except Exception as e:
            logger.error(f"Erro ao listar categorias: {e}")
            raise
    
    # =============================================================================
    # GESTÃO DE TAGS
    # =============================================================================
    
    async def create_tag(
        self,
        db: Session,
        tag_data: Dict[str, Any]
    ) -> Tag:
        """Criar nova tag"""
        try:
            # Verificar se tag já existe
            existing = db.query(Tag).filter(
                or_(
                    Tag.nome == tag_data['nome'],
                    Tag.slug == tag_data.get('slug', tag_data['nome'])
                )
            ).first()
            
            if existing:
                raise ValueError("Tag já existe")
            
            # Gerar slug se não fornecido
            slug = tag_data.get('slug') or self._generate_slug(tag_data['nome'])
            
            # Criar tag
            tag = Tag(
                nome=tag_data['nome'],
                slug=slug,
                ativo=tag_data.get('ativo', True)
            )
            
            db.add(tag)
            db.commit()
            db.refresh(tag)
            
            logger.info(f"Tag criada: {tag.id}")
            return tag
            
        except Exception as e:
            logger.error(f"Erro ao criar tag: {e}")
            raise
    
    async def search_tags(
        self,
        db: Session,
        query: str,
        limit: int = 20
    ) -> List[Tag]:
        """Buscar tags"""
        try:
            tags = db.query(Tag).filter(
                and_(
                    Tag.ativo == True,
                    or_(
                        Tag.nome.ilike(f"%{query}%"),
                        Tag.slug.ilike(f"%{query}%")
                    )
                )
            ).order_by(desc(Tag.uso_count)).limit(limit).all()
            
            return tags
            
        except Exception as e:
            logger.error(f"Erro ao buscar tags: {e}")
            raise
    
    # =============================================================================
    # GESTÃO DE LISTAGENS
    # =============================================================================
    
    async def create_listing(
        self,
        db: Session,
        seller_id: UUID,
        listing_data: Dict[str, Any]
    ) -> MarketplaceListing:
        """Criar nova listagem"""
        try:
            # Verificar se vendedor existe
            seller = db.query(User).filter(User.id == seller_id).first()
            if not seller:
                raise ValueError("Vendedor não encontrado")
            
            # Verificar categoria
            category = db.query(Category).filter(
                Category.id == listing_data['category_id']
            ).first()
            
            if not category:
                raise ValueError("Categoria não encontrada")
            
            # Verificar arquivo do modelo
            model_path = Path(listing_data['arquivo_modelo_path'])
            if not model_path.exists():
                raise ValueError("Arquivo do modelo não encontrado")
            
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            
            # Gerar slug único
            slug = await self._generate_unique_slug(
                db, listing_data['titulo'], seller_id
            )
            
            # Criar listagem
            listing = MarketplaceListing(
                seller_id=seller_id,
                category_id=listing_data['category_id'],
                titulo=listing_data['titulo'],
                slug=slug,
                descricao_curta=listing_data.get('descricao_curta'),
                descricao_completa=listing_data.get('descricao_completa'),
                arquivo_modelo_path=listing_data['arquivo_modelo_path'],
                arquivo_gallery_path=listing_data.get('arquivo_gallery_path'),
                arquivo_preview_path=listing_data.get('arquivo_preview_path'),
                arquivo_tamanho_mb=file_size_mb,
                formato_arquivo=listing_data.get('formato_arquivo'),
                software_compativel=listing_data.get('software_compativel', []),
                software_necessario=listing_data.get('software_necessario', []),
                dimensao_x=listing_data.get('dimensao_x'),
                dimensao_y=listing_data.get('dimensao_y'),
                dimensao_z=listing_data.get('dimensao_z'),
                unidade_medida=listing_data.get('unidade_medida', 'mm'),
                volume_estimado_cm3=listing_data.get('volume_estimado_cm3'),
                peso_estimado_g=listing_data.get('peso_estimado_g'),
                complexidade=listing_data.get('complexidade'),
                preco_original=Decimal(str(listing_data['preco_original'])),
                preco_promocional=listing_data.get('preco_promocional'),
                moeda=listing_data.get('moeda', 'BRL'),
                estoque_disponivel=listing_data.get('estoque_disponivel', 0),
                download_ilimitado=listing_data.get('download_ilimitado', True),
                download_licenca=listing_data.get('download_licenca', 'personal'),
                status='draft',
                featured=listing_data.get('featured', False),
                premium=listing_data.get('premium', False),
                meta_titulo=listing_data.get('meta_titulo'),
                meta_descricao=listing_data.get('meta_descricao'),
                palavras_chave=listing_data.get('palavras_chave', []),
                permissoes_uso=listing_data.get('permissoes_uso', {}),
                restricoes=listing_data.get('restricoes', []),
                atributos_licenca=listing_data.get('atributos_licenca', {})
            )
            
            db.add(listing)
            db.commit()
            db.refresh(listing)
            
            # Adicionar tags se fornecidas
            if listing_data.get('tags'):
                await self._add_tags_to_listing(db, listing.id, listing_data['tags'])
            
            logger.info(f"Listagem criada: {listing.id} por vendedor {seller_id}")
            return listing
            
        except Exception as e:
            logger.error(f"Erro ao criar listagem: {e}")
            raise
    
    async def list_listings(
        self,
        db: Session,
        filters: Optional[Dict] = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = 'created_at'
    ) -> Tuple[List[MarketplaceListing], int]:
        """Listar listagens com filtros"""
        try:
            query = db.query(MarketplaceListing).filter(
                MarketplaceListing.status == 'approved'
            )
            
            # Aplicar filtros
            if filters:
                if 'category_id' in filters:
                    query = query.filter(MarketplaceListing.category_id == filters['category_id'])
                
                if 'price_min' in filters:
                    query = query.filter(MarketplaceListing.preco_original >= filters['price_min'])
                
                if 'price_max' in filters:
                    query = query.filter(MarketplaceListing.preco_original <= filters['price_max'])
                
                if 'seller_id' in filters:
                    query = query.filter(MarketplaceListing.seller_id == filters['seller_id'])
                
                if 'featured_only' in filters and filters['featured_only']:
                    query = query.filter(MarketplaceListing.featured == True)
                
                if 'premium_only' in filters and filters['premium_only']:
                    query = query.filter(MarketplaceListing.premium == True)
                
                if 'search_query' in filters:
                    search_term = f"%{filters['search_query']}%"
                    query = query.filter(
                        or_(
                            MarketplaceListing.titulo.ilike(search_term),
                            MarketplaceListing.descricao_curta.ilike(search_term),
                            MarketplaceListing.palavras_chave.contains([filters['search_query']])
                        )
                    )
            
            # Contar total
            total = query.count()
            
            # Aplicar ordenação
            if sort_by == 'price_asc':
                query = query.order_by(MarketplaceListing.preco_original)
            elif sort_by == 'price_desc':
                query = query.order_by(desc(MarketplaceListing.preco_original))
            elif sort_by == 'rating':
                query = query.order_by(desc(MarketplaceListing.rating_medio))
            elif sort_by == 'popularity':
                query = query.order_by(desc(MarketplaceListing.downloads_count))
            elif sort_by == 'created_desc':
                query = query.order_by(desc(MarketplaceListing.created_at))
            else:
                query = query.order_by(desc(MarketplaceListing.created_at))
            
            # Aplicar paginação
            listings = query.offset(offset).limit(limit).options(
                joinedload(MarketplaceListing.category),
                joinedload(MarketplaceListing.tags),
                joinedload(MarketplaceListing.seller)
            ).all()
            
            return listings, total
            
        except Exception as e:
            logger.error(f"Erro ao listar listagens: {e}")
            raise
    
    async def get_listing(
        self,
        db: Session,
        listing_id: Optional[UUID] = None,
        slug: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> Optional[MarketplaceListing]:
        """Obter detalhes da listagem"""
        try:
            query = db.query(MarketplaceListing)
            
            if listing_id:
                query = query.filter(MarketplaceListing.id == listing_id)
            elif slug:
                query = query.filter(MarketplaceListing.slug == slug)
            else:
                raise ValueError("ID ou slug da listagem é obrigatório")
            
            listing = query.options(
                joinedload(MarketplaceListing.category),
                joinedload(MarketplaceListing.tags),
                joinedload(MarketplaceListing.seller),
                joinedload(MarketplaceListing.reviews).joinedload(Review.buyer)
            ).first()
            
            if not listing:
                return None
            
            # Incrementar contador de visualizações
            if user_id != listing.seller_id:  # Não contar visualizações do próprio vendedor
                listing.visualizacoes_count += 1
                db.commit()
            
            return listing
            
        except Exception as e:
            logger.error(f"Erro ao obter listagem: {e}")
            raise
    
    async def update_listing(
        self,
        db: Session,
        listing_id: UUID,
        seller_id: UUID,
        listing_data: Dict[str, Any]
    ) -> Optional[MarketplaceListing]:
        """Atualizar listagem"""
        try:
            listing = db.query(MarketplaceListing).filter(
                and_(
                    MarketplaceListing.id == listing_id,
                    MarketplaceListing.seller_id == seller_id
                )
            ).first()
            
            if not listing:
                raise ValueError("Listagem não encontrada")
            
            # Verificar se listagem pode ser editada
            if listing.status not in ['draft', 'rejected']:
                raise ValueError("Listagem não pode ser editada no status atual")
            
            # Atualizar campos
            updatable_fields = [
                'titulo', 'descricao_curta', 'descricao_completa', 'preco_original',
                'preco_promocional', 'moeda', 'estoque_disponivel', 'download_licenca',
                'meta_titulo', 'meta_descricao', 'palavras_chave'
            ]
            
            for field in updatable_fields:
                if field in listing_data:
                    setattr(listing, field, listing_data[field])
            
            listing.updated_at = datetime.utcnow()
            
            # Atualizar tags se fornecidas
            if 'tags' in listing_data:
                await self._update_listing_tags(db, listing.id, listing_data['tags'])
            
            db.commit()
            db.refresh(listing)
            
            logger.info(f"Listagem atualizada: {listing_id}")
            return listing
            
        except Exception as e:
            logger.error(f"Erro ao atualizar listagem: {e}")
            raise
    
    async def publish_listing(
        self,
        db: Session,
        listing_id: UUID,
        seller_id: UUID
    ) -> bool:
        """Publicar listagem (enviar para análise)"""
        try:
            listing = db.query(MarketplaceListing).filter(
                and_(
                    MarketplaceListing.id == listing_id,
                    MarketplaceListing.seller_id == seller_id
                )
            ).first()
            
            if not listing:
                raise ValueError("Listagem não encontrada")
            
            if listing.status != 'draft':
                raise ValueError("Apenas listagens em rascunho podem ser publicadas")
            
            # Validar listagem
            validation_result = await self._validate_listing(listing)
            if not validation_result['valid']:
                raise ValueError(f"Listagem inválida: {validation_result['errors']}")
            
            # Atualizar status
            listing.status = 'pending_review'
            listing.published_at = datetime.utcnow()
            listing.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Listagem enviada para análise: {listing_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar listagem: {e}")
            raise
    
    # =============================================================================
    # PROCESSAMENTO DE TRANSAÇÕES E PAGAMENTOS
    # =============================================================================
    
    async def create_transaction(
        self,
        db: Session,
        buyer_id: UUID,
        listing_id: UUID,
        transaction_data: Dict[str, Any]
    ) -> Transaction:
        """Criar nova transação"""
        try:
            # Verificar comprador
            buyer = db.query(User).filter(User.id == buyer_id).first()
            if not buyer:
                raise ValueError("Comprador não encontrado")
            
            # Verificar listagem
            listing = db.query(MarketplaceListing).filter(
                MarketplaceListing.id == listing_id
            ).first()
            
            if not listing:
                raise ValueError("Listagem não encontrada")
            
            if listing.status != 'approved':
                raise ValueError("Listagem não está disponível para compra")
            
            # Verificar estoque
            if not listing.download_ilimitado and listing.estoque_disponivel <= 0:
                raise ValueError("Produto fora de estoque")
            
            # Calcular valores
            original_price = listing.preco_original
            promo_price = listing.preco_promocional
            final_price = promo_price if promo_price else original_price
            
            # Aplicar desconto de código promocional
            discount_amount = Decimal('0.00')
            discount_percentage = 0.0
            promotion_code = transaction_data.get('codigo_promocional')
            
            if promotion_code:
                promo_result = await self._apply_promotion_code(db, promotion_code, final_price)
                if promo_result['valid']:
                    discount_amount = promo_result['discount_amount']
                    discount_percentage = promo_result['discount_percentage']
            
            # Calcular valores finais
            subtotal = final_price - discount_amount
            platform_fee = subtotal * Decimal(str(self.platform_fee_rate))
            total_amount = subtotal + platform_fee
            
            # Gerar número do pedido único
            order_number = await self._generate_order_number(db)
            
            # Criar transação
            transaction = Transaction(
                listing_id=listing_id,
                buyer_id=buyer_id,
                seller_id=listing.seller_id,
                numero_pedido=order_number,
                tipo_transacao=transaction_data.get('tipo_transacao', 'purchase'),
                valor_item=subtotal,
                taxa_plataforma=platform_fee,
                valor_total=total_amount,
                moeda=listing.moeda,
                desconto_percentual=discount_percentage,
                valor_desconto=discount_amount,
                codigo_promocional=promotion_code,
                status='pending',
                metadata=transaction_data.get('metadata', {}),
                created_at=datetime.utcnow()
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            # Criar payment intent no Stripe
            if total_amount > 0:  # Transações gratuitas não precisam de pagamento
                payment_intent = await self._create_stripe_payment_intent(
                    transaction, listing
                )
                
                transaction.stripe_payment_intent_id = payment_intent['id']
                db.commit()
            
            logger.info(f"Transação criada: {transaction.id} para listagem {listing_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Erro ao criar transação: {e}")
            raise
    
    async def process_payment(
        self,
        db: Session,
        transaction_id: UUID,
        payment_method_id: str,
        user_id: UUID
    ) -> Transaction:
        """Processar pagamento via Stripe"""
        try:
            transaction = db.query(Transaction).filter(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.buyer_id == user_id
                )
            ).first()
            
            if not transaction:
                raise ValueError("Transação não encontrada")
            
            if transaction.status != 'pending':
                raise ValueError("Transação não pode ser processada no status atual")
            
            if transaction.valor_total <= 0:
                # Transação gratuita - processar automaticamente
                return await self._complete_free_transaction(db, transaction)
            
            # Processar pagamento via Stripe
            payment_intent = stripe.PaymentIntent.retrieve(
                transaction.stripe_payment_intent_id
            )
            
            if payment_intent['status'] == 'requires_payment_method':
                # Confirmar pagamento com método fornecido
                payment_intent = stripe.PaymentIntent.confirm(
                    transaction.stripe_payment_intent_id,
                    payment_method=payment_method_id,
                    return_url=f"{settings.FRONTEND_URL}/marketplace/payment-success"
                )
            
            # Verificar status do pagamento
            if payment_intent['status'] == 'succeeded':
                transaction.status = 'completed'
                transaction.processed_at = datetime.utcnow()
                transaction.stripe_charge_id = payment_intent['charges']['data'][0]['id']
                
                # Atualizar listagem (estoque, vendas)
                await self._update_listing_after_sale(db, transaction)
                
                # Criar licença
                await self._create_license(db, transaction)
                
                db.commit()
                db.refresh(transaction)
                
                logger.info(f"Pagamento processado com sucesso: {transaction_id}")
                return transaction
                
            elif payment_intent['status'] == 'requires_action':
                # Pagamento requer autenticação 3D Secure
                return {
                    'transaction_id': transaction_id,
                    'requires_action': True,
                    'client_secret': payment_intent['client_secret']
                }
            else:
                transaction.status = 'failed'
                transaction.failed_at = datetime.utcnow()
                transaction.erro_detalhes = f"Pagamento falhou: {payment_intent['status']}"
                db.commit()
                
                raise ValueError(f"Pagamento falhou: {payment_intent['status']}")
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento: {e}")
            raise
    
    async def handle_stripe_webhook(
        self,
        db: Session,
        webhook_data: Dict[str, Any]
    ) -> bool:
        """Processar webhook do Stripe"""
        try:
            event_type = webhook_data['type']
            data_object = webhook_data['data']['object']
            
            if event_type == 'payment_intent.succeeded':
                transaction_id = data_object.get('metadata', {}).get('transaction_id')
                if transaction_id:
                    transaction = db.query(Transaction).filter(
                        Transaction.id == transaction_id
                    ).first()
                    
                    if transaction and transaction.status == 'pending':
                        transaction.status = 'completed'
                        transaction.processed_at = datetime.utcnow()
                        transaction.stripe_charge_id = data_object['charges']['data'][0]['id']
                        
                        # Atualizar listagem e criar licença
                        await self._update_listing_after_sale(db, transaction)
                        await self._create_license(db, transaction)
                        
                        db.commit()
                        
            elif event_type == 'payment_intent.payment_failed':
                transaction_id = data_object.get('metadata', {}).get('transaction_id')
                if transaction_id:
                    transaction = db.query(Transaction).filter(
                        Transaction.id == transaction_id
                    ).first()
                    
                    if transaction:
                        transaction.status = 'failed'
                        transaction.failed_at = datetime.utcnow()
                        transaction.erro_detalhes = data_object.get('last_payment_error', {}).get('message')
                        db.commit()
            
            logger.info(f"Webhook Stripe processado: {event_type}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar webhook Stripe: {e}")
            raise
    
    # =============================================================================
    # SISTEMA DE AVALIAÇÕES
    # =============================================================================
    
    async def create_review(
        self,
        db: Session,
        listing_id: UUID,
        buyer_id: UUID,
        review_data: Dict[str, Any]
    ) -> Review:
        """Criar avaliação de produto"""
        try:
            # Verificar se comprador comprou o produto
            transaction = db.query(Transaction).filter(
                and_(
                    Transaction.listing_id == listing_id,
                    Transaction.buyer_id == buyer_id,
                    Transaction.status == 'completed'
                )
            ).first()
            
            if not transaction:
                raise ValueError("Produto deve ser comprado antes de avaliar")
            
            # Verificar se já existe avaliação
            existing_review = db.query(Review).filter(
                and_(
                    Review.listing_id == listing_id,
                    Review.buyer_id == buyer_id
                )
            ).first()
            
            if existing_review:
                raise ValueError("Já existe uma avaliação deste produto")
            
            # Criar avaliação
            review = Review(
                listing_id=listing_id,
                buyer_id=buyer_id,
                rating_geral=review_data['rating_geral'],
                rating_qualidade=review_data.get('rating_qualidade'),
                rating_facilidade_uso=review_data.get('rating_facilidade_uso'),
                rating_documentacao=review_data.get('rating_documentacao'),
                rating_suporte=review_data.get('rating_suporte'),
                comentario=review_data.get('comentario'),
                titulo=review_data.get('titulo'),
                created_at=datetime.utcnow()
            )
            
            db.add(review)
            
            # Atualizar rating médio da listagem
            await self._update_listing_rating(db, listing_id)
            
            db.commit()
            db.refresh(review)
            
            logger.info(f"Avaliação criada: {review.id} para listagem {listing_id}")
            return review
            
        except Exception as e:
            logger.error(f"Erro ao criar avaliação: {e}")
            raise
    
    async def get_reviews(
        self,
        db: Session,
        listing_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Review], int]:
        """Obter avaliações da listagem"""
        try:
            query = db.query(Review).filter(
                and_(
                    Review.listing_id == listing_id,
                    Review.ativo == True
                )
            )
            
            total = query.count()
            
            reviews = query.order_by(desc(Review.created_at)).offset(offset).limit(limit).options(
                joinedload(Review.buyer)
            ).all()
            
            return reviews, total
            
        except Exception as e:
            logger.error(f"Erro ao obter avaliações: {e}")
            raise
    
    # =============================================================================
    # WISHLIST
    # =============================================================================
    
    async def add_to_wishlist(
        self,
        db: Session,
        user_id: UUID,
        listing_id: UUID,
        notes: Optional[str] = None
    ) -> Wishlist:
        """Adicionar item à wishlist"""
        try:
            # Verificar se já está na wishlist
            existing = db.query(Wishlist).filter(
                and_(
                    Wishlist.user_id == user_id,
                    Wishlist.listing_id == listing_id
                )
            ).first()
            
            if existing:
                raise ValueError("Item já está na wishlist")
            
            # Verificar se listagem existe
            listing = db.query(MarketplaceListing).filter(
                MarketplaceListing.id == listing_id
            ).first()
            
            if not listing:
                raise ValueError("Listagem não encontrada")
            
            # Adicionar à wishlist
            wishlist_item = Wishlist(
                user_id=user_id,
                listing_id=listing_id,
                notas=notes,
                prioridade='medium',
                created_at=datetime.utcnow()
            )
            
            db.add(wishlist_item)
            db.commit()
            db.refresh(wishlist_item)
            
            logger.info(f"Item adicionado à wishlist: {listing_id} para usuário {user_id}")
            return wishlist_item
            
        except Exception as e:
            logger.error(f"Erro ao adicionar à wishlist: {e}")
            raise
    
    async def get_wishlist(
        self,
        db: Session,
        user_id: UUID,
        limit: int = 50
    ) -> List[Wishlist]:
        """Obter wishlist do usuário"""
        try:
            wishlist_items = db.query(Wishlist).filter(
                Wishlist.user_id == user_id
            ).order_by(desc(Wishlist.created_at)).limit(limit).options(
                joinedload(Wishlist.listing).joinedload(MarketplaceListing.seller),
                joinedload(Wishlist.listing).joinedload(MarketplaceListing.category)
            ).all()
            
            return wishlist_items
            
        except Exception as e:
            logger.error(f"Erro ao obter wishlist: {e}")
            raise
    
    # =============================================================================
    # MÉTODOS PRIVADOS DE ASSISTÊNCIA
    # =============================================================================
    
    def _generate_slug(self, text: str) -> str:
        """Gerar slug a partir de texto"""
        # Implementar normalização e slugificação
        slug = text.lower()
        slug = slug.replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        return slug
    
    async def _generate_unique_slug(
        self,
        db: Session,
        title: str,
        seller_id: UUID
    ) -> str:
        """Gerar slug único para listagem"""
        base_slug = self._generate_slug(title)
        slug = base_slug
        
        # Verificar unicidade
        counter = 1
        while True:
            existing = db.query(MarketplaceListing).filter(
                and_(
                    MarketplaceListing.slug == slug,
                    MarketplaceListing.seller_id == seller_id
                )
            ).first()
            
            if not existing:
                break
            
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    async def _add_tags_to_listing(
        self,
        db: Session,
        listing_id: UUID,
        tag_names: List[str]
    ):
        """Adicionar tags a uma listagem"""
        for tag_name in tag_names:
            # Buscar ou criar tag
            tag = db.query(Tag).filter(Tag.nome == tag_name).first()
            
            if not tag:
                tag = Tag(nome=tag_name, slug=self._generate_slug(tag_name))
                db.add(tag)
                db.flush()
            
            # Adicionar associação
            listing_tag = ListingTag(
                listing_id=listing_id,
                tag_id=tag.id
            )
            db.add(listing_tag)
            
            # Incrementar contador de uso
            tag.uso_count += 1
        
        db.commit()
    
    async def _update_listing_tags(
        self,
        db: Session,
        listing_id: UUID,
        new_tag_names: List[str]
    ):
        """Atualizar tags de uma listagem"""
        # Remover tags existentes
        db.query(ListingTag).filter(
            ListingTag.listing_id == listing_id
        ).delete()
        
        # Adicionar novas tags
        if new_tag_names:
            await self._add_tags_to_listing(db, listing_id, new_tag_names)
    
    async def _validate_listing(self, listing: MarketplaceListing) -> Dict[str, Any]:
        """Validar listagem antes da publicação"""
        errors = []
        
        # Verificar campos obrigatórios
        if not listing.titulo or len(listing.titulo.strip()) < 5:
            errors.append("Título deve ter pelo menos 5 caracteres")
        
        if not listing.descricao_curta or len(listing.descricao_curta.strip()) < 20:
            errors.append("Descrição curta deve ter pelo menos 20 caracteres")
        
        if not listing.preco_original or listing.preco_original <= 0:
            errors.append("Preço deve ser maior que zero")
        
        if not listing.arquivo_modelo_path:
            errors.append("Arquivo do modelo é obrigatório")
        
        # Verificar se arquivo existe
        if listing.arquivo_modelo_path:
            model_path = Path(listing.arquivo_modelo_path)
            if not model_path.exists():
                errors.append("Arquivo do modelo não encontrado")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def _generate_order_number(self, db: Session) -> str:
        """Gerar número único de pedido"""
        import random
        import string
        
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        return f"ORD-{timestamp}-{random_suffix}"
    
    async def _create_stripe_payment_intent(
        self,
        transaction: Transaction,
        listing: MarketplaceListing
    ) -> Dict[str, Any]:
        """Criar payment intent no Stripe"""
        amount_cents = int(transaction.valor_total * 100)  # Converter para centavos
        
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=listing.moeda.lower(),
            metadata={
                'transaction_id': str(transaction.id),
                'listing_id': str(listing.id),
                'buyer_id': str(transaction.buyer_id),
                'seller_id': str(transaction.seller_id)
            },
            automatic_payment_methods={
                'enabled': True,
            }
        )
        
        return payment_intent
    
    async def _complete_free_transaction(
        self,
        db: Session,
        transaction: Transaction
    ) -> Transaction:
        """Completar transação gratuita"""
        transaction.status = 'completed'
        transaction.processed_at = datetime.utcnow()
        
        # Atualizar listagem e criar licença
        await self._update_listing_after_sale(db, transaction)
        await self._create_license(db, transaction)
        
        db.commit()
        db.refresh(transaction)
        
        return transaction
    
    async def _update_listing_after_sale(
        self,
        db: Session,
        transaction: Transaction
    ):
        """Atualizar listagem após venda"""
        listing = transaction.listing
        
        # Incrementar contador de vendas
        listing.vendas_count += 1
        
        # Decrementar estoque se não for download ilimitado
        if not listing.download_ilimitado:
            listing.estoque_disponivel = max(0, listing.estoque_disponivel - 1)
    
    async def _create_license(
        self,
        db: Session,
        transaction: Transaction
    ) -> License:
        """Criar licença para o comprador"""
        listing = transaction.listing
        
        # Gerar license key
        license_key = f"LIC-{transaction.numero_pedido}-{uuid.uuid4().hex[:8].upper()}"
        
        # Definir validade baseada no tipo de licença
        expires_at = None
        if listing.download_licenca != 'exclusive':
            expires_at = datetime.utcnow() + timedelta(days=365)  # 1 ano padrão
        
        license_obj = License(
            listing_id=transaction.listing_id,
            buyer_id=transaction.buyer_id,
            transaction_id=transaction.id,
            tipo_licenca=listing.download_licenca,
            uso_pessoal=True,
            uso_comercial=listing.download_licenca in ['commercial', 'extended'],
            uso_sublicenciamento=listing.download_licenca == 'extended',
            uso_distribuicao=listing.download_licenca == 'exclusive',
            modificacoes_permitidas=listing.permissoes_uso.get('modificacoes_permitidas', True),
            copia_porcelana_permitida=listing.permissoes_uso.get('copia_porcelana_permitida', True),
            descricao_detalhes=listing.atributos_licenca.get('descricao', ''),
            atributos_especiais=listing.atributos_licenca,
            license_key=license_key,
            status='active',
            expira_em=expires_at
        )
        
        db.add(license_obj)
        
        return license_obj
    
    async def _apply_promotion_code(
        self,
        db: Session,
        promo_code: str,
        current_price: Decimal
    ) -> Dict[str, Any]:
        """Aplicar código promocional"""
        promotion = db.query(Promotion).filter(
            and_(
                Promotion.codigo == promo_code,
                Promotion.ativa == True,
                Promotion.ativa_desde <= datetime.utcnow(),
                or_(Promotion.expira_em == None, Promotion.expira_em > datetime.utcnow())
            )
        ).first()
        
        if not promotion:
            return {'valid': False}
        
        # Verificar limites de uso
        if promotion.uso_maximo_total and promotion.usos_realizados >= promotion.uso_maximo_total:
            return {'valid': False}
        
        # Calcular desconto
        if promotion.tipo_desconto == 'percentage':
            discount_amount = current_price * Decimal(str(promotion.valor_desconto / 100))
        else:  # fixed_amount
            discount_amount = promotion.valor_desconto
        
        # Aplicar limite mínimo
        if promotion.valor_minimo_pedido and current_price < promotion.valor_minimo_pedido:
            return {'valid': False}
        
        # Aplicar limite máximo de desconto
        if promotion.valor_maximo_desconto and discount_amount > promotion.valor_maximo_desconto:
            discount_amount = promotion.valor_maximo_desconto
        
        # Incrementar contador de uso
        promotion.usos_realizados += 1
        db.commit()
        
        return {
            'valid': True,
            'discount_amount': min(discount_amount, current_price),
            'discount_percentage': float(promotion.valor_desconto) if promotion.tipo_desconto == 'percentage' else 0
        }
    
    async def _update_listing_rating(
        self,
        db: Session,
        listing_id: UUID
    ):
        """Atualizar rating médio da listagem"""
        listing = db.query(MarketplaceListing).filter(
            MarketplaceListing.id == listing_id
        ).first()
        
        # Calcular rating médio
        reviews = db.query(Review).filter(
            and_(
                Review.listing_id == listing_id,
                Review.ativo == True
            )
        ).all()
        
        if reviews:
            total_rating = sum(review.rating_geral for review in reviews)
            listing.rating_medio = total_rating / len(reviews)
            listing.total_reviews = len(reviews)
        
        db.commit()
    
    # =============================================================================
    # MÉTODOS DE BUSCA E ESTATÍSTICAS
    # =============================================================================
    
    async def search_listings(
        self,
        db: Session,
        query: str,
        filters: Optional[Dict] = None,
        limit: int = 20
    ) -> List[MarketplaceListing]:
        """Buscar listagens"""
        try:
            search_query = db.query(MarketplaceListing).filter(
                MarketplaceListing.status == 'approved'
            )
            
            # Filtro de busca textual
            if query:
                search_term = f"%{query}%"
                search_query = search_query.filter(
                    or_(
                        MarketplaceListing.titulo.ilike(search_term),
                        MarketplaceListing.descricao_curta.ilike(search_term),
                        MarketplaceListing.palavras_chave.contains([query])
                    )
                )
            
            # Aplicar filtros adicionais
            if filters:
                if 'category_id' in filters:
                    search_query = search_query.filter(
                        MarketplaceListing.category_id == filters['category_id']
                    )
                
                if 'price_min' in filters:
                    search_query = search_query.filter(
                        MarketplaceListing.preco_original >= filters['price_min']
                    )
                
                if 'price_max' in filters:
                    search_query = search_query.filter(
                        MarketplaceListing.preco_original <= filters['price_max']
                    )
                
                if 'rating_min' in filters:
                    search_query = search_query.filter(
                        MarketplaceListing.rating_medio >= filters['rating_min']
                    )
            
            listings = search_query.order_by(desc(MarketplaceListing.rating_medio)).limit(limit).all()
            return listings
            
        except Exception as e:
            logger.error(f"Erro na busca de listagens: {e}")
            raise
    
    async def get_marketplace_statistics(
        self,
        db: Session,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Obter estatísticas do marketplace"""
        try:
            base_query = db.query(MarketplaceListing).filter(
                MarketplaceListing.status == 'approved'
            )
            
            if user_id:
                base_query = base_query.filter(MarketplaceListing.seller_id == user_id)
            
            # Contar listagens
            total_listings = base_query.count()
            featured_listings = base_query.filter(MarketplaceListing.featured == True).count()
            premium_listings = base_query.filter(MarketplaceListing.premium == True).count()
            
            # Estatísticas de vendas
            transaction_query = db.query(Transaction).filter(
                Transaction.status == 'completed'
            )
            
            if user_id:
                transaction_query = transaction_query.filter(
                    Transaction.seller_id == user_id
                )
            
            total_sales = transaction_query.count()
            total_revenue = transaction_query.with_entities(
                func.sum(Transaction.valor_item)
            ).scalar() or 0
            
            # Categorias populares
            category_stats = db.query(
                Category.nome,
                func.count(MarketplaceListing.id).label('count')
            ).join(
                MarketplaceListing
            ).filter(
                MarketplaceListing.status == 'approved'
            ).group_by(
                Category.nome
            ).order_by(
                desc('count')
            ).limit(5).all()
            
            return {
                'total_listings': total_listings,
                'featured_listings': featured_listings,
                'premium_listings': premium_listings,
                'total_sales': total_sales,
                'total_revenue': float(total_revenue),
                'popular_categories': [
                    {'name': cat[0], 'count': cat[1]} for cat in category_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            raise