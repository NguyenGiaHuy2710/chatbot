# Import các thư viện
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Import các hàm tiện ích
from utils.query import (
    get_all_symbol, get_symbol_info, get_latest_price, get_price, 
    get_latest_year_financials, get_latest_quarter_financials
)
from utils.plotly_chart import plot_chart

# Khai báo hàm
def get_tool_declarations():
    """Trả về danh sách các khai báo hàm cho Gemini."""
    return [
        types.FunctionDeclaration(
            name="get_all_symbol",
            description="Lấy tất cả các cổ phiếu hiện có trong CSDL",
            parameters=types.Schema(
                type=types.Type.OBJECT,
            )
        ),
        types.FunctionDeclaration(
            name="get_symbol_info",
            description="Lấy thông tin cơ bản của công ty (tên, sàn, ngày niêm yết, v.v.).",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "symbol": types.Schema(type=types.Type.STRING, description="Mã chứng khoán, ví dụ: VNM, FPT")
                },
                required=["symbol"],
            )
        ),
        types.FunctionDeclaration(
            name="get_latest_price",
            description="Lấy giá hiện tại và các chỉ báo kỹ thuật (RSI, MACD...) của mã chứng khoán.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "symbol": types.Schema(type=types.Type.STRING, description="Mã chứng khoán")
                },
                required=["symbol"],
            )
        ),
        types.FunctionDeclaration(
            name="get_price",
            description="Lấy dữ liệu giá lịch sử (OHLCV) trong khoảng thời gian cụ thể.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "symbol": types.Schema(type=types.Type.STRING, description="Mã chứng khoán"),
                    "start_date": types.Schema(type=types.Type.STRING, description="Ngày bắt đầu (YYYY-MM-DD)"),
                    "end_date": types.Schema(type=types.Type.STRING, description="Ngày kết thúc (YYYY-MM-DD)")
                },
                required=["symbol", "start_date", "end_date"],
            )
        ),
        types.FunctionDeclaration(
            name="plot_chart",
            description="Vẽ biểu đồ giá chứng khoán.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "symbol": types.Schema(type=types.Type.STRING, description="Mã chứng khoán"),
                    "start_date": types.Schema(type=types.Type.STRING, description="Ngày bắt đầu (YYYY-MM-DD)"),
                    "end_date": types.Schema(type=types.Type.STRING, description="Ngày kết thúc (YYYY-MM-DD)")
                },
                required=["symbol"],
            )
        ),
        types.FunctionDeclaration(
            name="get_latest_year_financials",
            description="Lấy chỉ số tài chính theo năm mới nhất (PE, EPS, ROE...).",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "ticker": types.Schema(type=types.Type.STRING, description="Mã chứng khoán")
                },
                required=["ticker"],
            )
        ),
        types.FunctionDeclaration(
            name="get_latest_quarter_financials",
            description="Lấy chỉ số tài chính theo quý mới nhất.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "ticker": types.Schema(type=types.Type.STRING, description="Mã chứng khoán")
                },
                required=["ticker"],
            )
        ),
    ]

