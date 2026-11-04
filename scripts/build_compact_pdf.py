#!/usr/bin/env python3
"""Four A4 pages, one day per page, synced with embedded index.html data."""
from pathlib import Path
from html import escape
import json, re, urllib.request
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle, PageBreak, Spacer, KeepTogether
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent.parent
html=(ROOT/"index.html").read_text(encoding="utf-8")
match=re.search(r'<script type="application/json" id="tripdata">([\s\S]*?)</script><script>',html)
if not match: raise SystemExit("Cannot find authoritative tripdata in index.html")
DATA=json.loads(match.group(1))
OUTPUT=ROOT/"Shanghai_Dad_Son_Compact_4pages_2026.pdf"
FONT=ROOT/"nanum.ttf"
if not FONT.exists():
    try: urllib.request.urlretrieve("https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Regular.ttf",FONT)
    except Exception as e: print("Font fetch error:",e)
if FONT.exists():
    pdfmetrics.registerFont(TTFont("Korean",str(FONT)))
    fname="Korean"
else:
    pdfmetrics.registerFont(UnicodeCIDFont("HYGothic-Medium"))
    fname="HYGothic-Medium"

NAVY=colors.HexColor("#17384e"); BLUE=colors.HexColor("#226d85")
TEAL=colors.HexColor("#217768"); LIGHT=colors.HexColor("#edf5f6")
RULE=colors.HexColor("#d6e1e5"); GREY=colors.HexColor("#536b77")
W,H=A4
def style(key,size,leading=None,color=NAVY,align=TA_LEFT):
    return ParagraphStyle(key,fontName=fname,fontSize=size,leading=leading or size*1.38,
                          textColor=color,alignment=align,wordWrap="CJK")
sty={
 "eyebrow":style("eyebrow",10,13,TEAL),
 "title":style("title",19.5,27),
 "sub":style("sub",9.4,14,GREY),
 "main":style("main",9.2,13),
 "small":style("small",8.1,11.5,GREY),
 "tiny":style("tiny",7.7,10.8,GREY),
 "clock":style("clock",9.7,13,TEAL),
 "white":style("white",8.7,11,colors.white),
 "boxhead":style("boxhead",9.2,13,BLUE),
}
def p(x,k="main"):
    return Paragraph(escape(str(x)).replace("\n","<br/>"),sty[k])
def raw(x,k="main"):return Paragraph(x,sty[k])
def short(s,maxlen=62):
    s=re.sub(r"\s+"," ",str(s or "")).strip()
    return s if len(s)<=maxlen else s[:maxlen-1].rstrip()+"…"

class Doc(BaseDocTemplate):
    pass
doc=Doc(str(OUTPUT),pagesize=A4,
    leftMargin=14*mm,rightMargin=14*mm,topMargin=13*mm,bottomMargin=16*mm,
    title="상하이 부자 여행 | 날짜별 한 장 일정표 | 2026.11.05–11.08",
    author="Shanghai Dad & Son Travel Guide")
frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
def foot(canvas,document):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.line(14*mm,12*mm,W-14*mm,12*mm)
    canvas.setFont(fname,8.3)
    canvas.setFillColor(GREY)
    canvas.drawString(14*mm,8.2*mm,"SHANGHAI 2026  |  DAD & SON")
    canvas.drawRightString(W-14*mm,8.2*mm,f"{document.page} / 4")
    canvas.restoreState()
doc.addPageTemplates([PageTemplate(id="Compact",frames=[frame],onPage=foot)])
width=doc.width
story=[]
summary=[
 ["11/5 목","도착·쇼핑·ERA2","14:10 그랜드마더","17:00 양꼬치"],
 ["11/6 금","예원·타워·와이탄","13:15 점도덕","18:00 주광옥 훠궈"],
 ["11/7 토","우캉루·임시정부","12:00 RAC","17:05 위싱지"],
 ["11/8 일","공항·귀국","기내식(예정)","귀국 후"],
]
notes=[
 ("오늘의 핵심","입국·호텔 이동이 늦어지면 쇼핑을 줄이고 19:30 ERA2 공연을 우선합니다."),
 ("식사 메모","14:10 그랜드마더는 도착 상황에 따라 지연 가능. 17:00 양꼬치 저녁은 빠르게 주문하세요."),
 ("공연 준비","ERA2 11/5(목) 19:30 · 上海马戏城(共和新路2266号). 실제 예약·입장 조건을 확인하세요."),
 ("오늘의 핵심","전통 정원과 초고층 전망대를 보고 저녁에 와이탄 야경으로 마무리합니다."),
 ("식사 메모","13:15 점도덕 딤섬 · 18:00 주광옥 훠궈. 훠궈 대기 시 와이탄 산책 시간 단축."),
 ("예약 준비","상하이 타워 16:00 입장권, 점도덕·주광옥 영업 및 대기 상태를 확인하세요."),
 ("오늘의 핵심","오후 14:00 대한민국 임시정부 청사 방문을 가장 중요하게 유지합니다."),
 ("식사 메모","12:00 RAC 브런치 · 17:05 위싱지 게살국수. 저녁 후 자유 산책 또는 휴식."),
 ("이동 준비","쇼핑은 유동적으로 조정하고 임시정부 방문 시간은 놓치지 않도록 합니다."),
 ("오늘의 핵심","08:35 전후 호텔 출발 후 푸동공항 T1으로 이동, 출국 수속과 라운지 이용."),
 ("기내 점심","13:10 출발 항공편에서 기내식을 예상하지만 실제 제공 시간은 항공사 안내를 확인하세요."),
 ("필수 체크","여권 2개·탑승권·보조배터리·구매품·체크아웃·T1 카운터·당일 라운지 확인."),
]
def draw_meal_strip(day_index):
    row=summary[day_index]
    text=f"점심  {row[2]}     |     저녁  {row[3]}"
    tab=Table([[p(text,"boxhead")]],colWidths=[width])
    tab.setStyle(TableStyle([
       ("BACKGROUND",(0,0),(-1,-1),LIGHT),
       ("BOX",(0,0),(-1,-1),0.5,RULE),
       ("LEFTPADDING",(0,0),(-1,-1),11),
       ("RIGHTPADDING",(0,0),(-1,-1),9),
       ("TOPPADDING",(0,0),(-1,-1),8),
       ("BOTTOMPADDING",(0,0),(-1,-1),8),
    ]))
    return tab

