#!/usr/bin/env python3
"""Build a Korean-language Shanghai trip PDF from trip.json."""
import json
import os
import re
import urllib.request
from html import escape
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "trip.json").read_text("utf-8"))
OUTPUT = ROOT / "shanghai-itinerary-2026.pdf"
FONT = ROOT / "nanum.ttf"
if not FONT.exists():
    url = "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    try:
        urllib.request.urlretrieve(url, FONT)
    except Exception as exc:
        print("Font download failure; will try Korean CID font:", exc)

if FONT.exists():
    pdfmetrics.registerFont(TTFont("Hangul", str(FONT)))
    font = "Hangul"
else:
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    pdfmetrics.registerFont(UnicodeCIDFont("HYGothic-Medium"))
    font = "HYGothic-Medium"

navy = colors.HexColor("#17384E")
teal = colors.HexColor("#297F8C")
sky = colors.HexColor("#EAF3F5")
line = colors.HexColor("#DCE6EA")
grey = colors.HexColor("#667A87")
warm = colors.HexColor("#C77756")

styles = {}
def make(name,size=9.2,leading=None,color=navy,bold=False,align=TA_LEFT,spaceAfter=0):
    styles[name]=ParagraphStyle(name,fontName=font,fontSize=size,leading=leading or size*1.55,
        textColor=color,alignment=align,spaceAfter=spaceAfter,allowWidows=0,allowOrphans=0)
make("title",24,34)
make("h1",18,26)
make("h2",12,19)
make("body",9.1,15)
make("tiny",8.05,12.4)
make("small",7.7,11.6)
make("time",9.0,13,warm)
make("note",8.25,13,grey)
make("white",8,13,colors.white)
make("sub",11,18,teal)
make("center",9,15,navy,align=TA_CENTER)

def para(t,style="body"):
    return Paragraph(escape(str(t)).replace("\n","<br/>"),styles[style])

def rich(t,style="body"):
    return Paragraph(t,styles[style])

def table_style(header=False):
    rules=[
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),8),
        ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LINEBELOW",(0,0),(-1,-2),0.45,line),
    ]
    if header:
        rules += [("BACKGROUND",(0,0),(-1,0),navy),
                  ("TOPPADDING",(0,0),(-1,0),9),
                  ("BOTTOMPADDING",(0,0),(-1,0),9)]
    return TableStyle(rules)

def add_footer(canvas,doc):
    canvas.saveState()
    w,h=A4
    canvas.setStrokeColor(line)
    canvas.line(18*mm,16.5*mm,w-18*mm,16.5*mm)
    canvas.setFont(font,8)
    canvas.setFillColor(grey)
    canvas.drawString(18*mm,12*mm,"SHANGHAI 2026  |  DAD & SON")
    canvas.drawRightString(w-18*mm,12*mm,str(doc.page))
    canvas.restoreState()

doc=SimpleDocTemplate(str(OUTPUT),pagesize=A4,
    leftMargin=18*mm,rightMargin=18*mm,topMargin=18*mm,bottomMargin=21*mm,
    title="상하이 부자 여행 일정표 2026.11.05–11.08",
    author="Travel itinerary")
usable=A4[0]-36*mm
story=[]
story += [Spacer(1,10*mm),para("SHANGHAI · DAD & SON","sub"),
          Spacer(1,5*mm),para("상하이, 우리 둘의 여행","title"),
          para("2026년 11월 5일(목) — 11월 8일(일) · 3박 4일","sub"),
          Spacer(1,11*mm)]
flight=[
    [para("출국 · 11/5 목","white"),para("귀국 · 11/8 일","white")],
    [para("10:50 인천 ICN → 11:55 푸동 PVG","body"),
     para("13:10 푸동 PVG → 16:00 인천 ICN","body")],
    [para("아시아나 비즈니스 · 인천 T2","tiny"),
     para("아시아나 비즈니스 · 푸동 T1","tiny")]]
ft=Table(flight,colWidths=[usable/2]*2)
ft.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),navy),
                       ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,sky]),
                       ("BOX",(0,0),(-1,-1),.65,line),
                       ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                       ("LEFTPADDING",(0,0),(-1,-1),12),
                       ("TOPPADDING",(0,0),(-1,-1),9),
                       ("BOTTOMPADDING",(0,0),(-1,-1),9)]))
story += [ft,Spacer(1,9*mm),
          para("호텔 · 3박 예약 완료","h2"),
          para("Shanghai Marriott Marquis City Centre (上海雅居乐万豪侯爵酒店)","body"),
          para("주소: 上海市黄浦区西藏中路555号 · 인민광장 / 난징동루 인근","note"),
          Spacer(1,12*mm),para("4일 여행 한눈에 보기","h1")]
