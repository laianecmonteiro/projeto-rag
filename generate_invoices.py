import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_invoices():
    os.makedirs("data/invoices", exist_ok=True)
    
    invoices_data = [
        {
            "filename": "NF_001_VoltCharge_Equipamentos.pdf",
            "number": "NF-001045",
            "provider": "VoltCharge Indústria de Carregadores V.E. S.A.",
            "cnpj": "14.238.901/0001-44",
            "date": "10/02/2026",
            "items": [
                ["Item", "Descrição", "Qtd", "Valor Unit.", "Total"],
                ["1", "Wallbox Residencial 7.4kW Monofásico Tipo 2 (com Wi-Fi/App)", "5", "R$ 4.200,00", "R$ 21.000,00"],
                ["2", "Carregador Comercial AC 22kW Trifásico com Leitor RFID OCPP 1.6", "2", "R$ 8.900,00", "R$ 17.800,00"],
                ["3", "Cabo de Extensão de Recarga Tipo 2 para Tipo 2 (32A, 5 metros)", "8", "R$ 850,00", "R$ 6.800,00"]
            ],
            "subtotal": "R$ 45.600,00",
            "tax": "R$ 4.104,00",
            "total": "R$ 45.600,00",
            "notes": "Equipamentos certificados pelo INMETRO com proteção IP54 contra chuva e poeira. Garantia de 3 anos inclusa para todos os carregadores Wallbox."
        },
        {
            "filename": "NF_002_FastEletro_EstacoesDC.pdf",
            "number": "NF-002389",
            "provider": "FastEletro Estações de Recarga Rápida Ltda",
            "cnpj": "28.712.345/0001-88",
            "date": "20/02/2026",
            "items": [
                ["Item", "Descrição", "Qtd", "Valor Unit.", "Total"],
                ["1", "Estação de Carga Ultrarrápida DC 60kW Conector Duplo CCS2/CHAdeMO", "1", "R$ 78.000,00", "R$ 78.000,00"],
                ["2", "Módulo de Balanceamento de Carga Dinâmica (DLM Inteligente)", "1", "R$ 6.500,00", "R$ 6.500,00"],
                ["3", "Totem Metálico Protetor com Painel Publicitário LED 10 Polegadas", "1", "R$ 4.800,00", "R$ 4.800,00"]
            ],
            "subtotal": "R$ 89.300,00",
            "tax": "R$ 8.037,00",
            "total": "R$ 89.300,00",
            "notes": "Destinado à implantação do Hub Eletroposto Rodovia Anhanguera KM 42. Suporte técnico 24/7 e telemetria remota por protocolo OCPP."
        },
        {
            "filename": "NF_003_SolarPower_Instalacao.pdf",
            "number": "NF-003112",
            "provider": "EletroGrid Engenharia e Infraestrutura Elétrica ME",
            "cnpj": "39.845.612/0001-09",
            "date": "02/03/2026",
            "items": [
                ["Item", "Descrição", "Qtd", "Valor Unit.", "Total"],
                ["1", "Transformador Trifásico a Seco 75kVA (Rede 220V/380V)", "1", "R$ 16.500,00", "R$ 16.500,00"],
                ["2", "Quadro Geral de Distribuição QG-VE com DPS Classe II e DR Tipo B", "2", "R$ 3.400,00", "R$ 6.800,00"],
                ["3", "Cabeamento de Cobre 35mm² Especial Anti-chama para V.E. (100m)", "3", "R$ 1.950,00", "R$ 5.850,00"]
            ],
            "subtotal": "R$ 29.150,00",
            "tax": "R$ 2.623,50",
            "total": "R$ 29.150,00",
            "notes": "Serviço de adequação de infraestrutura predial para 12 vagas com carregadores elétricos em condomínio residencial. Emissão de ART de instalação inclusa."
        },
        {
            "filename": "NF_004_EcoMobility_Servicos.pdf",
            "number": "NF-004870",
            "provider": "EcoMobility Software de Gestão e Eletromobilidade S.A.",
            "cnpj": "42.110.987/0001-33",
            "date": "12/03/2026",
            "items": [
                ["Item", "Descrição", "Qtd", "Valor Unit.", "Total"],
                ["1", "Licença Anual de Software SaaS para Gestão de Eletropostos (10 pontos)", "1", "R$ 7.200,00", "R$ 7.200,00"],
                ["2", "Lote com 100 Cartões RFID Customizados para Autenticação de Usuários", "1", "R$ 1.500,00", "R$ 1.500,00"],
                ["3", "Treinamento Técnico Presencial para Operação e Manutenção Preventiva", "2", "R$ 1.800,00", "R$ 3.600,00"]
            ],
            "subtotal": "R$ 12.300,00",
            "tax": "R$ 1.107,00",
            "total": "R$ 12.300,00",
            "notes": "Integração via API com gateway de pagamento PIX e cartão para cobrança automática por kWh consumido em condomínios e estacionamentos comerciais."
        }
    ]

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )
    body_style = ParagraphStyle(
        'InvoiceBody',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    bold_style = ParagraphStyle(
        'InvoiceBold',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica-Bold'
    )

    for inv in invoices_data:
        filepath = os.path.join("data", "invoices", inv["filename"])
        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements = []

        # Cabeçalho
        elements.append(Paragraph(f"<b>DANFE - DOCUMENTO AUXILIAR DE NOTA FISCAL ELETRÔNICA</b>", title_style))
        elements.append(Paragraph(f"Número da Nota: <b>{inv['number']}</b> | Série: 1 | Emissão: <b>{inv['date']}</b>", subtitle_style))
        elements.append(Spacer(1, 10))

        # Dados do Fornecedor e Emitente
        info_data = [
            [
                Paragraph(f"<b>EMITENTE / FORNECEDOR:</b><br/>{inv['provider']}<br/>CNPJ: {inv['cnpj']}<br/>Inscrição Estadual: 109.876.543.110", body_style),
                Paragraph(f"<b>DESTINATÁRIO:</b><br/>RAG Laiane Eletromobilidade & Carregadores Ltda<br/>CNPJ: 00.987.654/0001-99<br/>Endereço: Av. dos Veículos Elétricos, 500 - Polo Tecnológico", body_style)
            ]
        ]
        info_table = Table(info_data, colWidths=[270, 270])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 15))

        # Tabela de Itens / Produtos
        items_table_data = []
        for i, row in enumerate(inv["items"]):
            if i == 0:
                items_table_data.append([Paragraph(f"<b>{col}</b>", bold_style) for col in row])
            else:
                items_table_data.append([Paragraph(col, body_style) for col in row])

        items_table = Table(items_table_data, colWidths=[35, 260, 45, 100, 100])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF2F6')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#3B82F6')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 15))

        # Totais
        totals_data = [
            [Paragraph("<b>Subtotal dos Produtos:</b>", body_style), Paragraph(inv['subtotal'], bold_style)],
            [Paragraph("<b>Impostos Retidos (ICMS/ISS/IPI):</b>", body_style), Paragraph(inv['tax'], body_style)],
            [Paragraph("<b>VALOR TOTAL DA NOTA:</b>", bold_style), Paragraph(f"<b>{inv['total']}</b>", bold_style)]
        ]
        totals_table = Table(totals_data, colWidths=[400, 140])
        totals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F1F5F9')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 15))

        # Informações Adicionais
        notes_p = Paragraph(f"<b>INFORMAÇÕES COMPLEMENTARES / OBSERVAÇÕES:</b><br/>{inv['notes']}", body_style)
        notes_table = Table([[notes_p]], colWidths=[540])
        notes_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(notes_table)

        doc.build(elements)
        print(f"[OK] Gerado documento de carregadores elétricos: {filepath}")

if __name__ == "__main__":
    create_invoices()
