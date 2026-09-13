"""
🚀 CORE AGENT APPLICATION (DAY 03: CHATBOT VS REACT AGENT)
Thực thi so sánh giữa Chatbot Baseline (Cấp 2) và ReAct Agent kết nối MCP Server (Cấp 3).
"""

import json
import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from mcp_server import MCPAcademicServer
from prompts import (
    CHATBOT_BASELINE_PROMPT,
    REACT_AGENT_SYSTEM_PROMPT,
    MAX_ITERATIONS
)
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Tải danh sách 5 test cases từ config/test_cases.json hoặc config/test_cases.example.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    if not os.path.exists(config_path):
        example_path = os.path.join(base_dir, "config", "test_cases.example.json")
        if os.path.exists(example_path):
            print("⚠️ [CONFIG NOTICE]: Chưa thấy file 'config/test_cases.json'. Đang dùng mẫu 'config/test_cases.example.json'.")
            print("👉 Hãy chạy: copy config/test_cases.example.json config/test_cases.json và viết test cases theo đề tài của bạn!\n")
            config_path = example_path
        else:
            config_path = "test_cases.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_waterfall_trace(trace_data: list):
    """Ghi vết log Waterfall Trace Log ra file docs/trace_waterfall.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    trace_path = os.path.join(docs_dir, "trace_waterfall.json")
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, ensure_ascii=False, indent=2)
    print(f"📊 [OBSERVABILITY]: Đã lưu {len(trace_data)} sự kiện Waterfall Trace tại '{trace_path}'!")


def run_baseline_chatbot(user_query: str, provider):
    """Chạy Chatbot gốc (Cấp 2) không có công cụ gọi Tool"""
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot phản hồi:\n{response}")


def answer_common_nutrition_question(user_query: str):
    """Trả lời kiến thức chung local, không gọi LLM/API."""
    normalized_query = user_query.lower().strip()
    common_topics = (
        "calo", "protein", "carbohydrate", "tinh bột", "chất béo",
        "vitamin", "chất xơ", "uống nước", "dinh dưỡng là gì",
        "ăn uống lành mạnh", "chế độ ăn lành mạnh"
    )
    personalized_topics = (
        "thực đơn", "bữa ăn", "hồ sơ", "khách hàng", "kh202", "dị ứng",
        "mục tiêu", "calo của tôi", "cá nhân hóa", "tạo món"
    )
    if not any(topic in normalized_query for topic in common_topics):
        return None
    if any(topic in normalized_query for topic in personalized_topics):
        return None

    if "protein" in normalized_query:
        answer = (
            "Protein giúp xây dựng và phục hồi cơ bắp, đồng thời hỗ trợ cảm giác no. "
            "Nguồn protein có thể gồm trứng, sữa, cá, thịt nạc, đậu phụ và các loại đậu."
        )
    elif "calo" in normalized_query:
        answer = (
            "Calo là đơn vị đo năng lượng từ thực phẩm. Nhu cầu calo phụ thuộc vào "
            "tuổi, giới tính, cân nặng, chiều cao và mức độ vận động của mỗi người."
        )
    elif "chất xơ" in normalized_query:
        answer = "Chất xơ hỗ trợ tiêu hóa và giúp no lâu. Rau xanh, trái cây, đậu và ngũ cốc nguyên hạt là những nguồn phổ biến."
    elif "uống nước" in normalized_query:
        answer = "Nên uống nước đều trong ngày và điều chỉnh theo thời tiết, mức vận động và tình trạng sức khỏe."
    else:
        answer = "Một chế độ ăn cân bằng thường kết hợp đủ protein, rau củ, chất xơ, chất béo tốt và tinh bột phù hợp với nhu cầu năng lượng."

    return {
        "type": "text",
        "content": answer,
        "thought": "Câu hỏi thuộc nhóm kiến thức dinh dưỡng chung; trả lời local, không gọi API."
    }


def synthesize_final_answer(user_query: str, tool_name: str, observation: dict, provider) -> str:
    """Để LLM tổng hợp câu trả lời cuối từ Observation thực tế của tool."""
    synthesis_prompt = (
        "Hãy trả lời người dùng dựa duy nhất trên Observation từ tool dưới đây. "
        "Nếu tool là create_meal_plan, hãy tự xây dựng thực đơn cụ thể với tên món, "
        "khẩu phần và phân bổ calo phù hợp; không trả JSON và không nói 'đã xử lý qua MCP'. "
        "Không bịa dữ liệu hồ sơ ngoài Observation.\n\n"
        f"Câu hỏi người dùng: {user_query}\n"
        f"Tool: {tool_name}\n"
        f"Observation: {json.dumps(observation, ensure_ascii=False)}"
    )
    return provider.generate(
        synthesis_prompt,
        system_prompt=REACT_AGENT_SYSTEM_PROMPT
    )


def run_react_agent(user_query: str, provider, mcp_server: MCPAcademicServer) -> list:
    """
    [REACT AGENT LOOP] Thực thi vòng lặp Thought -> Action -> Observation với MCP Server
    Trả về danh sách trace log của phiên thực thi.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    
    step = 0
    trace_logs = []
    tools_list = mcp_server.list_tools()

    local_response = answer_common_nutrition_question(user_query)
    if local_response:
        print(f"🧠 [Thought]: {local_response['thought']}")
        print(f"🏁 [Final Answer]: {local_response['content']}")
        trace_logs.append({
            "step": 1,
            "query": user_query,
            "action_type": "LOCAL_KNOWLEDGE",
            "provider": "local",
            "thought": local_response["thought"],
            "output": local_response["content"],
            "latency_ms": 0.0
        })
        return trace_logs
    
    while step < MAX_ITERATIONS:
        step += 1
        step_start_time = time.time()
        print(f"\n--- 🔄 Vòng lặp ReAct Loop (Step {step}/{MAX_ITERATIONS}) ---")
        
        # Gọi LLM với Native Tool Calling Specs
        llm_response = provider.generate_with_tools(user_query, tools_list, system_prompt=REACT_AGENT_SYSTEM_PROMPT)
        latency_ms = round((time.time() - step_start_time) * 1000, 2)
        
        thought = llm_response.get("thought", "Đang suy luận...")
        print(f"🧠 [Thought]: {thought}")
        
        # Trường hợp 1: LLM quyết định trả lời bằng văn bản trực tiếp
        if llm_response.get("type") in {"text", "error"}:
            final_content = llm_response.get("content", "")
            print(f"🏁 [Final Answer]: {final_content}")
            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "FINAL_ANSWER",
                "thought": thought,
                "output": final_content,
                "latency_ms": latency_ms
            })
            break
            
        # Trường hợp 2: LLM đề xuất gọi Tool (Action)
        elif llm_response.get("type") == "tool_call":
            tool_name = llm_response.get("tool_name")
            arguments = llm_response.get("arguments", {})
            
            print(f"🛠️ [Action Proposed]: {tool_name}({arguments})")
            
            # Thực thi Tool qua MCP Server
            mcp_result = mcp_server.call_tool(tool_name, arguments)
            obs_data = mcp_result.get("result", {})
            
            if not obs_data:
                print(f"👁️ [Observation từ MCP Server]: {{}}")
                print(f"⚠️ [CHÚ Ý]: MCP Server trả về kết quả rỗng! Học viên cần hoàn thành TODO 2.1 trong 'src/mcp_server.py'.")
                final_answer = "Chưa thể trả lời chi tiết do chưa nhận được dữ liệu từ MCP Server (hãy hoàn thành TODO 2.1)."
            else:
                obs_str = json.dumps(obs_data, ensure_ascii=False)
                print(f"👁️ [Observation từ MCP Server]: {obs_str}")
                
                final_answer = synthesize_final_answer(
                    user_query,
                    tool_name,
                    obs_data,
                    provider
                )
            
            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "TOOL_EXECUTION",
                "tool_name": tool_name,
                "arguments": arguments,
                "observation": obs_data,
                "latency_ms": latency_ms
            })
            
            # Kết thúc vòng lặp sau khi hoàn tất Observation và xuất Final Answer
            print(f"🧠 [Thought]: Đã nhận được dữ liệu từ MCP Server. Tổng hợp kết quả phản hồi.")
            print(f"🏁 [Final Answer]: {final_answer}")
            
            trace_logs.append({
                "step": step + 1,
                "query": user_query,
                "action_type": "FINAL_ANSWER",
                "thought": "Tổng hợp kết quả từ MCP Server thành công.",
                "output": final_answer,
                "latency_ms": 10.0
            })
            break

    return trace_logs


