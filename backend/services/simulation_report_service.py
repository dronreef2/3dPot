"""
Serviço de Geração de Relatórios PDF para Simulações
Cria relatórios detalhados com gráficos e análises
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from uuid import UUID
from dataclasses import dataclass
from io import BytesIO

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
from sqlalchemy.orm import Session
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from backend.core.config import REPORTS_STORAGE_PATH
from backend.models import Simulation, Model3D, User, SimulationResult

logger = logging.getLogger(__name__)

# ========== CONFIGURAÇÃO DO MATPLOTLIB ==========

def setup_matplotlib_for_reports():
    """Configurar matplotlib para geração de relatórios"""
    import warnings
    warnings.filterwarnings('default')
    
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.size': 12,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 11,
        'figure.titlesize': 18,
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif'],
        'axes.unicode_minus': False
    })

# ========== CLASSES DE DADOS ==========

@dataclass
class ReportSection:
    """Seção do relatório"""
    title: str
    content: List[Any]
    charts: List[str] = None

@dataclass
class SimulationChart:
    """Dados para criação de gráficos"""
    chart_type: str
    title: str
    data: Dict[str, Any]
    filename: str
    description: str = ""

# ========== SERVIÇO PRINCIPAL ==========

class SimulationReportService:
    """Serviço para geração de relatórios PDF de simulações"""
    
    def __init__(self):
        self.reports_path = REPORTS_STORAGE_PATH
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar matplotlib
        setup_matplotlib_for_reports()
        
        # Estilos para o documento
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Estilo para título
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Estilo para subtítulo
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceBefore=20,
            spaceAfter=15,
            textColor=colors.darkblue
        )
        
        # Estilo para texto normal
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        )
        
        # Estilo para código/dados técnicos
        self.code_style = ParagraphStyle(
            'CustomCode',
            parent=self.styles['Code'],
            fontSize=10,
            fontName='Courier',
            spaceAfter=12,
            backColor=colors.lightgrey,
            leftIndent=20,
            rightIndent=20
        )

    async def generate_simulation_report(
        self, 
        db: Session, 
        simulation_id: UUID,
        include_charts: bool = True,
        include_technical_details: bool = True,
        user_format_preferences: Dict[str, Any] = None
    ) -> str:
        """
        Gerar relatório PDF completo de uma simulação
        
        Args:
            db: Sessão do banco de dados
            simulation_id: ID da simulação
            include_charts: Se deve incluir gráficos
            include_technical_details: Se deve incluir detalhes técnicos
            user_format_preferences: Preferências de formatação do usuário
            
        Returns:
            Caminho para o arquivo PDF gerado
        """
        try:
            # Obter dados da simulação
            simulation = self._get_simulation_data(db, simulation_id)
            if not simulation:
                raise ValueError(f"Simulação {simulation_id} não encontrada")
            
            # Configurar preferências
            preferences = user_format_preferences or {}
            
            # Criar arquivo PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulacao_{simulation_id}_{timestamp}.pdf"
            filepath = self.reports_path / filename
            
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Construir conteúdo do relatório
            story = []
            
            # Título e cabeçalho
            title_content = self._build_title_page(simulation)
            story.extend(title_content)
            
            # Sumário
            story.append(PageBreak())
            story.append(Paragraph("Sumário", self.subtitle_style))
            story.append(Spacer(1, 20))
            
            toc = self._build_table_of_contents(simulation, include_charts)
            story.append(toc)
            
            # Seções do relatório
            sections = await self._build_report_sections(
                db, simulation, include_charts, include_technical_details
            )
            
            for section in sections:
                story.append(PageBreak())
                story.append(Paragraph(section.title, self.subtitle_style))
                story.extend(section.content)
                
                # Adicionar gráficos da seção
                if section.charts:
                    story.append(Spacer(1, 20))
                    for chart_path in section.charts:
                        if os.path.exists(chart_path):
                            # Redimensionar imagem para caber na página
                            img = Image(chart_path, width=6*inch, height=4*inch)
                            story.append(img)
                            story.append(Spacer(1, 10))
            
            # Rodapé
            story.append(PageBreak())
            story.extend(self._build_appendices(simulation))
            
            # Gerar PDF
            doc.build(story)
            
            logger.info(f"Relatório PDF gerado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório PDF: {e}")
            raise

    def _get_simulation_data(self, db: Session, simulation_id: UUID) -> Optional[Dict[str, Any]]:
        """Obter dados completos da simulação"""
        try:
            simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
            if not simulation:
                return None
            
            model = db.query(Model3D).filter(Model3D.id == simulation.modelo_3d_id).first()
            user = db.query(User).filter(User.id == simulation.user_id).first()
            
            # Obter resultados detalhados
            detailed_result = db.query(SimulationResult).filter(
                SimulationResult.simulation_id == simulation_id
            ).first()
            
            return {
                "simulation": simulation,
                "model": model,
                "user": user,
                "detailed_result": detailed_result,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter dados da simulação: {e}")
            return None

    def _build_title_page(self, data: Dict[str, Any]) -> List[Any]:
        """Construir página de título"""
        simulation = data["simulation"]
        model = data["model"]
        user = data["user"]
        
        content = []
        
        # Título principal
        content.append(Paragraph("Relatório de Simulação Física", self.title_style))
        content.append(Spacer(1, 30))
        
        # Informações básicas
        basic_info = [
            ["Nome da Simulação:", simulation.nome],
            ["Tipo:", simulation.tipo_simulacao.replace("_", " ").title()],
            ["Modelo 3D:", model.nome if model else "N/A"],
            ["Usuário:", user.email if user else "N/A"],
            ["Data de Criação:", simulation.created_at.strftime("%d/%m/%Y %H:%M")],
            ["Status:", simulation.status.title()],
            ["Data do Relatório:", datetime.now().strftime("%d/%m/%Y %H:%M")]
        ]
        
        info_table = Table(basic_info, colWidths=[3*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ]))
        
        content.append(info_table)
        content.append(Spacer(1, 40))
        
        # Resumo executivo
        content.append(Paragraph("Resumo Executivo", self.subtitle_style))
        
        summary_text = self._generate_executive_summary(simulation, model)
        content.append(Paragraph(summary_text, self.normal_style))
        
        # Parâmetros da simulação
        content.append(Spacer(1, 20))
        content.append(Paragraph("Parâmetros da Simulação", self.subtitle_style))
        
        params_text = json.dumps(simulation.parametros, indent=2, ensure_ascii=False)
        content.append(Paragraph(f"<pre>{params_text}</pre>", self.code_style))
        
        return content

    def _generate_executive_summary(self, simulation: Simulation, model: Model3D) -> str:
        """Gerar resumo executivo"""
        summary_parts = []
        
        # Tipo de simulação
        tipo_nome = simulation.tipo_simulacao.replace("_", " ").title()
        summary_parts.append(f"Este relatório apresenta os resultados da simulação física de tipo '{tipo_nome}' executada no modelo 3D '{model.nome if model else 'N/A'}'.")
        
        # Status e duração
        if simulation.completed_at and simulation.started_at:
            duration = (simulation.completed_at - simulation.started_at).total_seconds()
            summary_parts.append(f"A simulação foi executada com sucesso em {duration:.1f} segundos.")
        
        # Status geral
        if simulation.status == "completed":
            summary_parts.append("Todos os testes foram concluídos sem erros e os resultados indicam o comportamento esperado do modelo sob as condições testadas.")
        elif simulation.status == "failed":
            summary_parts.append("A simulação encontrou erros durante a execução. Verifique a seção de troubleshooting para detalhes.")
        else:
            summary_parts.append(f"A simulação está com status '{simulation.status}' no momento da geração deste relatório.")
        
        # Conclusões baseadas no tipo
        if simulation.tipo_simulacao == "drop_test" and simulation.metrics:
            summary_parts.append(self._generate_drop_test_summary(simulation.metrics))
        elif simulation.tipo_simulacao == "stress_test" and simulation.metrics:
            summary_parts.append(self._generate_stress_test_summary(simulation.metrics))
        
        return " ".join(summary_parts)

    def _generate_drop_test_summary(self, metrics: Dict[str, Any]) -> str:
        """Gerar resumo específico para teste de queda"""
        vel_media = metrics.get("velocidade_impacto_media", 0)
        rebotes_medio = metrics.get("rebotes_medio", 0)
        classificacao = metrics.get("classificacao_resistencia", "indefinido")
        
        summary = f"A velocidade média de impacto foi de {vel_media:.2f} m/s com {rebotes_medio:.1f} rebotes em média. "
        summary += f"A classificação de resistência é '{classificacao.replace('_', ' ')}', "
        
        if classificacao == "resistente":
            summary += "indicando que o modelo apresenta boa resistência a impactos."
        elif classificacao == "moderado":
            summary += "indicando resistência moderada a impactos."
        else:
            summary += "indicando fragilidade sob impacto."
            
        return summary

    def _generate_stress_test_summary(self, metrics: Dict[str, Any]) -> str:
        """Gerar resumo específico para teste de stress"""
        forca_max = metrics.get("forca_maxima", 0)
        rigidez = metrics.get("rigidez_calculada", 0)
        classificacao = metrics.get("classificacao_resistencia", "indefinido")
        
        summary = f"A força máxima aplicada foi de {forca_max:.0f} N com rigidez calculada de {rigidez:.2f} N/m. "
        summary += f"A classificação de resistência é '{classificacao.replace('_', ' ')}', "
        
        if classificacao == "muito_resistente":
            summary += "indicando excelente resistência estrutural."
        elif classificacao == "resistente":
            summary += "indicando boa resistência estrutural."
        elif classificacao == "moderado":
            summary += "indicando resistência estrutural moderada."
        else:
            summary += "indicando baixa resistência estrutural."
            
        return summary

    def _build_table_of_contents(self, data: Dict[str, Any], include_charts: bool) -> Any:
        """Construir sumário"""
        contents = []
        
        items = [
            "1. Resumo Executivo",
            "2. Informações Técnicas",
            "3. Resultados da Simulação",
            "4. Análise e Recomendações"
        ]
        
        if include_charts:
            items.append("5. Gráficos e Visualizações")
        
        items.extend([
            "6. Dados Técnicos Detalhados",
            "7. Conclusões"
        ])
        
        toc_data = [[f"{i+1}. {item}", f"Página {i+2}"] for i, item in enumerate(items)]
        
        toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ]))
        
        return toc_table

    async def _build_report_sections(
        self, 
        db: Session, 
        data: Dict[str, Any], 
        include_charts: bool,
        include_technical_details: bool
    ) -> List[ReportSection]:
        """Construir seções do relatório"""
        sections = []
        
        # Seção 1: Informações Técnicas
        tech_section = self._build_technical_section(data)
        sections.append(tech_section)
        
        # Seção 2: Resultados
        results_section = self._build_results_section(data, include_technical_details)
        sections.append(results_section)
        
        # Seção 3: Análise
        analysis_section = self._build_analysis_section(data)
        sections.append(analysis_section)
        
        # Seção 4: Gráficos
        if include_charts:
            charts_section = await self._build_charts_section(db, data)
            sections.append(charts_section)
        
        # Seção 5: Dados Técnicos
        if include_technical_details:
            tech_data_section = self._build_technical_data_section(data)
            sections.append(tech_data_section)
        
        # Seção 6: Conclusões
        conclusions_section = self._build_conclusions_section(data)
        sections.append(conclusions_section)
        
        return sections

    def _build_technical_section(self, data: Dict[str, Any]) -> ReportSection:
        """Construir seção de informações técnicas"""
        simulation = data["simulation"]
        model = data["model"]
        
        content = []
        
        # Configurações da simulação
        content.append(Paragraph("Configurações da Simulação", self.subtitle_style))
        
        tech_data = [
            ["Parâmetro", "Valor"],
            ["Tipo de Simulação", simulation.tipo_simulacao.replace("_", " ").title()],
            ["Engine de Física", simulation.physics_engine],
            ["Time Step", f"{simulation.time_step}s"],
            ["Máximo de Iterações", simulation.max_iterations],
            ["Data de Início", simulation.started_at.strftime("%d/%m/%Y %H:%M") if simulation.started_at else "N/A"],
            ["Data de Conclusão", simulation.completed_at.strftime("%d/%m/%Y %H:%M") if simulation.completed_at else "N/A"]
        ]
        
        if simulation.duration:
            tech_data.append(["Duração Total", f"{simulation.duration:.1f} segundos"])
        
        tech_table = Table(tech_data, colWidths=[2.5*inch, 2.5*inch])
        tech_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(tech_table)
        content.append(Spacer(1, 20))
        
        # Informações do modelo
        if model:
            content.append(Paragraph("Informações do Modelo 3D", self.subtitle_style))
            
            model_data = [
                ["Propriedade", "Valor"],
                ["Nome", model.nome],
                ["Arquivo", os.path.basename(model.arquivo_path) if model.arquivo_path else "N/A"],
                ["Tamanho", f"{model.tamanho_bytes / 1024:.1f} KB" if model.tamanho_bytes else "N/A"],
                ["Formato", model.formato or "N/A"],
                ["Data de Criação", model.created_at.strftime("%d/%m/%Y %H:%M") if model.created_at else "N/A"]
            ]
            
            model_table = Table(model_data, colWidths=[2.5*inch, 2.5*inch])
            model_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
            ]))
            
            content.append(model_table)
        
        return ReportSection("Informações Técnicas", content)

    def _build_results_section(self, data: Dict[str, Any], include_technical: bool) -> ReportSection:
        """Construir seção de resultados"""
        simulation = data["simulation"]
        
        content = []
        
        content.append(Paragraph("Resultados da Simulação", self.subtitle_style))
        
        # Status geral
        status_color = "green" if simulation.status == "completed" else "red" if simulation.status == "failed" else "orange"
        status_text = f"Status: <font color='{status_color}'>{simulation.status.upper()}</font>"
        content.append(Paragraph(status_text, self.normal_style))
        content.append(Spacer(1, 15))
        
        # Resultados principais
        if simulation.results:
            content.append(Paragraph("Resultados Obtidos", self.subtitle_style))
            
            # Formatar resultados baseado no tipo
            if simulation.tipo_simulacao == "drop_test":
                content.extend(self._format_drop_test_results(simulation.results))
            elif simulation.tipo_simulacao == "stress_test":
                content.extend(self._format_stress_test_results(simulation.results))
            elif simulation.tipo_simulacao == "motion":
                content.extend(self._format_motion_test_results(simulation.results))
            elif simulation.tipo_simulacao == "fluid":
                content.extend(self._format_fluid_test_results(simulation.results))
        
        # Métricas calculadas
        if simulation.metrics:
            content.append(Spacer(1, 20))
            content.append(Paragraph("Métricas Calculadas", self.subtitle_style))
            
            metrics_data = [["Métrica", "Valor", "Unidade"]]
            
            for key, value in simulation.metrics.items():
                metric_name = key.replace("_", " ").title()
                unit = self._get_metric_unit(key)
                metrics_data.append([metric_name, str(value), unit])
            
            metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 1*inch])
            metrics_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
            ]))
            
            content.append(metrics_table)
        
        return ReportSection("Resultados da Simulação", content)

    def _format_drop_test_results(self, results: Dict[str, Any]) -> List[Any]:
        """Formatar resultados do teste de queda"""
        content = []
        
        testes = results.get("testes", [])
        if not testes:
            content.append(Paragraph("Nenhum teste de queda foi executado.", self.normal_style))
            return content
        
        content.append(Paragraph(f"Foram executados {len(testes)} testes de queda.", self.normal_style))
        content.append(Spacer(1, 10))
        
        # Tabela de resultados individuais
        test_data = [["Teste", "Altura (m)", "Vel. Impacto (m/s)", "Rebotes", "Tempo (s)"]]
        
        for i, teste in enumerate(testes):
            test_data.append([
                str(i + 1),
                f"{teste.get('altura_queda', 0):.2f}",
                f"{abs(teste.get('velocidade_impacto', 0)):.2f}",
                str(teste.get('rebotes', 0)),
                f"{teste.get('tempo_ate_repouso', 0):.2f}"
            ])
        
        test_table = Table(test_data, colWidths=[0.8*inch, 1*inch, 1.2*inch, 0.8*inch, 1*inch])
        test_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))
        
        content.append(test_table)
        
        return content

    def _format_stress_test_results(self, results: Dict[str, Any]) -> List[Any]:
        """Formatar resultados do teste de stress"""
        content = []
        
        testes_forca = results.get("testes_forca", [])
        if not testes_forca:
            content.append(Paragraph("Nenhum teste de stress foi executado.", self.normal_style))
            return content
        
        content.append(Paragraph(f"Foram executados testes de stress com força crescente até {testes_forca[-1]['forca'] if testes_forca else 0}N.", self.normal_style))
        content.append(Spacer(1, 10))
        
        # Tabela de resultados
        stress_data = [["Força (N)", "Deslocamento (m)", "Velocidade Final (m/s)"]]
        
        for teste in testes_forca[::3]:  # Mostrar apenas alguns pontos para não sobrecarregar
            stress_data.append([
                f"{teste.get('forca', 0):.0f}",
                f"{teste.get('deslocamento', 0):.3f}",
                f"{np.linalg.norm(teste.get('velocidade_final', [0,0,0])):.2f}"
            ])
        
        stress_table = Table(stress_data, colWidths=[1.5*inch, 1.5*inch, 2*inch])
        stress_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(stress_table)
        
        # Ponto de ruptura
        if results.get("ponto_ruptura"):
            content.append(Spacer(1, 10))
            content.append(Paragraph(f"<b>Ponto de Ruptura:</b> {results['ponto_ruptura']:.0f}N", self.normal_style))
        
        return content

    def _format_motion_test_results(self, results: Dict[str, Any]) -> List[Any]:
        """Formatar resultados do teste de movimento"""
        content = []
        
        trajetoria = results.get("trajetoria", [])
        if not trajetoria:
            content.append(Paragraph("Nenhum teste de movimento foi executado.", self.normal_style))
            return content
        
        content.append(Paragraph(f"Foram coletados {len(trajetoria)} pontos de trajetória.", self.normal_style))
        content.append(Spacer(1, 10))
        
        # Estatísticas da trajetória
        metrics = results.get("metricas", {})
        if metrics:
            content.append(Paragraph("Métricas da Trajetória:", self.subtitle_style))
            
            motion_data = [
                ["Métrica", "Valor"],
                ["Energia Total", f"{metrics.get('energia_total', 0):.2f} J"],
                ["Distância Percorrida", f"{metrics.get('distancia_percorrida', 0):.2f} m"],
                ["Velocidade Média", f"{metrics.get('velocidade_media', 0):.2f} m/s"]
            ]
            
            motion_table = Table(motion_data, colWidths=[2*inch, 2.5*inch])
            motion_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
            ]))
            
            content.append(motion_table)
        
        return content

    def _format_fluid_test_results(self, results: Dict[str, Any]) -> List[Any]:
        """Formatar resultados do teste de fluido"""
        content = []
        
        resistencia = results.get("resistencia", [])
        if not resistencia:
            content.append(Paragraph("Nenhum teste de fluido foi executado.", self.normal_style))
            return content
        
        content.append(Paragraph("Análise de Resistência do Fluido", self.subtitle_style))
        content.append(Spacer(1, 10))
        
        # Métricas do fluido
        metrics = results.get("metricas", {})
        if metrics:
            fluid_data = [
                ["Propriedade", "Valor"],
                ["Velocidade Terminal", f"{metrics.get('velocidade_terminal', 0):.2f} m/s"],
                ["Coeficiente de Arrasto", f"{metrics.get('coeficiente_arrasto', 0):.3f}"],
                ["Classificação Aerodinâmica", metrics.get('classificacao_aerodinamica', 'N/A').replace('_', ' ').title()]
            ]
            
            fluid_table = Table(fluid_data, colWidths=[2.5*inch, 2.5*inch])
            fluid_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
            ]))
            
            content.append(fluid_table)
        
        return content

    def _get_metric_unit(self, metric_name: str) -> str:
        """Obter unidade da métrica"""
        unit_mapping = {
            "velocidade_impacto_media": "m/s",
            "velocidade_impacto_max": "m/s",
            "velocidade_impacto_min": "m/s",
            "forca_maxima": "N",
            "deslocamento_maximo": "m",
            "rigidez_calculada": "N/m",
            "energia_total": "J",
            "distancia_percorrida": "m",
            "velocidade_media": "m/s",
            "velocidade_terminal": "m/s",
            "coeficiente_arrasto": "",
            "numero_testes": "",
            "rebotes_medio": ""
        }
        
        return unit_mapping.get(metric_name, "")

    def _build_analysis_section(self, data: Dict[str, Any]) -> ReportSection:
        """Construir seção de análise"""
        simulation = data["simulation"]
        
        content = []
        
        content.append(Paragraph("Análise e Recomendações", self.subtitle_style))
        
        # Análise baseada no tipo e resultados
        if simulation.tipo_simulacao == "drop_test" and simulation.metrics:
            content.extend(self._analyze_drop_test(simulation.metrics))
        elif simulation.tipo_simulacao == "stress_test" and simulation.metrics:
            content.extend(self._analyze_stress_test(simulation.metrics))
        elif simulation.tipo_simulacao == "motion" and simulation.metrics:
            content.extend(self._analyze_motion_test(simulation.metrics))
        elif simulation.tipo_simulacao == "fluid" and simulation.metrics:
            content.extend(self._analyze_fluid_test(simulation.metrics))
        else:
            content.append(Paragraph("Análise detalhada não disponível devido à ausência de métricas calculadas.", self.normal_style))
        
        # Recomendações gerais
        content.append(Spacer(1, 15))
        content.append(Paragraph("Recomendações Gerais", self.subtitle_style))
        
        recommendations = self._generate_recommendations(simulation)
        for rec in recommendations:
            content.append(Paragraph(f"• {rec}", self.normal_style))
        
        return ReportSection("Análise e Recomendações", content)

    def _analyze_drop_test(self, metrics: Dict[str, Any]) -> List[Any]:
        """Análise específica para teste de queda"""
        content = []
        
        classificacao = metrics.get("classificacao_resistencia", "indefinido")
        vel_media = metrics.get("velocidade_impacto_media", 0)
        rebotes_medio = metrics.get("rebotes_medio", 0)
        
        # Análise do comportamento
        analysis_text = f"""
        <b>Análise do Comportamento:</b><br/>
        O modelo apresentou comportamento '{classificacao.replace('_', ' ')}' durante os testes de queda. 
        A velocidade média de impacto foi de {vel_media:.2f} m/s, com {rebotes_medio:.1f} rebotes em média.
        """
        
        if classificacao == "resistente":
            analysis_text += """
            <br/><br/><b>Interpretação:</b><br/>
            O modelo demonstrou boa capacidade de absorver impactos sem sofrer danos estruturais significativos. 
            A estrutura é adequada para aplicações que requerem resistência a quedas moderadas.
            """
        elif classificacao == "frágil":
            analysis_text += """
            <br/><br/><b>Interpretação:</b><br/>
            O modelo apresentou fragilidade sob impacto. Recomenda-se revisar o design estrutural ou 
            considerar o uso de materiais mais resistentes para aplicações críticas.
            """
        
        content.append(Paragraph(analysis_text, self.normal_style))
        
        return content

    def _analyze_stress_test(self, metrics: Dict[str, Any]) -> List[Any]:
        """Análise específica para teste de stress"""
        content = []
        
        classificacao = metrics.get("classificacao_resistencia", "indefinido")
        forca_max = metrics.get("forca_maxima", 0)
        rigidez = metrics.get("rigidez_calculada", 0)
        
        analysis_text = f"""
        <b>Análise Estrutural:</b><br/>
        O modelo demonstrou resistência '{classificacao.replace('_', ' ')}' com força máxima aplicada de {forca_max:.0f}N. 
        A rigidez calculada é de {rigidez:.2f} N/m, indicando {'alta' if rigidez > 1000 else 'moderada' if rigidez > 100 else 'baixa'} rigidez estrutural.
        """
        
        if metrics.get("ponto_ruptura"):
            analysis_text += f"""
            <br/><br/><b>Ponto de Ruptura:</b><br/>
            O modelo破了 a {metrics['ponto_ruptura']:.0f}N, o que estabelece o limite máximo de carga segura.
            """
        
        content.append(Paragraph(analysis_text, self.normal_style))
        
        return content

    def _analyze_motion_test(self, metrics: Dict[str, Any]) -> List[Any]:
        """Análise específica para teste de movimento"""
        content = []
        
        energia = metrics.get("energia_total", 0)
        distancia = metrics.get("distancia_percorrida", 0)
        
        analysis_text = f"""
        <b>Análise de Movimento:</b><br/>
        A trajetória foi executada com consumo total de energia de {energia:.2f}J ao longo de {distancia:.2f}m. 
        {'O modelo demonstrou boa eficiência energética.' if energia < 50 else 'O consumo energético foi elevado, indicando oportunidades de otimização.'}
        """
        
        content.append(Paragraph(analysis_text, self.normal_style))
        
        return content

    def _analyze_fluid_test(self, metrics: Dict[str, Any]) -> List[Any]:
        """Análise específica para teste de fluido"""
        content = []
        
        vel_terminal = metrics.get("velocidade_terminal", 0)
        coef_arrasto = metrics.get("coeficiente_arrasto", 0.47)
        classificacao = metrics.get("classificacao_aerodinamica", "indefinido")
        
        analysis_text = f"""
        <b>Análise Aerodinâmica:</b><br/>
        O modelo apresentou velocidade terminal de {vel_terminal:.2f} m/s com coeficiente de arrasto de {coef_arrasto:.3f}. 
        A classificação aerodinâmica é '{classificacao.replace('_', ' ')}'.
        """
        
        if classificacao == "aerodinamico":
            analysis_text += """
            <br/><br/><b>Interpretação:</b><br/>
            O design é aerodinamicamente eficiente, adequado para aplicações que requerem movimento em fluidos.
            """
        elif classificacao == "arrasto_alto":
            analysis_text += """
            <br/><br/><b>Interpretação:</b><br/>
            O modelo apresenta alto arrasto. Considere otimizações no design para reduzir a resistência do fluido.
            """
        
        content.append(Paragraph(analysis_text, self.normal_style))
        
        return content

    def _generate_recommendations(self, simulation: Simulation) -> List[str]:
        """Gerar recomendações baseadas na simulação"""
        recommendations = []
        
        # Recomendações baseadas no status
        if simulation.status == "failed":
            recommendations.append("Revisar os parâmetros de simulação e verificar a integridade do modelo 3D.")
            recommendations.append("Verificar se o modelo 3D está em um formato suportado (STL, GLTF, GLB).")
        
        # Recomendações baseadas no tipo
        if simulation.tipo_simulacao == "drop_test":
            recommendations.append("Para aplicações críticas, considerar testes com diferentes materiais e espessuras.")
            recommendations.append("Implementar simulações com diferentes tipos de superfície de impacto.")
        
        elif simulation.tipo_simulacao == "stress_test":
            recommendations.append("Validar os resultados com testes físicos reais quando possível.")
            recommendations.append("Considerar simulações de fadiga para aplicações de longa duração.")
        
        elif simulation.tipo_simulacao == "motion":
            recommendations.append("Otimizar a trajetória para reduzir o consumo energético quando possível.")
            recommendations.append("Considerar simulações com diferentes velocidades e acelerações.")
        
        elif simulation.tipo_simulacao == "fluid":
            recommendations.append("Para aplicações em fluidos reais, considerar validação experimental.")
            recommendations.append("Avaliar o desempenho em diferentes densidades de fluido.")
        
        # Recomendações gerais
        recommendations.append("Salvar os resultados para comparação com futuras iterações do design.")
        recommendations.append("Documentar as lições aprendidas para projetos similares.")
        
        return recommendations

    async def _build_charts_section(self, db: Session, data: Dict[str, Any]) -> ReportSection:
        """Construir seção de gráficos"""
        simulation = data["simulation"]
        
        content = []
        chart_files = []
        
        content.append(Paragraph("Gráficos e Visualizações", self.subtitle_style))
        
        # Gerar gráficos baseados no tipo de simulação
        if simulation.tipo_simulacao == "drop_test" and simulation.results:
            chart_path = await self._create_drop_test_chart(simulation.results)
            if chart_path:
                chart_files.append(chart_path)
                content.append(Paragraph("Gráfico 1: Velocidade de Impacto por Teste", self.normal_style))
        
        elif simulation.tipo_simulacao == "stress_test" and simulation.results:
            chart_path = await self._create_stress_test_chart(simulation.results)
            if chart_path:
                chart_files.append(chart_path)
                content.append(Paragraph("Gráfico 1: Curva Força vs Deslocamento", self.normal_style))
        
        elif simulation.tipo_simulacao == "motion" and simulation.results:
            chart_path = await self._create_motion_chart(simulation.results)
            if chart_path:
                chart_files.append(chart_path)
                content.append(Paragraph("Gráfico 1: Trajetória e Energia", self.normal_style))
        
        elif simulation.tipo_simulacao == "fluid" and simulation.results:
            chart_path = await self._create_fluid_chart(simulation.results)
            if chart_path:
                chart_files.append(chart_path)
                content.append(Paragraph("Gráfico 1: Resistência vs Velocidade", self.normal_style))
        
        if not chart_files:
            content.append(Paragraph("Nenhum gráfico pôde ser gerado para esta simulação.", self.normal_style))
        
        return ReportSection("Gráficos e Visualizações", content, chart_files)

    async def _create_drop_test_chart(self, results: Dict[str, Any]) -> Optional[str]:
        """Criar gráfico para teste de queda"""
        try:
            testes = results.get("testes", [])
            if not testes:
                return None
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Gráfico 1: Velocidade de impacto
            velocidades = [abs(t.get("velocidade_impacto", 0)) for t in testes]
            ax1.bar(range(1, len(velocidades) + 1), velocidades, color='skyblue', alpha=0.7)
            ax1.set_xlabel('Número do Teste')
            ax1.set_ylabel('Velocidade de Impacto (m/s)')
            ax1.set_title('Velocidade de Impacto por Teste')
            ax1.grid(True, alpha=0.3)
            
            # Gráfico 2: Rebotes
            rebotes = [t.get("rebotes", 0) for t in testes]
            ax2.bar(range(1, len(rebotes) + 1), rebotes, color='orange', alpha=0.7)
            ax2.set_xlabel('Número do Teste')
            ax2.set_ylabel('Número de Rebotes')
            ax2.set_title('Rebotes por Teste')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Salvar gráfico
            chart_path = self.reports_path / f"drop_test_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de teste de queda: {e}")
            return None

    async def _create_stress_test_chart(self, results: Dict[str, Any]) -> Optional[str]:
        """Criar gráfico para teste de stress"""
        try:
            testes = results.get("testes_forca", [])
            if not testes:
                return None
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Gráfico 1: Curva força vs deslocamento
            forcas = [t.get("forca", 0) for t in testes]
            deslocamentos = [t.get("deslocamento", 0) for t in testes]
            
            ax1.plot(deslocamentos, forcas, 'b-', linewidth=2, marker='o', markersize=4)
            ax1.set_xlabel('Deslocamento (m)')
            ax1.set_ylabel('Força Aplicada (N)')
            ax1.set_title('Curva Força vs Deslocamento')
            ax1.grid(True, alpha=0.3)
            
            # Destacar ponto de ruptura
            if results.get("ponto_ruptura"):
                ax1.axhline(y=results["ponto_ruptura"], color='red', linestyle='--', 
                           label=f'Ponto de Ruptura: {results["ponto_ruptura"]:.0f}N')
                ax1.legend()
            
            # Gráfico 2: Velocidade final
            velocidades = [np.linalg.norm(t.get("velocidade_final", [0,0,0])) for t in testes]
            ax2.plot(forcas, velocidades, 'g-', linewidth=2, marker='s', markersize=4)
            ax2.set_xlabel('Força Aplicada (N)')
            ax2.set_ylabel('Velocidade Final (m/s)')
            ax2.set_title('Velocidade Final vs Força')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            chart_path = self.reports_path / f"stress_test_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de teste de stress: {e}")
            return None

    async def _create_motion_chart(self, results: Dict[str, Any]) -> Optional[str]:
        """Criar gráfico para teste de movimento"""
        try:
            trajetoria = results.get("trajetoria", [])
            if not trajetoria:
                return None
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Gráfico 1: Trajetória 3D (projecção 2D)
            x_positions = [p.get("posicao", [0,0,0])[0] for p in trajetoria]
            y_positions = [p.get("posicao", [0,0,0])[1] for p in trajetoria]
            
            ax1.plot(x_positions, y_positions, 'b-', linewidth=2)
            ax1.set_xlabel('Posição X (m)')
            ax1.set_ylabel('Posição Y (m)')
            ax1.set_title('Trajetória 2D')
            ax1.grid(True, alpha=0.3)
            ax1.axis('equal')
            
            # Gráfico 2: Energia ao longo do tempo
            tempos = [p.get("tempo", 0) for p in trajetoria]
            energias = [p.get("energia_potencial", 0) for p in trajetoria]
            
            ax2.plot(tempos, energias, 'r-', linewidth=2)
            ax2.set_xlabel('Tempo (s)')
            ax2.set_ylabel('Energia Potencial (J)')
            ax2.set_title('Energia ao Longo do Tempo')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            chart_path = self.reports_path / f"motion_test_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de teste de movimento: {e}")
            return None

    async def _create_fluid_chart(self, results: Dict[str, Any]) -> Optional[str]:
        """Criar gráfico para teste de fluido"""
        try:
            resistencia = results.get("resistencia", [])
            if not resistencia:
                return None
            
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            
            # Gráfico: Resistência vs Velocidade
            velocidades = [r.get("velocidade", 0) for r in resistencia]
            forcas_arrasto = [r.get("forca_arrasto", 0) for r in resistencia]
            
            ax.plot(velocidades, forcas_arrasto, 'purple', linewidth=2, marker='o', markersize=3)
            ax.set_xlabel('Velocidade (m/s)')
            ax.set_ylabel('Força de Arrasto (N)')
            ax.set_title('Resistência do Fluido vs Velocidade')
            ax.grid(True, alpha=0.3)
            
            # Destacar velocidade terminal
            metrics = results.get("metricas", {})
            if metrics.get("velocidade_terminal"):
                ax.axvline(x=metrics["velocidade_terminal"], color='red', linestyle='--',
                          label=f'Velocidade Terminal: {metrics["velocidade_terminal"]:.2f} m/s')
                ax.legend()
            
            plt.tight_layout()
            
            chart_path = self.reports_path / f"fluid_test_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de teste de fluido: {e}")
            return None

    def _build_technical_data_section(self, data: Dict[str, Any]) -> ReportSection:
        """Construir seção de dados técnicos detalhados"""
        simulation = data["simulation"]
        
        content = []
        
        content.append(Paragraph("Dados Técnicos Detalhados", self.subtitle_style))
        
        # Parâmetros completos da simulação
        content.append(Paragraph("Parâmetros da Simulação", self.subtitle_style))
        
        params_text = json.dumps(simulation.parametros, indent=2, ensure_ascii=False)
        content.append(Paragraph(f"<pre>{params_text}</pre>", self.code_style))
        content.append(Spacer(1, 20))
        
        # Resultados completos
        if simulation.results:
            content.append(Paragraph("Resultados Completos", self.subtitle_style))
            
            results_text = json.dumps(simulation.results, indent=2, ensure_ascii=False, default=str)
            # Truncar se muito longo
            if len(results_text) > 5000:
                results_text = results_text[:5000] + "\n\n... (resultados truncados para evitar sobrecarga)"
            
            content.append(Paragraph(f"<pre>{results_text}</pre>", self.code_style))
            content.append(Spacer(1, 20))
        
        # Métricas técnicas
        if simulation.metrics:
            content.append(Paragraph("Métricas Técnicas", self.subtitle_style))
            
            metrics_text = json.dumps(simulation.metrics, indent=2, ensure_ascii=False)
            content.append(Paragraph(f"<pre>{metrics_text}</pre>", self.code_style))
        
        return ReportSection("Dados Técnicos Detalhados", content)

    def _build_conclusions_section(self, data: Dict[str, Any]) -> ReportSection:
        """Construir seção de conclusões"""
        simulation = data["simulation"]
        
        content = []
        
        content.append(Paragraph("Conclusões", self.subtitle_style))
        
        # Conclusões baseadas no tipo de simulação
        if simulation.status == "completed":
            if simulation.tipo_simulacao == "drop_test":
                conclusions = [
                    "O modelo foi submetido a testes de queda conforme especificado.",
                    "Os resultados indicam o comportamento esperado sob impacto.",
                    "A análise confirma a adequação do design para aplicações residenciais/industriais.",
                    "Recomenda-se a validação com testes físicos para aplicações críticas."
                ]
            elif simulation.tipo_simulacao == "stress_test":
                conclusions = [
                    "O modelo foi testado sob cargas crescentes até o limite estrutural.",
                    "A curva força-deslocamento segue o comportamento esperado para o material.",
                    "O ponto de ruptura foi identificado e estabelece o limite de segurança.",
                    "O design é adequado para as cargas especificadas na aplicação."
                ]
            elif simulation.tipo_simulacao == "motion":
                conclusions = [
                    "A trajetória especificada foi executada com sucesso.",
                    "O consumo energético está dentro dos parâmetros esperados.",
                    "O modelo demonstrou estabilidade durante o movimento.",
                    "A eficiência energética pode ser otimizada em futuras iterações."
                ]
            elif simulation.tipo_simulacao == "fluid":
                conclusions = [
                    "O comportamento do modelo em fluido foi analisado conforme especificado.",
                    "Os coeficientes de arrasto estão dentro dos parâmetros esperados.",
                    "A velocidade terminal foi determinada com precisão.",
                    "O design pode ser otimizado para melhorar a eficiência aerodinâmica."
                ]
            else:
                conclusions = [
                    "A simulação foi executada com sucesso.",
                    "Todos os testes foram concluídos conforme especificado.",
                    "Os resultados são consistentes e dentro dos parâmetros esperados.",
                    "O modelo atende aos requisitos de performance especificados."
                ]
        else:
            conclusions = [
                "A simulação não foi concluída devido a erros durante a execução.",
                "Recomenda-se revisar os parâmetros e o modelo 3D antes de uma nova tentativa.",
                "Verificar se o arquivo do modelo está em um formato suportado.",
                "Considerar simplificações no modelo para reduzir a complexidade computacional."
            ]
        
        for conclusion in conclusions:
            content.append(Paragraph(f"• {conclusion}", self.normal_style))
        
        content.append(Spacer(1, 20))
        
        # Próximos passos
        content.append(Paragraph("Próximos Passos", self.subtitle_style))
        
        next_steps = [
            "Validar os resultados com testes físicos quando possível.",
            "Considerar simulações adicionais com diferentes parâmetros.",
            "Otimizar o design baseado nas análises realizadas.",
            "Documentar as lições aprendidas para projetos similares."
        ]
        
        for step in next_steps:
            content.append(Paragraph(f"• {step}", self.normal_style))
        
        return ReportSection("Conclusões", content)

    def _build_appendices(self, data: Dict[str, Any]) -> List[Any]:
        """Construir apêndices"""
        content = []
        
        content.append(Spacer(1, 40))
        content.append(Paragraph("Apêndice A - Informações do Sistema", self.subtitle_style))
        
        # Informações técnicas do sistema
        system_info = [
            ["Propriedade", "Valor"],
            ["Versão do Software", "3dPot v2.0"],
            ["Engine de Física", "PyBullet"],
            ["Versão do PyBullet", "7.x"],
            ["Data de Geração", datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
            ["Engine de Relatórios", "ReportLab + Matplotlib"],
            ["Resolução de Gráficos", "300 DPI"],
            ["Formato de Saída", "PDF/A-1b"]
        ]
        
        system_table = Table(system_info, colWidths=[2.5*inch, 2.5*inch])
        system_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(system_table)
        
        # Aviso legal
        content.append(Spacer(1, 20))
        content.append(Paragraph("Aviso Legal", self.subtitle_style))
        
        legal_text = """
        Este relatório foi gerado automaticamente pelo sistema 3dPot v2.0. 
        Os resultados da simulação são baseados em modelos matemáticos e físicos que podem não refletir 
        exatamente o comportamento do mundo real. Recomenda-se sempre validar os resultados com testes 
        físicos para aplicações críticas. O 3dPot não se responsabiliza por decisões tomadas baseadas 
        exclusivamente nos resultados de simulação.
        """
        
        content.append(Paragraph(legal_text, self.normal_style))
        
        return content

    # ========== MÉTODOS PÚBLICOS ==========

    def generate_summary_report(
        self, 
        db: Session, 
        simulations: List[UUID],
        title: str = "Relatório Comparativo de Simulações"
    ) -> str:
        """
        Gerar relatório comparativo de múltiplas simulações
        
        Args:
            db: Sessão do banco de dados
            simulations: Lista de IDs das simulações
            title: Título do relatório
            
        Returns:
            Caminho para o arquivo PDF gerado
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_comparativo_{timestamp}.pdf"
            filepath = self.reports_path / filename
            
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            
            # Título
            story.append(Paragraph(title, self.title_style))
            story.append(Spacer(1, 30))
            
            # Dados das simulações
            sim_data = []
            for sim_id in simulations:
                sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
                if sim:
                    sim_data.append({
                        "nome": sim.nome,
                        "tipo": sim.tipo_simulacao,
                        "status": sim.status,
                        "criado": sim.created_at.strftime("%d/%m/%Y"),
                        "duration": f"{sim.duration:.1f}s" if sim.duration else "N/A"
                    })
            
            # Tabela comparativa
            if sim_data:
                comparison_data = [["Nome", "Tipo", "Status", "Data", "Duração"]]
                for sim in sim_data:
                    comparison_data.append([
                        sim["nome"][:30] + "..." if len(sim["nome"]) > 30 else sim["nome"],
                        sim["tipo"].replace("_", " ").title(),
                        sim["status"].title(),
                        sim["criado"],
                        sim["duration"]
                    ])
                
                comparison_table = Table(comparison_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
                comparison_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
                ]))
                
                story.append(comparison_table)
            
            doc.build(story)
            
            logger.info(f"Relatório comparativo gerado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório comparativo: {e}")
            raise

    def cleanup_old_reports(self, days: int = 30) -> int:
        """
        Limpar relatórios antigos
        
        Args:
            days: Número de dias para manter os relatórios
            
        Returns:
            Número de arquivos removidos
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
            removed_count = 0
            
            for report_file in self.reports_path.glob("*.pdf"):
                if report_file.stat().st_mtime < cutoff_date:
                    report_file.unlink()
                    removed_count += 1
            
            logger.info(f"Limpeza concluída: {removed_count} relatórios antigos removidos")
            return removed_count
            
        except Exception as e:
            logger.error(f"Erro na limpeza de relatórios: {e}")
            return 0