from collections import defaultdict
from pprint import pprint

# 원본 테이블 데이터 (dict 형태)
rows = [
    {
        "process_id": "process_id#1",
        "step_seq": "REWORK001",
        "ppid": "ppid#1",
        "eqp_id": "EQP_01",
        "chamber_id": "EX1",
        "root_lot_id": "RTAAA",
        "wafer_id_array": ["01", "02", "03"],
    },
    {
        "process_id": "process_id#2",
        "step_seq": "REWORK002",
        "ppid": "ppid#2",
        "eqp_id": "EQP_02",
        "chamber_id": "EX2",
        "root_lot_id": "RTAAB",
        "wafer_id_array": ["04", "05", "06"],
    },
    {
        "process_id": "process_id#3",
        "step_seq": "REWORK003",
        "ppid": "ppid#3",
        "eqp_id": "EQP_03",
        "chamber_id": "EX1",
        "root_lot_id": "RTAAC",
        "wafer_id_array": ["07", "08"],
    },
]

# ------------------------------------------------------
# 변환 로직
# ------------------------------------------------------

# sets 생성
sets = []
unique_root_lot_ids = set()

for row in rows:
    root_lot_id = row["root_lot_id"]

    if root_lot_id not in unique_root_lot_ids:
        unique_root_lot_ids.add(root_lot_id)

        sets.append({
            "id": root_lot_id,
            "label": root_lot_id,
        })

# steps 구조 생성
step_map = defaultdict(lambda: {
    "step_seq": "",
    "sets": {}
})

group_counter = 1

for row in rows:
    step_seq = row["step_seq"]
    root_lot_id = row["root_lot_id"]

    step_item = step_map[step_seq]
    step_item["step_seq"] = step_seq

    # set 초기화
    if root_lot_id not in step_item["sets"]:
        step_item["sets"][root_lot_id] = {
            "subgroups": []
        }

    subgroup = {
        "group_id": f"GROUP_{group_counter:03d}",
        "ppid": row["ppid"],
        "eqp": row["eqp_id"],
        "chamber_id": row["chamber_id"],
        "wafers": row["wafer_id_array"],
    }

    step_item["sets"][root_lot_id]["subgroups"].append(subgroup)

    group_counter += 1

# 최종 결과
result = {
    "sets": sets,
    "steps": list(step_map.values())
}

# 출력
pprint(result, width=120)