for di,day in enumerate(DATA["days"]):
    if di: story.append(PageBreak())
    story += [
        p("SHANGHAI · DAD & SON   |   DAY "+str(di+1),"eyebrow"),
        Spacer(1,2*mm),
        p(f"{day['label']}  ·  {day['title']}","title"),
        Spacer(1,2*mm),
        p(short(day["sub"],96),"sub"),
        Spacer(1,4*mm),
        draw_meal_strip(di),
        Spacer(1,3*mm),
    ]
    cells=[[p("시각","white"),p("활동 / 장소","white"),p("핵심 메모 · 이동","white")]]
    # Distinctly concise details for a practical single-page printout.
    for s in day["stops"]:
        name=short(s[1],31)
        detail=short(s[4],49)
        move=short(s[5],31)
        if "라운지" in name: detail="출국 수속 후 휴식 · 실제 라운지 안내 확인"
        if "그랜드마더" in name: detail="홍소육·마파두부·채소·볶음밥"
        if "양꼬치" in name: detail="양꼬치·닭날개·버섯·옥수수"
        if "점도덕" in name: detail="하가우·슈마이·홍미창·채소"
        if "주광옥" in name: detail="소고기·새우완자·버섯·청경채"
        if "RAC" in name: detail="갈레트·달걀·치즈·샐러드"
        if "위싱지" in name: detail="게살국수·채소 반찬"
        if "ERA2 서커스" in name: detail="19:30~20:30 · 공연 티켓 별도 확인"
        if "대한민국 임시정부" in name: detail="대한민국 독립운동 역사 탐방"
        if "와이탄 야경 산책" in name: detail="동방명주·황푸강 야경 감상"
        # Two short lines max where possible.
        cells.append([p(s[0],"clock"),p(name,"main"),p(detail+" · "+move,"tiny")])
    tab=Table(cells,colWidths=[54,162,width-216],repeatRows=1,hAlign="LEFT")
    rules=[
        ("BACKGROUND",(0,0),(-1,0),NAVY),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LINEBELOW",(0,0),(-1,-2),.4,RULE),
        ("LEFTPADDING",(0,0),(-1,-1),7),
        ("RIGHTPADDING",(0,0),(-1,-1),7),
        ("TOPPADDING",(0,0),(-1,-1),4.3),
        ("BOTTOMPADDING",(0,0),(-1,-1),4.3),
        ("TOPPADDING",(0,0),(-1,0),7),
        ("BOTTOMPADDING",(0,0),(-1,0),7),
    ]
    for j,s in enumerate(day["stops"],1):
        if s[2]=="food" and ("점심" in s[1] or "저녁" in s[1] or "조식" in s[1]):
            rules.append(("BACKGROUND",(0,j),(-1,j),colors.HexColor("#eef7f1")))
        if "ERA2 서커스" in s[1] or "임시정부" in s[1] or "와이탄 야경 산책" in s[1]:
            rules.append(("BACKGROUND",(0,j),(-1,j),colors.HexColor("#fff5e9")))
    tab.setStyle(TableStyle(rules))
    story.append(tab)
    story.append(Spacer(1,4.2*mm))
    for key,val in notes[di*3:di*3+3]:
        story.append(raw(f'<font color="#226d85">{escape(key)}</font>  |  {escape(val)}',"small"))
        story.append(Spacer(1,1.25*mm))
    if di==0:
        story.append(Spacer(1,2*mm))
        story.append(p("호텔  Shanghai Marriott Marquis City Centre  |  西藏中路555号","tiny"))
    if di==3:
        story.append(Spacer(1,2*mm))
        story.append(p("항공  11/5 ICN 10:50 → PVG 11:55  |  11/8 PVG 13:10 → ICN 16:00","tiny"))
# Each day forced to a new page. Validate exact 4-page output.
doc.build(story)
reader=PdfReader(str(OUTPUT))
assert len(reader.pages)==4, f"Expected 4 pages but generated {len(reader.pages)}"
for n,page in enumerate(reader.pages,1):
    extracted=page.extract_text() or ""
    assert "DAY "+str(n) in extracted, f"Day {n} title missing on page {n}"
print("SUCCESS",str(OUTPUT),OUTPUT.stat().st_size,"bytes",len(reader.pages),"A4 pages")