# Lớp Chatbot
class StockChatbot:
    def __init__(self):
        load_dotenv()
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Lỗi: Không tìm thấy GOOGLE_API_KEY trong biến môi trường.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash-lite" 

        # Định nghĩa System Prompt
        self.system_prompt = """
        Bạn là trợ lý AI chuyên về phân tích chứng khoán Việt Nam. Năm nay là năm 2025.
        QUY TẮC QUAN TRỌNG:
        - Năm mặc định: 2025. Đơn vị tiền tệ: Nghìn đồng.
        - Dữ liệu: Phải gọi hàm (Tool) để lấy số liệu thực tế (get_price, get_latest_price...), KHÔNG được bịa số liệu.
        - Nếu người dùng hỏi chung chung, hãy tự động lấy dữ liệu mới nhất để phân tích.
        - Nếu dự đoán giá: Bắt buộc gọi hàm lấy dữ liệu lịch sử và đưa ra dự đoán cụ thể từng ngày dựa trên xu hướng.
        - Nếu vẽ biểu đồ: Bắt buộc gọi hàm lấy dữ liệu lịch sử và vẽ biểu đồ dựa trên dữ liệu lấy được từ việc gọi hàm
        - Trả lời ngắn gọn, tập trung vào insight tài chính.
        """

        # Ánh xạ hàm thực tế
        self.available_functions_map = {
            "get_all_symbol": get_all_symbol, # Hàm lấy danh sách các cổ phiếu hiện có
            "get_symbol_info": get_symbol_info, # Hàm lấy thông tin cổ phiếu
            "get_latest_price": get_latest_price, # Hàm lấy giá cổ phiếu gần nhất (150 ngày)
            "get_price": get_price, # Hàm lấy danh sách các cổ phiếu trong khoảng thời gian
            "plot_chart": plot_chart, # Hàm vẽ biểu đồ 
            "get_latest_year_financials": get_latest_year_financials, # Hàm lấy báo cáo tài chính theo năm
            "get_latest_quarter_financials": get_latest_quarter_financials, # Hàm lấy báo cáo tài chính theo quý
        }

        # Cấu hình Tool (Gộp tất cả declaration vào 1 Tool) Tool chứa danh sách các function_declarations
        self.tools_config = [
            types.Tool(function_declarations=get_tool_declarations())
        ]

        # 4. Khởi tạo Chat Session
        self.create_chat_session()

    def create_chat_session(self):
        """Khởi tạo hoặc đặt lại phiên chat."""
        self.chat_session = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                tools=self.tools_config
            )
        )
        self.conversation_history = []

    def get_response(self, user_message: str) -> str:
        try:
            # Gửi tin nhắn đầu tiên
            response = self.chat_session.send_message(user_message)

            # Vòng lặp xử lý Function Calling
            # Gemini có thể gọi nhiều hàm liên tiếp hoặc gọi hàm nhiều lần
            while response.function_calls:
                function_responses = []

                for call in response.function_calls:
                    fn_name = call.name
                    fn_args = call.args
                    
                    # Chuyển đổi args thành dict thuần Python nếu cần thiết
                    if not isinstance(fn_args, dict):
                        try:
                            fn_args = dict(fn_args)
                        except:
                            pass 

                    print(f"Đang gọi hàm: {fn_name} với tham số {fn_args}")

                    if fn_name in self.available_functions_map:
                        try:
                            # Gọi hàm thực thi
                            func_to_call = self.available_functions_map[fn_name]
                            api_result = func_to_call(**fn_args)
                            
                            # Kết quả trả về phải là Dict hoặc JSON string
                            result_content = api_result if isinstance(api_result, (dict, str)) else str(api_result)
                            
                            function_responses.append(
                                types.Part.from_function_response(
                                    name=fn_name,
                                    response={"result": result_content}
                                )
                            )
                        except Exception as e:
                            # Báo lỗi lại cho Gemini nếu có lỗi
                            error_msg = f"Lỗi khi thực thi hàm {fn_name}: {str(e)}"
                            print(error_msg)
                            function_responses.append(
                                types.Part.from_function_response(
                                    name=fn_name,
                                    response={"error": error_msg}
                                )
                            )
                    else:
                        function_responses.append(
                            types.Part.from_function_response(
                                name=fn_name,
                                response={"error": f"Hàm {fn_name} không tồn tại."}
                            )
                        )

                # Gửi kết quả thực thi hàm trở lại cho Gemini
                if function_responses:
                    response = self.chat_session.send_message(function_responses)
                else:
                    break

            return response.text

        except APIError as e:
            return f"Lỗi API Gemini: {str(e)}"
        except Exception as e:
            return f"Lỗi hệ thống: {str(e)}"

    def clear_conversation(self):
        self.create_chat_session()
        print("Đã xóa lịch sử trò chuyện.")


if __name__ == "__main__":
    try:
        bot = StockChatbot()
        print("Chatbot đã sẵn sàng! Gõ 'exit' hoặc 'quit' để thoát.")
        
        while True:
            user_input = input("\nBạn: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # Giả lập spinner
            print("Gemini đang suy nghĩ...")
            reply = bot.get_response(user_input)
            print(f"Bot: {reply}")
            
    except Exception as e:
        print(f"Khởi tạo thất bại: {e}")