summ=[
    ("DAY 1 · 11/5 목","난징동루 쇼핑 · 양꼬치 · 와이탄 야경"),
    ("DAY 2 · 11/6 금","예원 · 난샹 간식 · 점도덕 딤섬 · IFC몰 · 상하이 타워"),
    ("DAY 3 · 11/7 토","우캉루 · HARMAY · 대한민국 임시정부 · 로스터리 · ERA2 서커스"),
    ("DAY 4 · 11/8 일","호텔 체크아웃 · 푸동 T1 · 라운지 · 귀국")
]
summary=[[para(x,"h2"),para(y,"body")] for x,y in summ]
t=Table(summary,colWidths=[120,usable-120])
t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),sky),
                       ("BOX",(0,0),(-1,-1),0.65,line),
                       ("LINEBELOW",(0,0),(-1,-2),.45,line),
                       ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                       ("LEFTPADDING",(0,0),(-1,-1),11),
                       ("TOPPADDING",(0,0),(-1,-1),11),
                       ("BOTTOMPADDING",(0,0),(-1,-1),11)]))
story += [t,Spacer(1,13*mm),
          para("여행의 핵심","h2"),
          para("① 음식과 쇼핑 중심의 자유여행  ② 아버지·아들의 도시 탐방  ③ 대한민국 임시정부 방문을 통한 역사 체험","body"),
          Spacer(1,7*mm),
          para("※ 모든 시각은 현지시간 기준(상하이는 한국보다 1시간 느림). 식당·공연·전망대 영업 및 예약 여부는 방문 전 확인하세요.","note")]

for di,day in enumerate(DATA["days"]):
    story.append(PageBreak())
    story.append(para("DAY %d   |   %s"%(di+1,day["label"]),"sub"))
    story.append(para(day["title"],"h1"))
    story.append(para(day["sub"],"note"))
    story.append(Spacer(1,3*mm))
    cols=[50,157,usable-207]
    rows=[[para("시간","white"),para("방문·활동","white"),para("주요 내용 및 이동","white")]]
    for s in day["stops"]:
        detail=s[4]+"  /  "+s[5]
        rows.append([para(s[0],"time"),para(s[1],"body"),para(detail,"tiny")])
    t=Table(rows,colWidths=cols,repeatRows=1,hAlign="LEFT")
    t.setStyle(table_style(header=True))
    story.append(t)
    story.append(Spacer(1,6*mm))
    story.append(para("당일 참고  |  "+day["tip"],"note"))

story.append(PageBreak())
story.append(para("실전 이동·예약 체크","h1"))
story.append(Spacer(1,4*mm))
ess=[
    ("교통·지도","공항↔호텔은 공식 택시 또는 DiDi 이용. 시내는 DiDi와 고덕지도(Amap)를 함께 사용하고 중국어 목적지를 제시합니다."),
    ("11/6 점도덕","점도덕·덕소관 정대광장점(点都德·德小馆 正大店), 陆家嘴西路168号 正大广场 西区6楼614室. 13:15 딤섬 점심 예정."),
    ("11/7 역사 탐방","대한민국 임시정부 청사: 马当路306弄4号. 14:00 방문을 핵심 일정으로 유지합니다."),
    ("11/7 공연","상하이 서커스 월드 ERA2: 19:30~20:30(계획). 티켓·공연일정 최종 확인이 필요합니다."),
    ("상하이 타워","11/6 16:00 전망대 예정. 가시거리·날씨와 사전 예매 여부를 확인합니다."),
    ("라운지","인천공항 T2는 탑승권 안내 라운지 확인. 푸동공항은 T1 체크인 시 당일 지정 제휴 라운지 확인(과거 T2 라운지 정보 사용 금지).")
]
r=[[para(name,"h2"),para(detail,"tiny")] for name,detail in ess]
t=Table(r,colWidths=[108,usable-108])
t.setStyle(TableStyle([("BOX",(0,0),(-1,-1),.5,line),
                       ("LINEBELOW",(0,0),(-1,-2),.5,line),
                       ("BACKGROUND",(0,0),(0,-1),sky),
                       ("VALIGN",(0,0),(-1,-1),"TOP"),
                       ("LEFTPADDING",(0,0),(-1,-1),10),
                       ("TOPPADDING",(0,0),(-1,-1),9),
                       ("BOTTOMPADDING",(0,0),(-1,-1),9)]))
story.append(t)
story.append(Spacer(1,8*mm))
story.append(para("출발 전 체크리스트","h2"))
items=["여권 2개 · 항공권 · 호텔 바우처 · 보험",
       "ERA2 / 전망대 입장권 · 영업시간 확인",
       "Alipay 등록 · DiDi · 고덕지도 · 번역 앱",
       "중국용 eSIM 또는 로밍 · 충전기 · 보조배터리 규정 확인",
       "비상용 현금 ¥200~400 · 예비 해외결제 카드"]
story.extend([para("□ "+x,"body") for x in items])
story.append(Spacer(1,8*mm))
story.append(para("공식 여행 웹사이트: https://jaykim-ai.github.io/shanghai-dad-son-2026/","note"))
doc.build(story,onFirstPage=add_footer,onLaterPages=add_footer)
print(f"Created {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