if __name__ == "__main__":
    print("==========================================================")
    print("🥗 VINUNI AI COURSE - DAY 03 LAB: NUTRITION REACT AGENT")
    print("==========================================================")
    
    provider = get_llm_provider()
    mcp_server = MCPAcademicServer()
    
    print(f"🔌 LLM Provider: {provider.__class__.__name__}")
    print(f"🌐 MCP Server: {mcp_server.server_name}\n")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases thử nghiệm.\n")
    
    if "--interactive" in sys.argv:
        print("🎮 [INTERACTIVE MODE] Trò chuyện trực tiếp với ReAct Agent:")
        print("💡 Gợi ý câu hỏi thử nghiệm:")
        print("   - Kiến thức chung: 'Calo và protein có vai trò gì trong chế độ ăn?'")
        print("   - Tra cứu hồ sơ: 'Hãy tra cứu hồ sơ dinh dưỡng của khách hàng KH2026001'")
        print("   - Tạo thực đơn: 'Hãy tạo thực đơn ngày mai, 1800 calo, không có hải sản'")
        print("   - Gõ 'exit' hoặc 'quit' để kết thúc phiên trò chuyện.\n")
        while True:
            try:
                user_input = input("👤 Khách hàng hỏi: ").strip()
                if not user_input or user_input.lower() in ["exit", "quit"]:
                    print("👋 Tạm biệt! Kết thúc phiên trò chuyện.")
                    break
                logs = run_react_agent(user_input, provider, mcp_server)
                save_waterfall_trace(logs)
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Đã thoát phiên tương tác.")
                break
    elif "--all" in sys.argv:
        print("🚀 [TEST SUITE MODE] Kiểm tra 5 Test Cases:")
        completed_count = 0
        todo_count = 0
        all_traces = []
        
        for tc in tests:
            print(f"\n==================================================")
            print(f"🧪 [{tc['id']}] Loại test: {tc['type']} (Độ phức tạp: {tc['complexity']})")
            print(f"📌 Kỳ vọng: {tc['expected_behavior']}")
            
            if tc["question"].strip().startswith("TODO"):
                print(f"⏸️ [CHƯA KÍCH HOẠT - ĐANG LÀ TODO]:")
                print(f"   {tc['question']}")
                print(f"   👉 Hãy mở file 'config/test_cases.json' để viết câu hỏi thực tế cho Test Case này!")
                todo_count += 1
            else:
                logs = run_react_agent(tc["question"], provider, mcp_server)
                all_traces.extend(logs)
                completed_count += 1
                
        print(f"\n==================================================")
        print(f"📊 [KẾT QUẢ TEST SUITE]: Đã thực thi {completed_count}/{len(tests)} Test Cases | {todo_count} Test Cases đang chờ điền câu hỏi (TODO)")
        if all_traces:
            save_waterfall_trace(all_traces)
        print(f"💡 Để trò chuyện trực tiếp từng câu: Chạy 'python src/app.py --interactive'")
    else:
        # Chế độ mặc định khi chỉ gõ 'python src/app.py'
        print("ℹ️ HƯỚNG DẪN SỬ DỤNG CHƯƠNG TRÌNH:")
        print("  1. Chat trực tiếp liên tục:   python src/app.py --interactive")
        print("  2. Chạy toàn bộ Test Cases:    python src/app.py --all\n")
        
        sample_query = tests[1]["question"]
        print(f"--- 🏁 DEMO CHẠY THỬ 1 TEST CASE MẪU (TC02: Tra cứu dinh dưỡng) ---")
        logs = run_react_agent(sample_query, provider, mcp_server)
        save_waterfall_trace(logs)
        print("\n💡 Hãy thử ngay lệnh: python src/app.py --interactive để chat trực tiếp!")
