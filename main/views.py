from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Notice


# ==========================================
# 0. 메인 홈
# ==========================================
def home(request):
    return render(request, 'home.html')


# ==========================================
# 1. 학원 소개 (Intro)
# ==========================================
def intro_greeting(request):
    return render(request, 'intro_greeting.html')

def intro_facility(request):
    return render(request, 'intro_facility.html')

def intro_meal(request):
    return render(request, 'intro_meal.html')       # ★ 신규: 급식 예고

def intro_location(request):
    return render(request, 'intro_location.html')

def intro_teachers(request):
    # 1. 전체 강사진 마스터 데이터 (모달 생성용 & 카드 참조용)
    teachers_dict = {
        "teacher1": {
            "modal_id": "teacher1",
            "name": "강태관",
            "card_img": "ko_kang.png",
            "slogan": "국어의 본질을 말하다<br>국어영역의 온전한 도움",
            "careers": [
                "한양대학교(국어국문학) 졸업",
                "대치 토나아카데미 고등부 강의",
                "대치 720학원 재학생 & 재수종합반",
                "압구정 선아학원 고등부 강의",
                "강북세일학원 고등부 강의",
                "천재교육 저자 및 검토위원",
                "목동 김현구 국어학원 고등부 강의",
                "대치 플투스학원 재수종합반 국어과 대표강사",
                "대치 플투스학원 원장",
            ],
        },
        "teacher2": {
            "modal_id": "teacher2",
            "name": "전호범",
            "card_img": "ko_jeon.png",
            "slogan": "극강의 시작으로<br>최상의 결과를 거둬보자",
            "careers": [
                "서강대학교 국어국문학과 졸업",
                "대치 나인플러스 재학생반 국어과",
                "홍대 아름다운학원 재수종합반 국어과",
                "분당 대성학원 재수종합반 국어과",
                "안성 비상에듀학원기숙학원 재수종합반 국어과",
                "대치 플투스학원 재수종합반 국어과 전임",
            ],
        },
        "teacher3": {
            "modal_id": "teacher3",
            "name": "노가영",
            "card_img": "ko_no.png",
            "slogan": "꼼꼼하게 확실하게!<br>1등급행 급행 열차",
            "careers": [
                "홍익대학교 국어교육과 졸업",
                "중계 언희당 국어학원 고등부 강의",
                "목동 김종길 국어학원 고등부 강의",
                "인천 수입시학원 국어영역",
                "부천 능력학원 국어영역",
                "여주 비상에듀 기숙학원 재수종합반 국어과",
                "대치 플투스학원 재수종합반 국어과 전임",
            ],
        },
        "teacher4": {
            "modal_id": "teacher4",
            "name": "임명훈",
            "card_img": "ko_im.png",
            "slogan": "국어,<br>더는 지지 말자!",
            "careers": [
                "동국대학교 국어교육과 졸업",
                "강동 메가스터디 국어과",
                "송파 메가스터디 국어과",
                "대치 강안교육 재수종합반 국어과",
                "대치 플투스학원 재수종합반 국어과 전임",
            ],
        },
        "teacher5": {
            "modal_id": "teacher5",
            "name": "이우준",
            "card_img": "ma_lee.png",
            "slogan": "현재의 위치보다<br>방향이 중요하다!",
            "careers": [
                "한양대학교 수학과 졸업",
                "강남가우스 수학학원 팀장",
                "프리미어 수학학원 강사",
                "대치 플투스학원 재수종합반 수학과 전임",
                "대치플투스학원 부원장",
                "ETOOS 어썸네오시리즈 공저",
                '그릿에듀출판사 "백미" 시리즈 공저',
            ],
        },
        "teacher6": {
            "modal_id": "teacher6",
            "name": "조문선",
            "card_img": "ma_jo.png",
            "slogan": "수학의 두려움과 거부감을<br>자신감과 친근감으로!",
            "careers": [
                "중앙대학교 수학교육 석사 졸업",
                "노량진 코리아에듀학원 재수종합반",
                "노량진 정진학원 재수종합반",
                "상생학원(노량진,서대문) 재수종합반",
                "평촌 필탑학원 재수종합반",
                "목동 대성학원 재수종합반",
                "대치멘토스학원 재수종합반",
                "대치720학원 재수종합반",
                "대치 플투스학원 재수종합반 수학과 전임",
            ],
        },
        "teacher7": {
            "modal_id": "teacher7",
            "name": "김희수",
            "card_img": "ma_kim.png",
            "slogan": "실전에 강하게,<br>수학의 뼈대를 세우는 첫걸음",
            "careers": [
                "건국대학교 졸업",
                "성동구 입시학원 수학과 전임",
                "대치, 강남 수학 개인교습",
                "대치 플투스학원 재수종합반 수학과 전임",
            ],
        },
        "teacher8": {
            "modal_id": "teacher8",
            "name": "김종군",
            "card_img": "ma_jong.png",
            "slogan": "킬러와 변형에 강한 수학!!<br>인피니트!!",
            "careers": [
                "강동청솔학원 재수종합반",
                "진성진덕기숙학원 재수종합반",
                "ETOOS 온라인강사",
                "생각의지표학원 원장",
                "인피니트수학연구소 대표",
                "대치 플투스학원 재수종합반 수학과 전임",
                "최상위수학 공저",
                "최상위수학 라이트 공저",
                "ETOOS 더올림고등수학 공저",
                "GRIT 고등교재 시리즈 공저",
                "어썸&인피니트 스피드 모의고사 공저",
            ],
        },
        "teacher9": {
            "modal_id": "teacher9",
            "name": "남재언",
            "card_img": "ma_nam.png",
            "slogan": "어려운 수학에서<br>재미를 찾는다",
            "careers": [
                "대일 외고 / 고려대학교",
                "중계 청림학원",
                "대치 최고 수준의 사람들",
                "대치 나인에듀 재수종합반",
                "대치 원투원 플러스 재수종합반",
                "대치 수력학원",
                "72시간 재수학원",
                "대치 디딤학원",
                "대치 플투스학원 재수종합반 수학과 전임",
            ],
        },
        "teacher10": {
            "modal_id": "teacher10",
            "name": "장민호",
            "card_img": "ma_jang.png",
            "slogan": "수학은<br>곰(God_Of_Math)과 함께!",
            "careers": [
                "서울대학교 컴퓨터 공학부 졸업",
                "진성진덕기숙학원 재수종합반",
                "대치스카이논술n수능학원 자연계 논술",
                "과천고 ,병점고, 과천외고 수학 & 수리논술",
                "종로학원 온라인 e-class 수학과",
                "종로학원 본원 수학과 단과",
                "곰수학 원장",
                "대치 플투스학원 재수종합반 수학과 전임",
            ],
        },
        "teacher11": {
            "modal_id": "teacher11",
            "name": "장대영",
            "card_img": "eng_jang.png",
            "slogan": "괜찮아 잘될거야<br>샘이 있잖아!!",
            "careers": [
                "메가 스터디 러셀 [고3 / N수]",
                "노량진 메가스터디 단과 [고3 / N수]",
                "명인학원",
                "코드 ⓔ 수능연구소 대표",
                "메가 공무원 온라인 / 오프라인 대표강사",
                "대치 플투스학원 재수종합반 영어과 전임",
            ],
        },
        "teacher12": {
            "modal_id": "teacher12",
            "name": "박윤철",
            "card_img": "eng_park.png",
            "slogan": "직관적<br>영어 1등급!",
            "careers": [
                "강북대성학원 재수종합반 영어과 대표강사",
                "대치동 강남비타에듀학원 재수종합반 대표강사",
                "광주청솔기숙학원 재수종합반 영어과 대표강사",
                "광주비상에듀기숙학원 재수종합반 대표강사",
                "대치 플투스학원 재수종합반 영어과 전임",
            ],
        },
        "teacher13": {
            "modal_id": "teacher13",
            "name": "한고호",
            "card_img": "eng_han.png",
            "slogan": "밀착코칭으로 흡수, 반복훈련으로 체화,<br>성적상승으로 증명하는 (高)흡수영어",
            "careers": [
                "한국외국어대학교 영어통번역학, 경영학 졸업",
                "김영편입 영어 독해·문법",
                "한양학원 고3·N수 영어과 대표강사",
                "대치 플투스학원 재수종합반 영어과 전임",
            ],
        },
        "teacher14": {
            "modal_id": "teacher14",
            "name": "고광윤",
            "card_img": "sci_go.png",
            "slogan": "화학으로<br>대학 가자!",
            "careers": [
                "연세대 과학 교육 석사",
                "메가 PEET 일반화학 강사",
                "청심 고등학교 화학 초빙강사",
                "목동, 송파 종로 학원 화학, 논술 강의",
                "진명, JEET 화학 단과",
                "종로 학원 모의고사 출제 및 검토 위원",
                "대치 플투스학원 재수종합반 전임 대표강사",
            ],
        },
        "teacher15": {
            "modal_id": "teacher15",
            "name": "유선호",
            "card_img": "sci_you.png",
            "slogan": "언제나<br>1등급을 책임집니다!",
            "careers": [
                "연세대학교 석사 졸업",
                "양서고등학교 출강",
                "대치동 명인학원",
                "대치동 올림피아드학원",
                "이천탑텐스터디기숙학원",
                "노원세일학원 재수부",
                "대치동 지틀에듀학원",
                "강북세일학원 고등부",
                "이천청솔기숙학원",
                "대치 플투스학원 재수종합반 전임 대표강사",
                "하이패스 과학(디딤돌)",
            ],
        },
        "teacher16": {
            "modal_id": "teacher16",
            "name": "김동주",
            "card_img": "sci_kim.png",
            "modal_img": "sci_kim2.png",
            "slogan": "마술 같은 1등급<br>기적의 신화!!",
            "careers": [
                "서울아카데미(강동)",
                "수연당학원(용인)",
                "탑텐학원(이천)",
                "종로학원, 숨마투스 의치대반",
                "스카이에듀 재종반(수원, 강동)",
                "이강학원(영통, 수지, 화정)",
                "대치 플투스학원 재수종합반 전임 대표강사",
            ],
        },
        "teacher17": {
            "modal_id": "teacher17",
            "name": "김명우",
            "card_img": "sci_kimm.png",
            "slogan": "과학탐구<br>통합과학이 필수입니다.",
            "careers": [
                "서초 메가스터디 기숙학원 의대관 강사",
                "수만휘기숙학원 과탐강사",
                "DS 교육 과탐강사",
                "대치 플투스학원 재수종합반 전임 대표강사",
            ],
        },
        "teacher18": {
            "modal_id": "teacher18",
            "name": "김지용",
            "card_img": "so_kim.png",
            "slogan": "사회 탐구의 황제!<br>경험하고 느껴보라!",
            "careers": [
                "연세대 대학원",
                "세진사탐 (대치) 대표 강사",
                "글로벌1st (대치) 대표 강사",
                "대치우리 (대치) 대표 강사",
                "우림 (대치) 대표 강사",
                "대치동(멘토스, ST예인)",
                "이천 탑텐스터디, 비상탑클래스",
                "대치 플투스학원 재수종합반 전임 대표강사",
                "이지수능 파이널 한국(세계)지리 봉투모의고사",
            ],
        },
        "teacher19": {
            "modal_id": "teacher19",
            "name": "장진민",
            "card_img": "so_jang.png",
            "slogan": "언제나 1등급!<br>변함없는 최고를 만나다!",
            "careers": [
                "비상에듀, 마이맥 온라인",
                "KT 온라인, 천재교육 온라인",
                "EBS 3분 사회탐구 온라인 외 다수",
                "시대인재학원, 종로학원, 대성학원 출강",
                "메가스터디 러셀학원 등 출강",
                "이투스 온라인",
                "강남구청 인터넷 수능방송",
                "이강학원, 명인학원, 비상에듀학원",
                "ST예인학원, 서정학원 외 다수 출강",
                "대치 플투스학원 재수종합반 전임 대표강사",
            ],
        },
        "teacher20": {
            "modal_id": "teacher20",
            "name": "정 정",
            "card_img": "so_jeong.png",
            "slogan": "전공자의 눈!<br>쉽고 빠른 사회문화!",
            "careers": [
                "연세대학교 사회교육 석사",
                "러셀 목동, 영통 출강",
                "메가스터디 재수정규반 강남, 노량진, 분당 출강",
                "연세대학교 교육대학원 특강 강사",
                "대성학원, 대치명인학원, 세정학원",
                "강남하이퍼기숙학원, 청솔학원 출강",
                "대치 플투스학원 재수종합반 전임 대표강사",
                "㈜단단북스 일등급 사탐, 고품격 사탐",
                "㈜박문각 ebs 정정 사회 실전400제 등 다수",
            ],
        },
        "teacher21": {
            "modal_id": "teacher21",
            "name": "문성욱",
            "card_img": "so_moon.png",
            "slogan": "학생이 중심이 되어<br>움직이는 수업",
            "careers": [
                "고려대학교 대학원 일반사회교육 석사",
                "메가스터디",
                "SKYEDU 온라인 수능 사회탐구",
                "대치 이강학원",
                "대치 중심학원-대원외고",
                "스카이에듀 오프라인 선릉 예체능/남양주/수원",
                "용인 이강 기숙학원",
                "대치 플투스학원 재수종합반 전임 대표강사",
                "tvN 어쩌다 어른",
                "redpig academy 문성욱의 골목책방 (youtube)",
                "삼성전자/나/BMW/건설협회 철학 강좌 진행",
            ],
        },
        "teacher22": {
            "modal_id": "teacher22",
            "name": "김경민",
            "card_img": "ess_kim.png",
            "slogan": "대치동 빅3!!!<br>인문논술의 마술사",
            "careers": [
                "고려대학교 법학과 졸업",
                "노원 세일학원 논술 전문강사",
                "양서고, 염광고, 명일외고 등 논술특강 강사",
                "대치 거인의 어깨 논술 전문 강사",
                "중계동 유인학원 원장 및 논술담당",
                "강남 우리학원 원장 및 논술담당",
                "대치 플투스학원 인문논술 전임",
            ],
        },
    }

    def make_card(modal_id, subject):
        t = teachers_dict[modal_id]
        return {
            "modal_id": modal_id,
            "subject": subject,
            "name": t["name"],
            "card_img": t["card_img"],
        }

    teacher_groups = [
        {
            "id": "KoreanTeacher",
            "title": "국어 선생님",
            "desc": "수능의 본질을 꿰뚫는 압도적인 강의력을 보여줍니다.<br>결과로 증명하는 검증된 베테랑 강사진이 아이들의 성적 향상을 책임집니다.",
            "teachers": [
                make_card("teacher1", "국어영역"),
                make_card("teacher2", "국어영역"),
                make_card("teacher3", "국어영역"),
                make_card("teacher4", "국어영역"),
            ],
        },
        {
            "id": "MathTeacher",
            "title": "수학 선생님",
            "desc": "학생 한 명 한 명의 눈높이에서 진심으로 소통하며 잠재력을 깨웁니다.<br>가르침에 대한 뜨거운 열정과 따뜻한 관심으로 끝까지 함께하는 든든한 멘토가 되어드립니다.",
            "teachers": [
                make_card("teacher5", "수학영역"),
                make_card("teacher6", "수학영역"),
                make_card("teacher7", "수학영역"),
                make_card("teacher8", "수학영역"),
                make_card("teacher9", "수학영역"),
                make_card("teacher10", "수학영역"),
            ],
        },
        {
            "id": "EnglishTeacher",
            "title": "영어 선생님",
            "desc": "막막했던 공부가 즐거워지고 불가능해 보였던 목표가 현실이 되는 순간을 만듭니다.<br>최고의 선생님들과 함께라면 우리 아이의 성적 그래프는 반드시 우상향합니다.",
            "teachers": [
                make_card("teacher11", "영어영역"),
                make_card("teacher12", "영어영역"),
                make_card("teacher13", "영어영역"),
            ],
        },
        {
            "id": "InquiryTeacher",
            "title": "탐구 선생님",
            "desc": "대형 학원에서는 경험할 수 없는 세심하고 체계적인 1대1 밀착 코칭을 제공합니다.<br>아이의 취약점을 정확히 진단하고 완벽하게 보완하는 최정예 강사진이 함께합니다.",
            "teachers": [
                make_card("teacher14", "통합과학"),
                make_card("teacher15", "통합과학"),
                make_card("teacher16", "통합과학"),
                make_card("teacher17", "통합과학"),
                make_card("teacher18", "통합사회"),
                make_card("teacher19", "통합사회"),
                make_card("teacher20", "통합사회"),
                make_card("teacher21", "통합사회"),
            ],
        },
        {
            "id": "EssayTeacher",
            "title": "논술 선생님",
            "desc": "좋은 선생님을 만나는 것은 아이의 인생을 바꾸는 가장 큰 행운입니다.<br>대한민국 교육의 기준을 높이는 최고의 선생님들이 이곳에 모여 있습니다.",
            "teachers": [
                make_card("teacher10", "수리논술"),
                make_card("teacher22", "인문논술"),
            ],
        },
    ]

    context = {
        "teacher_groups": teacher_groups,
        "all_teachers": teachers_dict.values(),
    }
    return render(request, "intro_teachers.html", context)


