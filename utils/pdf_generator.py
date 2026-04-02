from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from io import BytesIO
from datetime import datetime

def generate_scorecard_pdf(match):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=26,
        alignment=1,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=20
    )

    result_box_style = ParagraphStyle(
        'ResultBoxStyle',
        parent=styles['Normal'],
        fontSize=16,
        alignment=1,
        textColor=colors.white,
        backgroundColor=colors.HexColor("#3b82f6"),
        borderPadding=10,
        borderRadius=5,
        spaceBefore=20,
        spaceAfter=20
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=20,
        spaceAfter=10,
        borderBottomWidth=1,
        borderBottomColor=colors.HexColor("#e2e8f0")
    )

    motm_box_style = ParagraphStyle(
        'MOTMBoxStyle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        textColor=colors.black,
        backgroundColor=colors.HexColor("#FFF9C4"), # Light Gold
        borderPadding=8,
        borderWidth=1,
        borderColor=colors.HexColor("#FFD700"), # Gold Border
        borderRadius=4,
        spaceBefore=15,
        spaceAfter=15
    )

    # 1. Header
    elements.append(Paragraph("🏏 TSE SmartCric Scorer", title_style))
    elements.append(Paragraph(f"{match.team_a.name} VS {match.team_b.name}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=20))

    # 2. Result Summary Box
    if match.is_finished:
        res_text = f"<b>MATCH RESULT: {match.status_message.upper()}</b>"
        elements.append(Paragraph(res_text, result_box_style))
        
        # Man of the Match Highlight
        motm_player, motm_points = match.man_of_the_match
        
        # Build Stats String
        stats_parts = []
        if motm_player.balls_faced > 0:
            stats_parts.append(f"Batting: {motm_player.runs}({motm_player.balls_faced})")
        if motm_player.balls_bowled > 0:
            stats_parts.append(f"Bowling: {motm_player.wickets_taken}/{motm_player.runs_conceded} ({motm_player.overs_formatted})")
            
        stats_str = " | ".join(stats_parts)
        if stats_str:
            motm_text = f"🏆 <b>MAN OF THE MATCH: {motm_player.name.upper()}</b><br/><font size='10' color='#475569'>{stats_str} | Points: {motm_points}</font>"
        else:
            motm_text = f"🏆 <b>MAN OF THE MATCH: {motm_player.name.upper()}</b> | Points: {motm_points}"

        elements.append(Paragraph(motm_text, motm_box_style))
        
        # Winner/Loser explicit mention
        winner_loser_data = [
            [Paragraph(f"<b>WINNER:</b> {match.winner_name}", styles['Normal']), 
             Paragraph(f"<b>LOSER:</b> {match.loser_name if match.loser_name else 'N/A'}", styles['Normal'])]
        ]
        wl_table = Table(winner_loser_data, colWidths=[250, 250])
        wl_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(wl_table)
    else:
        elements.append(Paragraph(f"<b>STATUS: {match.status_message}</b>", result_box_style))

    elements.append(Spacer(1, 20))

    # 3. Innings Data Helper
    def add_innings_section(team, opponent, innings_num):
        elements.append(Paragraph(f"INNINGS {innings_num}: {team.name.upper()}", section_header_style))
        elements.append(Paragraph(f"<b>Score: {team.runs}/{team.wickets}</b> in {team.overs_formatted} Overs (Extras: {team.total_extras})", styles['Normal']))
        elements.append(Spacer(1, 10))

        # Batting Table
        batting_data = [["BATSMAN", "STATUS", "R", "B", "4s", "6s", "SR"]]
        for name, p in team.players.items():
            if p.balls_faced > 0 or p.is_out:
                status = "OUT" if p.is_out else "NOT OUT"
                batting_data.append([name, status, p.runs, p.balls_faced, p.fours, p.sixes, f"{p.strike_rate:.1f}"])
        
        if len(batting_data) > 1:
            bat_table = Table(batting_data, colWidths=[150, 80, 40, 40, 40, 40, 60])
            bat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#475569")),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
            ]))
            elements.append(bat_table)
        
        elements.append(Spacer(1, 15))

        # Bowling Table
        bowling_data = [["BOWLER", "O", "R", "W", "ECON"]]
        for name, p in opponent.players.items():
            if p.balls_bowled > 0:
                bowling_data.append([name, p.overs_formatted, p.runs_conceded, p.wickets_taken, f"{p.economy:.1f}"])
        
        if len(bowling_data) > 1:
            elements.append(Paragraph("BOWLING", styles['Heading4']))
            bowl_table = Table(bowling_data, colWidths=[180, 60, 60, 60, 90])
            bowl_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#475569")),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
            ]))
            elements.append(bowl_table)
        
        elements.append(Spacer(1, 30))

    # 4. Add Both Innings
    # Determine who batted first
    # In our Match logic, team_a vs team_b. 
    # If match is finished, check current_innings.
    # For a simpler approach, we just output both if they have data.
    if match.current_innings >= 1:
        # Check who was the batting team in innings 1
        # If toss_winner exists and we have batting/bowling info, it helps.
        # For now, let's just show Team A then Team B or based on balls.
        add_innings_section(match.team_a, match.team_b, 1)
        if match.current_innings == 2 or match.is_finished:
            add_innings_section(match.team_b, match.team_a, 2)

    # Footer
    elements.append(Spacer(1, 40))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    footer_text = f"Generated by 🏏 TSE SmartCric Scorer on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.grey)))

    doc.build(elements)
    buffer.seek(0)
    return buffer
