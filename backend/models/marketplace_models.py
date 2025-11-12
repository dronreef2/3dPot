"""
Modelos SQLAlchemy - Marketplace Platform (Sprint 6+)
====================================================

Modelos para marketplace de modelos 3D e serviços, incluindo:
- Listagens de produtos (MarketplaceListing)
- Transações e pagamentos (Transaction)
- Avaliações e reviews (Review)
- Licenças de uso (License)
- Métodos de pagamento (PaymentMethod)
- Categorias e tags (Category, Tag)

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4, UUID
from decimal import Decimal

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, 
    JSON, Numeric, String, Text, Float, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from . import Base


class Category(Base):
    """Categorias do marketplace"""
    __tablename__ = "categories"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Informações da categoria
    nome = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    
    # Hierarquia
    categoria_pai_id = Column(PGUUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    nivel_hierarquia = Column(Integer, default=0)
    
    # Configurações
    ativa = Column(Boolean, default=True)
    ordem_exibicao = Column(Integer, default=0)
    icone = Column(String(200), nullable=True)
    
    # SEO
    meta_titulo = Column(String(200), nullable=True)
    meta_descricao = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    listings = relationship("MarketplaceListing", back_populates="category")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('slug', name='uq_category_slug'),
    )


class Tag(Base):
    """Tags para classificação de modelos"""
    __tablename__ = "tags"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    nome = Column(String(50), nullable=False, unique=True)
    slug = Column(String(50), nullable=False, unique=True)
    
    # Estatísticas
    uso_count = Column(Integer, default=0)
    
    # Status
    ativo = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    listings = relationship("MarketplaceListing", secondary="listing_tags", back_populates="tags")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('slug', name='uq_tag_slug'),
    )


class MarketplaceListing(Base):
    """Listagens de produtos no marketplace"""
    __tablename__ = "marketplace_listings"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    seller_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(PGUUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    
    # Informações básicas do produto
    titulo = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    descricao_curta = Column(Text, nullable=True)
    descricao_completa = Column(Text, nullable=True)
    
    # Arquivo do modelo
    arquivo_modelo_path = Column(String(500), nullable=False)
    arquivo_gallery_path = Column(String(500), nullable=True)  # Imagens/pdfs de showcase
    arquivo_preview_path = Column(String(500), nullable=True)
    arquivo_tamanho_mb = Column(Float, nullable=True)
    
    # Informações técnicas
    formato_arquivo = Column(String(10), nullable=False)  # .stl, .obj, .gltf, etc.
    software_compativel = Column(JSON, default=list)
    software_necessario = Column(JSON, default=list)
    
    # Dimensões e propriedades
    dimensao_x = Column(Float, nullable=True)
    dimensao_y = Column(Float, nullable=True)
    dimensao_z = Column(Float, nullable=True)
    unidade_medida = Column(String(10), default='mm')
    
    # Volume e peso estimados
    volume_estimado_cm3 = Column(Float, nullable=True)
    peso_estimado_g = Column(Float, nullable=True)
    complexidade = Column(Enum('baixa', 'media', 'alta', 'muito_alta', name='complexity_level'))
    
    # Preços e disponibilidade
    preco_original = Column(Numeric(10, 2), nullable=False)
    preco_promocional = Column(Numeric(10, 2), nullable=True)
    moeda = Column(String(3), default='BRL')
    
    # Disponibilidade
    estoque_disponivel = Column(Integer, default=0)
    download_ilimitado = Column(Boolean, default=True)
    download_licenca = Column(Enum('personal', 'commercial', 'extended', name='license_type'), 
                             default='personal')
    
    # Status da listagem
    status = Column(Enum('draft', 'pending_review', 'approved', 'rejected', 'suspended', 'archived', 
                        name='listing_status'), default='draft')
    featured = Column(Boolean, default=False)
    premium = Column(Boolean, default=False)
    
    # Estatísticas
    visualizacoes_count = Column(Integer, default=0)
    downloads_count = Column(Integer, default=0)
    vendas_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    
    # Avaliação média
    rating_medio = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Configurações de SEO
    meta_titulo = Column(String(200), nullable=True)
    meta_descricao = Column(Text, nullable=True)
    palavras_chave = Column(JSON, default=list)
    
    # Configurações de licenciamento
    permissoes_uso = Column(JSON, default=dict)
    restricoes = Column(JSON, default=list)
    atributos_licenca = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    seller = relationship("User", back_populates="marketplace_listings")
    category = relationship("Category", back_populates="listings")
    tags = relationship("Tag", secondary="listing_tags", back_populates="listings")
    transactions = relationship("Transaction", back_populates="listing")
    reviews = relationship("Review", back_populates="listing")
    licenses = relationship("License", back_populates="listing")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('seller_id', 'slug', name='uq_listing_seller_slug'),
        Index('idx_listings_status', 'status'),
        Index('idx_listings_category', 'category_id'),
        Index('idx_listings_featured', 'featured'),
    )


class ListingTag(Base):
    """Tabela de associação listing-tags"""
    __tablename__ = "listing_tags"
    
    listing_id = Column(PGUUID(as_uuid=True), ForeignKey("marketplace_listings.id"), 
                       primary_key=True)
    tag_id = Column(PGUUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True)
    
    # Relationships
    listing = relationship("MarketplaceListing")
    tag = relationship("Tag")


class Transaction(Base):
    """Transações do marketplace"""
    __tablename__ = "transactions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    listing_id = Column(PGUUID(as_uuid=True), ForeignKey("marketplace_listings.id"), 
                       nullable=False)
    buyer_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    seller_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Informações da transação
    numero_pedido = Column(String(50), nullable=False, unique=True)
    tipo_transacao = Column(Enum('purchase', 'subscription', 'custom_order', name='transaction_type'),
                           default='purchase')
    
    # Valores financeiros
    valor_item = Column(Numeric(10, 2), nullable=False)
    taxa_plataforma = Column(Numeric(10, 2), nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    moeda = Column(String(3), default='BRL')
    
    # Descontos e promoções
    desconto_percentual = Column(Float, nullable=True)
    valor_desconto = Column(Numeric(10, 2), nullable=True)
    codigo_promocional = Column(String(50), nullable=True)
    
    # Pagamento (Stripe)
    stripe_payment_intent_id = Column(String(100), nullable=True)
    stripe_charge_id = Column(String(100), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    
    # Status da transação
    status = Column(Enum('pending', 'processing', 'completed', 'failed', 'cancelled', 
                        'refunded', 'disputed', name='transaction_status'), default='pending')
    
    # Processamento
    processed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    
    # Detalhes de falha/erro
    erro_detalhes = Column(Text, nullable=True)
    codigo_erro = Column(String(50), nullable=True)
    
    # Metadados
    metadata_info = Column(JSON, default=dict)
    notas_internas = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    listing = relationship("MarketplaceListing", back_populates="transactions")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="buyer_transactions")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="seller_transactions")
    payment_method = relationship("PaymentMethod", back_populates="transaction")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('numero_pedido', name='uq_transaction_order_number'),
    )


class Review(Base):
    """Avaliações de produtos"""
    __tablename__ = "reviews"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    listing_id = Column(PGUUID(as_uuid=True), ForeignKey("marketplace_listings.id"), 
                       nullable=False)
    buyer_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Rating e feedback
    rating_geral = Column(Integer, nullable=False)  # 1-5 estrelas
    rating_qualidade = Column(Integer, nullable=True)  # 1-5
    rating_facilidade_uso = Column(Integer, nullable=True)  # 1-5
    rating_documentacao = Column(Integer, nullable=True)  # 1-5
    rating_suporte = Column(Integer, nullable=True)  # 1-5
    
    # Comentários
    comentario = Column(Text, nullable=True)
    titulo = Column(String(200), nullable=True)
    
    # Votos de outros usuários
    helpful_votes = Column(Integer, default=0)
    unhelpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # Moderação
    moderado = Column(Boolean, default=False)
    moderador_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    motivo_moderacao = Column(Text, nullable=True)
    aprovado = Column(Boolean, default=True)
    
    # Status
    ativo = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    moderated_at = Column(DateTime, nullable=True)
    
    # Relationships
    listing = relationship("MarketplaceListing", back_populates="reviews")
    buyer = relationship("User", back_populates="reviews_given")
    moderator = relationship("User", foreign_keys=[moderador_id])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('listing_id', 'buyer_id', name='uq_review_listing_buyer'),
        Index('idx_reviews_rating', 'rating_geral'),
    )


class License(Base):
    """Licenças de uso de modelos"""
    __tablename__ = "licenses"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    listing_id = Column(PGUUID(as_uuid=True), ForeignKey("marketplace_listings.id"), 
                       nullable=False)
    buyer_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transaction_id = Column(PGUUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    
    # Tipo de licença
    tipo_licenca = Column(Enum('personal', 'commercial', 'extended', 'exclusive', name='license_type'),
                         nullable=False)
    
    # Escopo da licença
    uso_pessoal = Column(Boolean, default=True)
    uso_comercial = Column(Boolean, default=False)
    uso_sublicenciamento = Column(Boolean, default=False)
    uso_distribuicao = Column(Boolean, default=False)
    modificacoes_permitidas = Column(Boolean, default=True)
    copia_porcelana_permitida = Column(Boolean, default=True)
    
    # Restrições
    quantidade_maxima_usos = Column(Integer, nullable=True)
    distribuicao_geografica = Column(JSON, default=list)
    restricoes_uso = Column(JSON, default=list)
    
    # Detalhes da licença
    descricao_detalhes = Column(Text, nullable=True)
    atributos_especiais = Column(JSON, default=dict)
    
    # Status
    status = Column(Enum('active', 'expired', 'suspended', 'revoked', name='license_status'),
                   default='active')
    
    # Validade
    ativa_desde = Column(DateTime, default=datetime.utcnow)
    expira_em = Column(DateTime, nullable=True)
    
    # Metadados
    license_key = Column(String(100), nullable=True, unique=True)
    download_urls = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    listing = relationship("MarketplaceListing", back_populates="licenses")
    buyer = relationship("User", back_populates="licenses")
    transaction = relationship("Transaction", back_populates="license")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('listing_id', 'buyer_id', 'transaction_id', name='uq_license_unique'),
    )


class PaymentMethod(Base):
    """Métodos de pagamento dos usuários"""
    __tablename__ = "payment_methods"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transaction_id = Column(PGUUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    
    # Stripe payment method
    stripe_payment_method_id = Column(String(100), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    
    # Informações do método
    tipo = Column(Enum('credit_card', 'debit_card', 'pix', 'bank_transfer', 'paypal', 
                      name='payment_method_type'), nullable=False)
    
    # Dados do cartão (Tokenizados)
    card_brand = Column(String(20), nullable=True)
    card_last_four = Column(String(4), nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)
    
    # Dados bancários
    bank_code = Column(String(10), nullable=True)
    bank_name = Column(String(50), nullable=True)
    account_type = Column(Enum('checking', 'savings', name='account_type'), nullable=True)
    
    # Configurações
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payment_methods")
    transaction = relationship("Transaction", back_populates="payment_method")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('stripe_payment_method_id', name='uq_payment_method_stripe'),
    )


class Wishlist(Base):
    """Lista de desejos do marketplace"""
    __tablename__ = "wishlist"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    listing_id = Column(PGUUID(as_uuid=True), ForeignKey("marketplace_listings.id"), 
                       nullable=False)
    
    # Notas pessoais
    notas = Column(Text, nullable=True)
    prioridade = Column(Enum('high', 'medium', 'low', name='wishlist_priority'), 
                       default='medium')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wishlist")
    listing = relationship("MarketplaceListing")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'listing_id', name='uq_wishlist_user_listing'),
    )


class Promotion(Base):
    """Promoções e cupons do marketplace"""
    __tablename__ = "promotions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Informações da promoção
    codigo = Column(String(50), nullable=False, unique=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Tipo de desconto
    tipo_desconto = Column(Enum('percentage', 'fixed_amount', name='discount_type'), 
                          nullable=False)
    valor_desconto = Column(Numeric(10, 2), nullable=False)
    valor_minimo_pedido = Column(Numeric(10, 2), nullable=True)
    valor_maximo_desconto = Column(Numeric(10, 2), nullable=True)
    
    # Aplicabilidade
    aplicavel_categorias = Column(JSON, default=list)  # Lista de category_ids
    aplicavel_vendedores = Column(JSON, default=list)  # Lista de seller_ids
    aplicavel_compradores = Column(JSON, default=list)  # Lista de buyer_ids
    aplicavel_produtos = Column(JSON, default=list)    # Lista de listing_ids
    
    # Limites de uso
    uso_maximo_total = Column(Integer, nullable=True)
    uso_maximo_por_usuario = Column(Integer, default=1)
    usos_realizados = Column(Integer, default=0)
    
    # Validade
    ativa_desde = Column(DateTime, default=datetime.utcnow)
    expira_em = Column(DateTime, nullable=True)
    
    # Status
    ativa = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Adicionar relacionamentos ao modelo User
def add_user_marketplace_relationships():
    """Adicionar relacionamentos ao modelo User"""
    if not hasattr(User, 'marketplace_listings'):
        User.marketplace_listings = relationship(
            "MarketplaceListing", 
            back_populates="seller"
        )
    
    if not hasattr(User, 'buyer_transactions'):
        User.buyer_transactions = relationship(
            "Transaction",
            foreign_keys="Transaction.buyer_id",
            back_populates="buyer"
        )
    
    if not hasattr(User, 'seller_transactions'):
        User.seller_transactions = relationship(
            "Transaction",
            foreign_keys="Transaction.seller_id",
            back_populates="seller"
        )
    
    if not hasattr(User, 'reviews_given'):
        User.reviews_given = relationship(
            "Review",
            back_populates="buyer"
        )
    
    if not hasattr(User, 'licenses'):
        User.licenses = relationship(
            "License",
            back_populates="buyer"
        )
    
    if not hasattr(User, 'payment_methods'):
        User.payment_methods = relationship(
            "PaymentMethod",
            back_populates="user"
        )
    
    if not hasattr(User, 'wishlist'):
        User.wishlist = relationship(
            "Wishlist",
            back_populates="user"
        )