# ==========================================
# 2. 학습 안내 (System)
# ==========================================
def system_x10(request):
    return render(request, 'system_x10.html')

def system_life(request):
    return render(request, 'system_life.html')

def system_voca(request):
    return render(request, 'system_voca.html')      # ★ 신규: 단어 시험

def system_mock(request):
    return render(request, 'system_mock.html')      # ★ 신규: 주간 모고


# ==========================================
# 3. 모집 요강 (Class)
# ==========================================
def class_retake(request):
    return render(request, 'class_retake.html')

def class_ged(request):
    return render(request, 'class_ged.html')        # ★ 신규: 검시대입

def class_camp(request):
    return render(request, 'class_camp.html')       # ★ 신규: 방학캠프

def class_english(request):
    return render(request, 'class_english.html')    # ★ 신규: 영어단과

def class_inquiry(request):
    return render(request, 'class_inquiry.html')    # ★ 신규: 탐구단과

def class_essay(request):
    return render(request, 'class_essay.html')      # ★ 신규: 대입논술


# ==========================================
# 4. 상담실 (Consult & Notice & Guide)
# ==========================================
@never_cache
def consult_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        student_name = request.POST.get('student_name', '').strip()
        age = request.POST.get('age', '').strip()
        high_school = request.POST.get('high_school', '').strip()
        phone_owner = request.POST.get('phone_owner', '').strip()
        phone = request.POST.get('phone', '').strip()
        region = request.POST.get('region', '').strip()
        csat_grade = request.POST.get('csat_grade', '').strip()
        consult_date = request.POST.get('consult_date', '').strip()
        consult_time = request.POST.get('consult_time', '').strip()

        subject = f"[대치플투스 상담예약] {student_name} ({age}) - {consult_date} {consult_time}"
        message = (
            f"새로운 방문/입시 상담 예약이 접수되었습니다.\n\n"
            f"■ 학생 이름: {student_name}\n"
            f"■ 나이: {age}\n"
            f"■ 이메일 주소: {email}\n"
            f"■ 출신 고등학교: {high_school}\n"
            f"■ 전화번호: [{phone_owner}] {phone}\n"
            f"■ 사는 지역: {region}\n"
            f"■ 올해 수능 등급: {csat_grade}\n"
            f"■ 희망 상담 일시: {consult_date} / {consult_time}\n"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_CONSULT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "상담 예약이 정상적으로 접수되었습니다. 담당자가 확인 후 연락드리겠습니다.")
            return redirect('booking')
        except Exception as e:
            messages.error(request, "메일 발송 중 오류가 발생했습니다. 학원으로 직접 문의해 주세요.")

    return render(request, 'booking.html')

def notice_list(request):
    query = request.GET.get("q", "").strip()
    notices = Notice.objects.all()

    if query:
        notices = notices.filter(Q(title__icontains=query) | Q(content__icontains=query))

    paginator = Paginator(notices, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "notice_list.html", {
        "page_obj": page_obj,
        "query": query,
    })

def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.views += 1
    notice.save(update_fields=["views"])

    prev_notice = Notice.objects.filter(id__lt=notice.id).order_by("-id").first()
    next_notice = Notice.objects.filter(id__gt=notice.id).order_by("id").first()

    return render(request, "notice_detail.html", {
        "notice": notice,
        "prev_notice": prev_notice,
        "next_notice": next_notice,
    })

def guide_info(request):
    return render(request, 'guide_info.html')       # ★ 신규: 안내 사항


# ==========================================
# 5. 입시 실적 (Results)
# ==========================================
def intro_results(request):
    return render(request, 'intro_results.html')    # 명예의 전당