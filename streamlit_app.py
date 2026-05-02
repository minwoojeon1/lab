import streamlit as st
from streamlit_calendar import calendar
import json
import os
import pandas as pd
from datetime import date, datetime
from uuid import uuid4
from io import BytesIO

# -------------------------------------------------
# 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="반도체 소자 연구실 시스템",
    layout="wide"
)

# -------------------------------------------------
# 폴더/파일 경로
# -------------------------------------------------
DATA_DIR = "."
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
MANUAL_UPLOAD_DIR = os.path.join(DATA_DIR, "manual_uploads")

EVENT_FILE = os.path.join(DATA_DIR, "events.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
PAPER_FILE = os.path.join(DATA_DIR, "papers.json")
EXPERIMENT_FILE = os.path.join(DATA_DIR, "experiment_data.json")
MANUAL_FILE = os.path.join(DATA_DIR, "manuals.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MANUAL_UPLOAD_DIR, exist_ok=True)

# -------------------------------------------------
# 공통 파일 초기화
# -------------------------------------------------
def ensure_json_file(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

ensure_json_file(EVENT_FILE)
ensure_json_file(INVENTORY_FILE)
ensure_json_file(PAPER_FILE)
ensure_json_file(EXPERIMENT_FILE)
ensure_json_file(MANUAL_FILE)

# -------------------------------------------------
# 공통 load/save
# -------------------------------------------------
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_events():
    return load_json(EVENT_FILE)

def save_events(data):
    save_json(EVENT_FILE, data)

def load_inventory():
    return load_json(INVENTORY_FILE)

def save_inventory(data):
    save_json(INVENTORY_FILE, data)

def load_papers():
    return load_json(PAPER_FILE)

def save_papers(data):
    save_json(PAPER_FILE, data)

def load_experiments():
    return load_json(EXPERIMENT_FILE)

def save_experiments(data):
    save_json(EXPERIMENT_FILE, data)

def load_manuals():
    return load_json(MANUAL_FILE)

def save_manuals(data):
    save_json(MANUAL_FILE, data)

# -------------------------------------------------
# 세션 상태 초기화
# -------------------------------------------------
if "selected_experiment_id" not in st.session_state:
    st.session_state.selected_experiment_id = None

if "edit_experiment_id" not in st.session_state:
    st.session_state.edit_experiment_id = None

# -------------------------------------------------
# CSS 스타일
# -------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #050816;
    color: white;
}
.main-title {
    font-size: 42px;
    font-weight: 800;
    color: white;
    margin-bottom: 10px;
}
hr {
    border: 1px solid #1c2333;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: white;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 15px;
}
.stTabs [aria-selected="true"] {
    background-color: #111827;
    border-bottom: 2px solid #ff4b4b;
}
.fc {
    background-color: #050816;
    color: white;
}
.fc-toolbar-title {
    color: white !important;
    font-size: 32px !important;
    font-weight: bold !important;
}
.fc-daygrid-day-number {
    color: white !important;
    font-weight: 600;
}
.fc-col-header-cell-cushion {
    color: white !important;
    font-size: 16px;
    font-weight: bold;
}
.fc-event {
    border-radius: 6px !important;
    border: none !important;
    padding: 4px !important;
    font-size: 12px !important;
}
.fc-button {
    background-color: #111827 !important;
    border: 1px solid #374151 !important;
}
.fc-button:hover {
    background-color: #1f2937 !important;
}
.fc-theme-standard td,
.fc-theme-standard th {
    border: 1px solid #1c2333 !important;
}
.fc-scrollgrid {
    border: 1px solid #1c2333 !important;
}
.fc-daygrid-event {
    white-space: normal !important;
    align-items: flex-start !important;
}
.fc-event-title {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.3 !important;
}
.fc-event-time {
    font-weight: bold !important;
    margin-right: 4px !important;
}
.fc-h-event {
    min-height: 45px !important;
}
.fc-daygrid-day-frame {
    min-height: 140px !important;
}
.block-box {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}
.small-muted {
    color: #9ca3af;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 유틸 함수
# -------------------------------------------------
def generate_id(prefix="id"):
    return f"{prefix}_{uuid4().hex[:12]}"

def safe_str(v):
    return "" if v is None else str(v)

def save_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return "", ""
    ext = os.path.splitext(uploaded_file.name)[1]
    unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}{ext}"
    save_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return uploaded_file.name, save_path

def save_manual_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return "", "", ""
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}{ext}"
    save_path = os.path.join(MANUAL_UPLOAD_DIR, unique_name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
        file_type = "image"
    elif ext == ".pdf":
        file_type = "pdf"
    else:
        file_type = "document"

    return uploaded_file.name, save_path, file_type

def update_linked_calendar_event(experiment):
    events = load_events()
    target_id = experiment["id"]
    found = False

    for ev in events:
        if ev.get("event_type") == "experiment" and ev.get("experiment_id") == target_id:
            ev["title"] = f"🧪 {experiment.get('장비', '')} | {experiment.get('연구명', '')}"
            ev["start"] = f"{experiment.get('날짜', '')}T{experiment.get('시작시간', '00:00')}"
            ev["color"] = get_event_color_by_device(experiment.get("장비", ""))
            ev["important"] = False
            ev["experiment_id"] = target_id
            ev["event_type"] = "experiment"
            found = True
            break

    if not found:
        events.append({
            "id": generate_id("event"),
            "title": f"🧪 {experiment.get('장비', '')} | {experiment.get('연구명', '')}",
            "start": f"{experiment.get('날짜', '')}T{experiment.get('시작시간', '00:00')}",
            "color": get_event_color_by_device(experiment.get("장비", "")),
            "important": False,
            "event_type": "experiment",
            "experiment_id": target_id
        })

    save_events(events)

def delete_linked_calendar_event(experiment_id):
    events = load_events()
    events = [
        ev for ev in events
        if not (ev.get("event_type") == "experiment" and ev.get("experiment_id") == experiment_id)
    ]
    save_events(events)

def get_event_color_by_device(device):
    color_map = {
        "RF Sputter": "#ef4444",
        "ALD": "#22c55e",
        "Furnace": "#f59e0b",
        "E-beam Evaporator": "#3b82f6",
        "Thermal Evaporator": "#8b5cf6",
        "PECVD": "#06b6d4",
        "RIE": "#ec4899",
        "Probe Station": "#84cc16",
        "기타": "#94a3b8"
    }
    return color_map.get(device, "#94a3b8")

def flatten_experiment_for_table(exp):
    common_cols = {
        "ID": exp.get("id", ""),
        "날짜": exp.get("날짜", ""),
        "시작시간": exp.get("시작시간", ""),
        "연구명": exp.get("연구명", ""),
        "장비": exp.get("장비", ""),
        "사용자": exp.get("사용자", ""),
        "가스종류": exp.get("가스종류", ""),
        "가스유량(sccm)": exp.get("가스유량(sccm)", ""),
        "타겟": exp.get("타겟", ""),
        "기판": exp.get("기판", ""),
        "Base진공도(Torr)": exp.get("Base진공도(Torr)", ""),
        "Work진공도(mTorr)": exp.get("Work진공도(mTorr)", ""),
        "기판온도(℃)": exp.get("기판온도(℃)", ""),
        "공정시간(min)": exp.get("공정시간(min)", ""),
        "증착두께(nm)": exp.get("증착두께(nm)", ""),
        "증착률(Å/s)": exp.get("증착률(Å/s)", ""),
        "첨부파일명": exp.get("첨부파일명", ""),
        "첨부파일경로": exp.get("첨부파일경로", ""),
        "비고": exp.get("비고", "")
    }

    device_specific = exp.get("장비별데이터", {})
    for k, v in device_specific.items():
        common_cols[k] = v

    return common_cols

def experiments_to_dataframe(experiments):
    if len(experiments) == 0:
        return pd.DataFrame()
    rows = [flatten_experiment_for_table(exp) for exp in experiments]
    return pd.DataFrame(rows)

def to_excel_bytes(df):
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Experiments")
        output.seek(0)
        return output.getvalue()
    except ModuleNotFoundError:
        try:
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Experiments")
            output.seek(0)
            return output.getvalue()
        except ModuleNotFoundError:
            st.error("Excel 다운로드를 위해 openpyxl 또는 xlsxwriter 설치가 필요합니다.")
            return None

def get_device_fields(device):
    if device == "RF Sputter":
        return [
            ("rf_power_w", "RF 파워 (W)", "number_int", 0),
            ("dc_power_w", "DC 파워 (W)", "number_int", 0),
            ("working_pressure_mtorr", "Work 진공도 (mTorr)", "number_float", 0.0),
            ("base_pressure_torr", "Base 진공도 (Torr)", "number_float4", 0.0),
            ("ar_flow_sccm", "Ar 유량 (sccm)", "number_float", 0.0),
            ("o2_flow_sccm", "O2 유량 (sccm)", "number_float", 0.0),
            ("target", "타겟 (Target)", "text", ""),
            ("substrate", "기판", "text", ""),
            ("substrate_temp_c", "기판 온도 (℃)", "number_int", 25),
            ("time_min", "공정 시간 (min)", "number_int", 30),
            ("thickness_nm", "증착 두께 (nm)", "number_float", 0.0),
            ("rate_as", "증착률 (Å/s)", "number_float2", 0.0)
        ]
    elif device == "ALD":
        return [
            ("base_pressure_torr", "Base 진공도 (Torr)", "number_float4", 0.0),
            ("process_pressure_torr", "Process 압력 (Torr)", "number_float4", 0.0),
            ("precursor_a", "Precursor A", "text", ""),
            ("precursor_b", "Precursor B", "text", ""),
            ("pulse_a_s", "Pulse A (s)", "number_float2", 0.1),
            ("purge_a_s", "Purge A (s)", "number_float2", 5.0),
            ("pulse_b_s", "Pulse B (s)", "number_float2", 0.1),
            ("purge_b_s", "Purge B (s)", "number_float2", 5.0),
            ("cycles", "사이클 수", "number_int", 100),
            ("substrate_temp_c", "기판 온도 (℃)", "number_int", 150),
            ("growth_per_cycle_a", "GPC (Å/cycle)", "number_float3", 0.0),
            ("thickness_nm", "박막 두께 (nm)", "number_float", 0.0)
        ]
    elif device == "Furnace":
        return [
            ("base_pressure_torr", "초기 압력 (Torr)", "number_float4", 0.0),
            ("process_gas", "공정 가스", "text", ""),
            ("gas_flow_sccm", "가스 유량 (sccm)", "number_float", 0.0),
            ("ramp_rate_c_min", "승온 속도 (℃/min)", "number_float", 10.0),
            ("target_temp_c", "목표 온도 (℃)", "number_int", 800),
            ("hold_time_min", "유지 시간 (min)", "number_int", 30),
            ("cooling_type", "냉각 방식", "text", ""),
            ("sample_count", "시편 수", "number_int", 1)
        ]
    else:
        return [
            ("base_pressure_torr", "Base 진공도 (Torr)", "number_float4", 0.0),
            ("process_pressure", "Process 조건", "text", ""),
            ("power", "파워/출력", "text", ""),
            ("temperature", "온도", "text", ""),
            ("time_min", "공정 시간 (min)", "number_int", 30),
            ("target", "타겟/재료", "text", ""),
            ("result", "결과", "text", "")
        ]

def render_dynamic_fields(device, prefix, existing=None):
    if existing is None:
        existing = {}

    fields = get_device_fields(device)
    values = {}

    st.markdown(f"#### {device} 맞춤 입력 항목")

    cols = st.columns(2)
    for i, (name, label, field_type, default) in enumerate(fields):
        val = existing.get(name, default)
        key = f"{prefix}_{device}_{name}"
        with cols[i % 2]:
            if field_type == "text":
                values[name] = st.text_input(label, value=safe_str(val), key=key)
            elif field_type == "number_int":
                try:
                    val = int(val)
                except:
                    val = int(default)
                values[name] = st.number_input(label, min_value=0, step=1, value=val, key=key)
            elif field_type == "number_float":
                try:
                    val = float(val)
                except:
                    val = float(default)
                values[name] = st.number_input(label, min_value=0.0, step=0.1, value=val, key=key)
            elif field_type == "number_float2":
                try:
                    val = float(val)
                except:
                    val = float(default)
                values[name] = st.number_input(label, min_value=0.0, step=0.01, value=val, format="%.2f", key=key)
            elif field_type == "number_float3":
                try:
                    val = float(val)
                except:
                    val = float(default)
                values[name] = st.number_input(label, min_value=0.0, step=0.001, value=val, format="%.3f", key=key)
            elif field_type == "number_float4":
                try:
                    val = float(val)
                except:
                    val = float(default)
                values[name] = st.number_input(label, min_value=0.0, step=0.0001, value=val, format="%.4f", key=key)
    return values

def parse_calendar_click(result):
    if not result:
        return None

    if isinstance(result, dict):
        if result.get("callback") == "eventClick":
            ev = result.get("eventClick", {})
            if isinstance(ev, dict):
                if "event" in ev and isinstance(ev["event"], dict):
                    return ev["event"]
                return ev

        for key in ["eventClick", "event", "selected", "selection"]:
            val = result.get(key)
            if isinstance(val, dict):
                if "event" in val and isinstance(val["event"], dict):
                    return val["event"]
                return val

    return None

def find_experiment_by_id(experiments, exp_id):
    for exp in experiments:
        if exp.get("id") == exp_id:
            return exp
    return None

def build_experiment_record(
    mode,
    record_id,
    exp_name,
    user_name,
    process_date,
    start_time,
    device_name,
    gas_kind,
    gas_flow,
    substrate,
    note,
    uploaded_file,
    old_record=None,
    device_specific=None
):
    original_file_name = ""
    saved_file_path = ""

    if mode == "edit" and old_record is not None:
        original_file_name = old_record.get("첨부파일명", "")
        saved_file_path = old_record.get("첨부파일경로", "")

    if uploaded_file is not None:
        original_file_name, saved_file_path = save_uploaded_file(uploaded_file)

    record = {
        "id": record_id,
        "날짜": str(process_date),
        "시작시간": str(start_time)[:5],
        "연구명": exp_name.strip(),
        "사용자": user_name.strip(),
        "장비": device_name,
        "가스종류": gas_kind,
        "가스유량(sccm)": gas_flow,
        "기판": substrate.strip(),
        "첨부파일명": original_file_name,
        "첨부파일경로": saved_file_path,
        "비고": note.strip(),
        "장비별데이터": device_specific if device_specific is not None else {}
    }

    ds = record["장비별데이터"]

    record["타겟"] = ds.get("target", "")
    record["Base진공도(Torr)"] = ds.get("base_pressure_torr", "")
    record["Work진공도(mTorr)"] = ds.get("working_pressure_mtorr", "")
    record["기판온도(℃)"] = ds.get("substrate_temp_c", ds.get("target_temp_c", ""))
    record["공정시간(min)"] = ds.get("time_min", ds.get("hold_time_min", ""))
    record["증착두께(nm)"] = ds.get("thickness_nm", "")
    record["증착률(Å/s)"] = ds.get("rate_as", "")

    return record

# -------------------------------------------------
# 탭 메뉴
# -------------------------------------------------
tabs = st.tabs([
    "📌 중요 일정",
    "📘 매뉴얼",
    "📊 실험 데이터",
    "📄 논문 관리",
    "📦 소모품 재고",
    "🛒 필요 물품",
    "⚙ 장비 관리",
    "🛠 고장/수리"
])

# -------------------------------------------------
# 중요 일정
# -------------------------------------------------
with tabs[0]:
    st.markdown("## 🗓 연구실 월간 스케줄러")

    events = load_events()
    experiments = load_experiments()

    with st.expander("➕ 일정 추가"):
        title = st.text_input("일정 제목", key="schedule_title")
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input("날짜", value=date.today(), key="schedule_date")
        with col2:
            start_time = st.time_input("시간", key="schedule_time")

        important = st.checkbox("⭐ 중요 일정", key="schedule_important")
        color = st.color_picker("색상 선택", "#1e90ff", key="schedule_color")

        if st.button("일정 저장", key="save_schedule_btn"):
            if title.strip() == "":
                st.warning("일정 제목을 입력하세요.")
            else:
                display_title = f"⭐ {title}" if important else title
                new_event = {
                    "id": generate_id("event"),
                    "title": display_title,
                    "start": f"{start_date}T{str(start_time)[:5]}",
                    "color": color,
                    "important": important,
                    "event_type": "general"
                }
                events.append(new_event)
                save_events(events)
                st.success("일정 저장 완료!")
                st.rerun()

    st.markdown("---")

    events = sorted(events, key=lambda x: x.get("start", ""))

    calendar_options = {
        "initialView": "dayGridMonth",
        "locale": "ko",
        "height": 950,
        "displayEventTime": True,
        "eventTimeFormat": {
            "hour": "2-digit",
            "minute": "2-digit",
            "hour12": False
        },
        "eventDisplay": "block",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        }
    }

    cal_result = calendar(
        events=events,
        options=calendar_options,
        key="research_calendar"
    )

    clicked_event = parse_calendar_click(cal_result)

    if clicked_event:
        exp_id = clicked_event.get("experiment_id")
        st.markdown("---")
        st.subheader("🔍 캘린더 선택 상세 정보")

        if exp_id:
            exp = find_experiment_by_id(experiments, exp_id)
            if exp:
                st.markdown('<div class="block-box">', unsafe_allow_html=True)
                st.write(f"**연구명:** {exp.get('연구명', '')}")
                st.write(f"**장비:** {exp.get('장비', '')}")
                st.write(f"**날짜/시간:** {exp.get('날짜', '')} {exp.get('시작시간', '')}")
                st.write(f"**사용자:** {exp.get('사용자', '')}")
                st.write(f"**가스:** {exp.get('가스종류', '')}")
                st.write(f"**가스유량:** {exp.get('가스유량(sccm)', '')} sccm")
                st.write(f"**기판:** {exp.get('기판', '')}")
                st.write(f"**비고:** {exp.get('비고', '')}")

                ds = exp.get("장비별데이터", {})
                if ds:
                    st.markdown("**장비별 상세 조건**")
                    for k, v in ds.items():
                        st.write(f"- {k}: {v}")

                if exp.get("첨부파일경로") and os.path.exists(exp.get("첨부파일경로")):
                    with open(exp.get("첨부파일경로"), "rb") as f:
                        st.download_button(
                            "📎 첨부파일 다운로드",
                            data=f.read(),
                            file_name=exp.get("첨부파일명", "attachment"),
                            key=f"download_attached_{exp_id}"
                        )
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("연결된 실험 데이터를 찾을 수 없습니다.")
        else:
            st.info(f"선택한 일정: {clicked_event.get('title', '')}")

    st.markdown("---")
    st.subheader("🗑 일정 삭제")

    if len(events) == 0:
        st.info("등록된 일정이 없습니다.")
    else:
        for idx, event in enumerate(events):
            col1, col2 = st.columns([8, 1])

            with col1:
                event_time = safe_str(event.get("start", "")).replace("T", " ")
                event_type = event.get("event_type", "general")
                extra = " [실험 연동]" if event_type == "experiment" else ""
                st.write(f"📌 {event_time} | {event.get('title', '')}{extra}")

            with col2:
                if st.button("삭제", key=f"delete_event_{idx}"):
                    events.pop(idx)
                    save_events(events)
                    st.rerun()

# -------------------------------------------------
# 매뉴얼
# -------------------------------------------------
with tabs[1]:
    st.subheader("📘 장비 매뉴얼 저장소")

    manuals = load_manuals()

    manual_device_options = [
        "RF Sputter",
        "E-beam Evaporator",
        "Thermal Evaporator",
        "ALD",
        "PECVD",
        "RIE",
        "Furnace",
        "Probe Station",
        "공통",
        "기타"
    ]

    manual_type_options = [
        "운영 매뉴얼",
        "SOP",
        "점검표",
        "안전 문서",
        "트러블슈팅",
        "교육자료",
        "기타"
    ]

    with st.expander("➕ 매뉴얼 업로드", expanded=True):
        m1, m2 = st.columns(2)
        with m1:
            manual_title = st.text_input("매뉴얼 제목", key="manual_title")
        with m2:
            manual_device = st.selectbox("장비 카테고리", manual_device_options, key="manual_device")

        m3, m4 = st.columns(2)
        with m3:
            manual_type = st.selectbox("문서 유형", manual_type_options, key="manual_type")
        with m4:
            manual_author = st.text_input("등록자", key="manual_author")

        manual_keywords = st.text_input("검색 키워드", key="manual_keywords", help="예: plasma, cleaning, chamber, safety")
        manual_desc = st.text_area("설명", height=100, key="manual_desc")
        manual_file = st.file_uploader(
            "매뉴얼 파일 업로드",
            type=["pdf", "png", "jpg", "jpeg", "gif", "webp", "docx", "pptx", "xlsx", "xls", "txt", "csv"],
            key="manual_upload"
        )

        if st.button("매뉴얼 저장", key="save_manual_btn"):
            if manual_title.strip() == "":
                st.warning("매뉴얼 제목을 입력하세요.")
            elif manual_file is None:
                st.warning("업로드할 파일을 선택하세요.")
            else:
                original_name, saved_path, file_type = save_manual_uploaded_file(manual_file)
                manual_record = {
                    "id": generate_id("manual"),
                    "제목": manual_title.strip(),
                    "장비": manual_device,
                    "유형": manual_type,
                    "등록자": manual_author.strip(),
                    "키워드": manual_keywords.strip(),
                    "설명": manual_desc.strip(),
                    "원본파일명": original_name,
                    "저장경로": saved_path,
                    "파일유형": file_type,
                    "등록일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                manuals.append(manual_record)
                save_manuals(manuals)
                st.success("매뉴얼이 저장되었습니다.")
                st.rerun()

    st.markdown("---")
    st.subheader("🔍 매뉴얼 검색 및 조회")

    if len(manuals) == 0:
        st.info("등록된 매뉴얼이 없습니다.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            manual_filter_device = st.selectbox("장비 필터", ["전체"] + manual_device_options, key="manual_filter_device")
        with f2:
            manual_filter_type = st.selectbox("유형 필터", ["전체"] + manual_type_options, key="manual_filter_type")
        with f3:
            manual_search = st.text_input("검색어", key="manual_search", help="제목, 장비, 키워드, 설명, 파일명 검색")

        filtered_manuals = manuals.copy()

        if manual_filter_device != "전체":
            filtered_manuals = [m for m in filtered_manuals if m.get("장비") == manual_filter_device]

        if manual_filter_type != "전체":
            filtered_manuals = [m for m in filtered_manuals if m.get("유형") == manual_filter_type]

        if manual_search.strip():
            q = manual_search.strip().lower()
            filtered_manuals = [
                m for m in filtered_manuals
                if q in safe_str(m.get("제목")).lower()
                or q in safe_str(m.get("장비")).lower()
                or q in safe_str(m.get("유형")).lower()
                or q in safe_str(m.get("키워드")).lower()
                or q in safe_str(m.get("설명")).lower()
                or q in safe_str(m.get("원본파일명")).lower()
            ]

        if len(filtered_manuals) == 0:
            st.info("조건에 맞는 매뉴얼이 없습니다.")
        else:
            manual_df = pd.DataFrame([
                {
                    "ID": m.get("id", ""),
                    "제목": m.get("제목", ""),
                    "장비": m.get("장비", ""),
                    "유형": m.get("유형", ""),
                    "등록자": m.get("등록자", ""),
                    "파일유형": m.get("파일유형", ""),
                    "원본파일명": m.get("원본파일명", ""),
                    "등록일시": m.get("등록일시", "")
                }
                for m in filtered_manuals
            ])
            st.dataframe(manual_df, use_container_width=True)

            st.markdown("---")
            st.subheader("📚 검색 결과")

            for m in filtered_manuals:
                st.markdown('<div class="block-box">', unsafe_allow_html=True)
                st.write(f"**제목:** {m.get('제목', '')}")
                st.write(f"**장비:** {m.get('장비', '')}")
                st.write(f"**유형:** {m.get('유형', '')}")
                st.write(f"**등록자:** {m.get('등록자', '')}")
                st.write(f"**키워드:** {m.get('키워드', '')}")
                st.write(f"**설명:** {m.get('설명', '')}")
                st.write(f"**파일명:** {m.get('원본파일명', '')}")
                st.write(f"**등록일시:** {m.get('등록일시', '')}")

                file_path = m.get("저장경로", "")
                file_type = m.get("파일유형", "")

                if file_type == "image" and file_path and os.path.exists(file_path):
                    try:
                        st.image(file_path, width=350)
                    except:
                        st.info("이미지 미리보기를 불러올 수 없습니다.")

                c1, c2 = st.columns([1, 1])

                with c1:
                    if file_path and os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button(
                                "📥 다운로드",
                                data=f.read(),
                                file_name=m.get("원본파일명", "manual_file"),
                                key=f"manual_download_{m.get('id')}"
                            )
                    else:
                        st.warning("저장된 파일을 찾을 수 없습니다.")

                with c2:
                    if st.button("🗑 삭제", key=f"manual_delete_{m.get('id')}"):
                        manuals = [x for x in manuals if x.get("id") != m.get("id")]
                        save_manuals(manuals)

                        if file_path and os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except:
                                pass

                        st.success("매뉴얼이 삭제되었습니다.")
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# 실험 데이터
# -------------------------------------------------
with tabs[2]:
    st.subheader("📊 장비별 공정 데이터 기록")

    experiments = load_experiments()

    device_options = [
        "RF Sputter",
        "E-beam Evaporator",
        "Thermal Evaporator",
        "ALD",
        "PECVD",
        "RIE",
        "Furnace",
        "Probe Station",
        "기타"
    ]

    gas_options = [
        "Ar", "O2", "N2", "H2", "NH3", "CF4", "SF6", "Cl2", "기타"
    ]

    with st.expander("➕ 새 실험 등록", expanded=True):
        st.markdown("### 🔬 상세 공정 입력")
        st.caption("장비별 맞춤 입력 폼, 파일 업로드, 캘린더 자동 등록을 지원합니다.")

        uploaded_file = st.file_uploader(
            "첨부 파일 업로드",
            type=["png", "jpg", "jpeg", "pdf", "xlsx", "xls", "csv", "txt"],
            key="exp_upload_new"
        )

        col1, col2 = st.columns(2)
        with col1:
            exp_name = st.text_input("연구명 이름 (실험명)", key="exp_name_new")
        with col2:
            user_name = st.text_input("사용자", key="exp_user_new")

        col3, col4 = st.columns(2)
        with col3:
            process_date = st.date_input("실험 날짜", value=date.today(), key="exp_date_new")
        with col4:
            start_time = st.time_input("실험 시작 시간", key="exp_start_time_new")

        col5, col6 = st.columns(2)
        with col5:
            device_name = st.selectbox("기록할 장비", device_options, key="exp_device_new")
        with col6:
            substrate = st.text_input("기판", key="exp_substrate_new")

        col7, col8 = st.columns(2)
        with col7:
            selected_gas = st.selectbox("사용 가스 종류 선택", gas_options, key="exp_gas_new")
        with col8:
            gas_flow = st.number_input("주 가스 유량 (sccm)", min_value=0.0, value=0.0, step=0.1, key="exp_gas_flow_new")

        device_specific_new = render_dynamic_fields(
            device=device_name,
            prefix="new",
            existing={}
        )

        note = st.text_area("비고 (특이사항)", height=120, key="exp_note_new")

        if st.button("DB 저장 및 캘린더 등록", key="save_experiment_btn"):
            if exp_name.strip() == "":
                st.warning("실험명을 입력하세요.")
            else:
                exp_id = generate_id("exp")
                record = build_experiment_record(
                    mode="new",
                    record_id=exp_id,
                    exp_name=exp_name,
                    user_name=user_name,
                    process_date=process_date,
                    start_time=start_time,
                    device_name=device_name,
                    gas_kind=selected_gas,
                    gas_flow=gas_flow,
                    substrate=substrate,
                    note=note,
                    uploaded_file=uploaded_file,
                    old_record=None,
                    device_specific=device_specific_new
                )
                experiments.append(record)
                save_experiments(experiments)
                update_linked_calendar_event(record)
                st.success("실험 데이터와 캘린더 일정이 저장되었습니다.")
                st.rerun()

    st.markdown("---")
    st.subheader("📋 실험 데이터 조회")

    if len(experiments) == 0:
        st.info("등록된 실험 데이터가 없습니다.")
    else:
        df_all = experiments_to_dataframe(experiments)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            use_start_filter = st.checkbox("시작 날짜 사용", key="use_start_filter")
            filter_start = st.date_input("시작 날짜", value=date.today(), key="filter_start") if use_start_filter else None
        with c2:
            use_end_filter = st.checkbox("종료 날짜 사용", key="use_end_filter")
            filter_end = st.date_input("종료 날짜", value=date.today(), key="filter_end") if use_end_filter else None
        with c3:
            filter_device = st.selectbox("장비 필터", ["전체"] + device_options, key="filter_device")
        with c4:
            search_keyword = st.text_input("검색어", key="exp_search_keyword")

        view_df = df_all.copy()

        if "날짜" in view_df.columns:
            view_df["날짜_dt"] = pd.to_datetime(view_df["날짜"], errors="coerce")

            if filter_start is not None:
                view_df = view_df[view_df["날짜_dt"] >= pd.to_datetime(filter_start)]

            if filter_end is not None:
                view_df = view_df[view_df["날짜_dt"] <= pd.to_datetime(filter_end)]

        if filter_device != "전체":
            view_df = view_df[view_df["장비"] == filter_device]

        if search_keyword.strip():
            mask = (
                view_df["연구명"].astype(str).str.contains(search_keyword, case=False, na=False) |
                view_df["장비"].astype(str).str.contains(search_keyword, case=False, na=False) |
                view_df["가스종류"].astype(str).str.contains(search_keyword, case=False, na=False) |
                view_df["타겟"].astype(str).str.contains(search_keyword, case=False, na=False) |
                view_df["사용자"].astype(str).str.contains(search_keyword, case=False, na=False) |
                view_df["비고"].astype(str).str.contains(search_keyword, case=False, na=False)
            )
            view_df = view_df[mask]

        if "날짜_dt" in view_df.columns:
            view_df = view_df.drop(columns=["날짜_dt"])

        st.dataframe(view_df, use_container_width=True)

        excel_data = to_excel_bytes(view_df)
        if excel_data is not None:
            st.download_button(
                label="📥 Excel 다운로드 (.xlsx)",
                data=excel_data,
                file_name=f"experiment_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_exp_xlsx"
            )

        st.markdown("---")
        st.subheader("🗑 조회 결과에서 바로 삭제")

        if len(view_df) == 0:
            st.info("현재 필터 조건에 해당하는 데이터가 없습니다.")
        else:
            for _, row in view_df.iterrows():
                exp_id = row["ID"]

                col1, col2, col3 = st.columns([7, 1, 1])

                with col1:
                    st.write(
                        f"📌 {row.get('날짜', '')} {row.get('시작시간', '')} | "
                        f"{row.get('연구명', '')} | {row.get('장비', '')} | "
                        f"{row.get('가스종류', '')} {row.get('가스유량(sccm)', '')} sccm"
                    )

                with col2:
                    if st.button("상세", key=f"view_detail_{exp_id}"):
                        st.session_state.selected_experiment_id = exp_id

                with col3:
                    if st.button("삭제", key=f"view_delete_{exp_id}"):
                        target = find_experiment_by_id(experiments, exp_id)

                        if target:
                            file_path = target.get("첨부파일경로", "")
                            experiments = [exp for exp in experiments if exp.get("id") != exp_id]
                            save_experiments(experiments)
                            delete_linked_calendar_event(exp_id)

                            if file_path and os.path.exists(file_path):
                                try:
                                    os.remove(file_path)
                                except:
                                    pass

                            st.success("선택한 실험 데이터가 삭제되었습니다.")
                            st.rerun()

        st.markdown("---")
        st.subheader("🔍 실험 상세 보기")

        selected_view_id = st.selectbox(
            "상세 조회할 실험 선택",
            options=[exp["id"] for exp in experiments],
            format_func=lambda x: next(
                (
                    f"{e.get('날짜', '')} | {e.get('장비', '')} | {e.get('연구명', '')}"
                    for e in experiments if e.get("id") == x
                ),
                x
            ),
            key="detail_experiment_select"
        )

        selected_exp = find_experiment_by_id(experiments, selected_view_id)

        if selected_exp:
            st.markdown('<div class="block-box">', unsafe_allow_html=True)
            st.write(f"**ID:** {selected_exp.get('id', '')}")
            st.write(f"**연구명:** {selected_exp.get('연구명', '')}")
            st.write(f"**장비:** {selected_exp.get('장비', '')}")
            st.write(f"**사용자:** {selected_exp.get('사용자', '')}")
            st.write(f"**날짜/시간:** {selected_exp.get('날짜', '')} {selected_exp.get('시작시간', '')}")
            st.write(f"**가스종류:** {selected_exp.get('가스종류', '')}")
            st.write(f"**가스유량:** {selected_exp.get('가스유량(sccm)', '')} sccm")
            st.write(f"**기판:** {selected_exp.get('기판', '')}")
            st.write(f"**비고:** {selected_exp.get('비고', '')}")

            ds = selected_exp.get("장비별데이터", {})
            if ds:
                st.markdown("**장비별 상세 조건**")
                for k, v in ds.items():
                    st.write(f"- {k}: {v}")

            if selected_exp.get("첨부파일경로") and os.path.exists(selected_exp.get("첨부파일경로")):
                with open(selected_exp.get("첨부파일경로"), "rb") as f:
                    st.download_button(
                        "📎 첨부파일 다운로드",
                        data=f.read(),
                        file_name=selected_exp.get("첨부파일명", "attachment"),
                        key=f"download_exp_file_{selected_exp.get('id')}"
                    )
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("✏ 실험 데이터 수정")

        edit_id = st.selectbox(
            "수정할 실험 선택",
            options=[exp["id"] for exp in experiments],
            format_func=lambda x: next(
                (
                    f"{e.get('날짜', '')} | {e.get('장비', '')} | {e.get('연구명', '')}"
                    for e in experiments if e.get("id") == x
                ),
                x
            ),
            key="edit_experiment_select"
        )

        edit_exp = find_experiment_by_id(experiments, edit_id)

        if edit_exp:
            with st.expander("수정 폼 열기", expanded=False):
                st.caption("새 파일을 업로드하지 않으면 기존 첨부파일을 유지합니다.")

                new_uploaded_file = st.file_uploader(
                    "첨부 파일 교체",
                    type=["png", "jpg", "jpeg", "pdf", "xlsx", "xls", "csv", "txt"],
                    key=f"edit_upload_{edit_id}"
                )

                ec1, ec2 = st.columns(2)
                with ec1:
                    edit_exp_name = st.text_input("연구명 이름 (실험명)", value=edit_exp.get("연구명", ""), key=f"edit_name_{edit_id}")
                with ec2:
                    edit_user_name = st.text_input("사용자", value=edit_exp.get("사용자", ""), key=f"edit_user_{edit_id}")

                ec3, ec4 = st.columns(2)
                with ec3:
                    default_date = pd.to_datetime(edit_exp.get("날짜", date.today()), errors="coerce")
                    if pd.isna(default_date):
                        default_date = pd.to_datetime(date.today())
                    edit_process_date = st.date_input(
                        "실험 날짜",
                        value=default_date.date(),
                        key=f"edit_date_{edit_id}"
                    )
                with ec4:
                    try:
                        default_time = datetime.strptime(edit_exp.get("시작시간", "00:00"), "%H:%M").time()
                    except:
                        default_time = datetime.strptime("00:00", "%H:%M").time()
                    edit_start_time = st.time_input(
                        "실험 시작 시간",
                        value=default_time,
                        key=f"edit_time_{edit_id}"
                    )

                ec5, ec6 = st.columns(2)
                with ec5:
                    default_device = edit_exp.get("장비", device_options[0])
                    device_index = device_options.index(default_device) if default_device in device_options else 0
                    edit_device_name = st.selectbox(
                        "기록할 장비",
                        device_options,
                        index=device_index,
                        key=f"edit_device_{edit_id}"
                    )
                with ec6:
                    edit_substrate = st.text_input("기판", value=edit_exp.get("기판", ""), key=f"edit_substrate_{edit_id}")

                ec7, ec8 = st.columns(2)
                with ec7:
                    default_gas = edit_exp.get("가스종류", gas_options[0])
                    gas_index = gas_options.index(default_gas) if default_gas in gas_options else 0
                    edit_selected_gas = st.selectbox(
                        "사용 가스 종류 선택",
                        gas_options,
                        index=gas_index,
                        key=f"edit_gas_{edit_id}"
                    )
                with ec8:
                    try:
                        gas_default = float(edit_exp.get("가스유량(sccm)", 0.0))
                    except:
                        gas_default = 0.0
                    edit_gas_flow = st.number_input(
                        "주 가스 유량 (sccm)",
                        min_value=0.0,
                        value=gas_default,
                        step=0.1,
                        key=f"edit_gas_flow_{edit_id}"
                    )

                edit_device_specific = render_dynamic_fields(
                    device=edit_device_name,
                    prefix=f"edit_{edit_id}",
                    existing=edit_exp.get("장비별데이터", {})
                )

                edit_note = st.text_area(
                    "비고 (특이사항)",
                    height=120,
                    value=edit_exp.get("비고", ""),
                    key=f"edit_note_{edit_id}"
                )

                if edit_exp.get("첨부파일명"):
                    st.write(f"현재 첨부파일: {edit_exp.get('첨부파일명')}")

                if st.button("수정 저장", key=f"save_edit_{edit_id}"):
                    if edit_exp_name.strip() == "":
                        st.warning("실험명을 입력하세요.")
                    else:
                        updated_record = build_experiment_record(
                            mode="edit",
                            record_id=edit_exp["id"],
                            exp_name=edit_exp_name,
                            user_name=edit_user_name,
                            process_date=edit_process_date,
                            start_time=edit_start_time,
                            device_name=edit_device_name,
                            gas_kind=edit_selected_gas,
                            gas_flow=edit_gas_flow,
                            substrate=edit_substrate,
                            note=edit_note,
                            uploaded_file=new_uploaded_file,
                            old_record=edit_exp,
                            device_specific=edit_device_specific
                        )

                        for i, exp in enumerate(experiments):
                            if exp.get("id") == edit_id:
                                experiments[i] = updated_record
                                break

                        save_experiments(experiments)
                        update_linked_calendar_event(updated_record)
                        st.success("실험 데이터가 수정되었습니다.")
                        st.rerun()

        if st.session_state.selected_experiment_id:
            picked = find_experiment_by_id(experiments, st.session_state.selected_experiment_id)
            if picked:
                st.markdown("---")
                st.subheader("🔎 선택된 실험 상세")
                st.write(f"**연구명:** {picked.get('연구명', '')}")
                st.write(f"**장비:** {picked.get('장비', '')}")
                st.write(f"**날짜/시간:** {picked.get('날짜', '')} {picked.get('시작시간', '')}")
                st.write(f"**사용자:** {picked.get('사용자', '')}")
                st.write(f"**비고:** {picked.get('비고', '')}")

# -------------------------------------------------
# 논문 관리
# -------------------------------------------------
with tabs[3]:
    st.subheader("📄 논문 관리 시스템")

    papers = load_papers()

    with st.expander("➕ 논문 등록"):
        title = st.text_input("논문 제목", key="paper_title")
        authors = st.text_input("저자", key="paper_authors")
        journal = st.text_input("학술지", key="paper_journal")
        year = st.number_input("연도", min_value=2000, max_value=2100, step=1, key="paper_year")
        doi = st.text_input("DOI", key="paper_doi")

        if st.button("논문 저장", key="save_paper_btn"):
            if title.strip() == "":
                st.warning("논문 제목을 입력하세요.")
            else:
                papers.append({
                    "제목": title,
                    "저자": authors,
                    "학술지": journal,
                    "연도": year,
                    "DOI": doi
                })
                save_papers(papers)
                st.success("논문 저장 완료")
                st.rerun()

    st.markdown("---")
    st.subheader("📚 등록 논문")

    if len(papers) == 0:
        st.info("등록된 논문이 없습니다.")
    else:
        df = pd.DataFrame(papers)
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("🗑 논문 삭제")

    for idx, paper in enumerate(papers):
        col1, col2 = st.columns([8, 1])

        with col1:
            st.write(f"📄 {paper['제목']} ({paper['연도']})")

        with col2:
            if st.button("삭제", key=f"paper_{idx}"):
                papers.pop(idx)
                save_papers(papers)
                st.rerun()

# -------------------------------------------------
# 소모품 재고
# -------------------------------------------------
with tabs[4]:
    st.subheader("📦 소모품 재고 관리")

    inventory = load_inventory()

    with st.expander("➕ 소모품 추가"):
        item_name = st.text_input("품목명", key="inventory_name")
        quantity = st.number_input("수량", min_value=0, step=1, key="inventory_qty")
        location = st.text_input("보관 위치", key="inventory_location")

        if st.button("재고 저장", key="save_inventory_btn"):
            if item_name.strip() == "":
                st.warning("품목명을 입력하세요.")
            else:
                inventory.append({
                    "품목명": item_name,
                    "수량": quantity,
                    "위치": location
                })
                save_inventory(inventory)
                st.success("재고 저장 완료")
                st.rerun()

    st.markdown("---")
    st.subheader("📋 현재 재고")

    if len(inventory) == 0:
        st.info("등록된 재고가 없습니다.")
    else:
        df = pd.DataFrame(inventory)
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("🗑 재고 삭제")

    for idx, item in enumerate(inventory):
        col1, col2 = st.columns([8, 1])

        with col1:
            st.write(f"📦 {item['품목명']} | 수량: {item['수량']} | 위치: {item['위치']}")

        with col2:
            if st.button("삭제", key=f"inv_{idx}"):
                inventory.pop(idx)
                save_inventory(inventory)
                st.rerun()

# -------------------------------------------------
# 필요 물품
# -------------------------------------------------
with tabs[5]:
    st.subheader("🛒 필요 물품")
    st.info("구매 요청 기능 추가 예정")

# -------------------------------------------------
# 장비 관리
# -------------------------------------------------
with tabs[6]:
    st.subheader("⚙ 장비 관리")
    st.info("장비 관리 기능 추가 예정")

# -------------------------------------------------
# 고장/수리
# -------------------------------------------------
with tabs[7]:
    st.subheader("🛠 고장/수리")
    st.info("고장 접수 기능 추가 예정")
