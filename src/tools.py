"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Tra cứu hồ sơ dinh dưỡng của khách hàng
    {
        "name": "nutrition_query",
        "description": "Tra cứu hồ sơ dinh dưỡng của khách hàng bằng mã khách hàng.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Mã khách hàng cần tra cứu (ví dụ: 'KH2026001')"
                }
            },
            "required": ["customer_id"]
        }
    },
    
    # --------------------------------------------------------------------------
    # Tool 2: Lập thực đơn theo mục tiêu và ràng buộc dinh dưỡng
    # --------------------------------------------------------------------------
    {
        "name": "create_meal_plan",
        "description": "Tạo thực đơn theo ngày, mục tiêu calo và ràng buộc dị ứng hoặc kiêng cữ.",
        "parameters": {
            "type": "object",
            "properties": {
                "date_range": {
                    "type": "string",
                    "description": "Khoảng ngày cần lập thực đơn, ví dụ: 'ngày mai' hoặc '3 ngày tới'."
                },
                "calorie_target": {
                    "type": "integer",
                    "description": "Mục tiêu calo mỗi ngày."
                },
                "dietary_restrictions": {
                    "type": "string",
                    "description": "Dị ứng, thực phẩm cần tránh hoặc chế độ ăn đặc biệt."
                },
                "meal_time": {
                    "type": "string",
                    "description": "Thời điểm ăn, ví dụ: 'buổi sáng', 'buổi trưa' hoặc 'buổi tối'."
                }
            },
            "required": ["date_range", "calorie_target", "dietary_restrictions", "meal_time"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "KH2026001": {
        "full_name": "Nguyễn Minh An",
        "calorie_target": 1800,
        "protein_target_g": 120,
        "allergies": ["hải sản"],
        "dietary_goal": "giảm mỡ, duy trì cơ"
    },
    "KH2026002": {
        "full_name": "Trần Hà Bình",
        "calorie_target": 2200,
        "protein_target_g": 140,
        "allergies": [],
        "dietary_goal": "duy trì cân nặng"
    }
}


def execute_nutrition_query(customer_id: str) -> str:
    """Thực thi tra cứu hồ sơ dinh dưỡng theo mã khách hàng."""
    customer = MOCK_DATABASE.get(customer_id.strip().upper())
    if customer:
        return json.dumps({
            "status": "SUCCESS",
            "customer_id": customer_id.strip().upper(),
            "data": customer
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy hồ sơ dinh dưỡng của khách hàng có mã '{customer_id}'"
        }, ensure_ascii=False)


def execute_create_meal_plan(
    date_range: str,
    calorie_target: int,
    dietary_restrictions: str,
    meal_time: str
) -> str:
    """Tạo thực đơn cụ thể theo calo, ràng buộc và thời điểm ăn."""
    return json.dumps({
        "status": "SUCCESS",
        "date_range": date_range,
        "calorie_target": calorie_target,
        "dietary_restrictions": dietary_restrictions,
        "meal_time": meal_time,
        "nutrition_note": "Hãy dùng các ràng buộc này để xây dựng thực đơn cụ thể."
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "nutrition_query": execute_nutrition_query,
    "create_meal_plan": execute_create_meal_plan
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
