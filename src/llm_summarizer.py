
from openai import OpenAI
import threading
import time

class LocalLLMSummarizer:
    def __init__(self, base_url="http://localhost:11434/v1", api_key="ollama", model="llama3"):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def summarize(self, text, prompt_prefix="以下の文章を要約してください:\n\n", stream_callback=None):
        """
        ローカルLLMを使って要約を生成する
        stream_callback: 部分的なテキストを受け取る関数 (text_chunk) -> None
        """
        if not text:
            return "テキストが空です。"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                    {"role": "user", "content": f"{prompt_prefix}{text}"}
                ],
                stream=True  # 常にストリーム有効にする（コールバックがない場合は全部結合して返す）
            )
            
            full_text = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_text += content
                    if stream_callback:
                        stream_callback(content)
            
            return full_text
        except Exception as e:
            return f"エラーが発生しました: {str(e)}"

    def check_connection(self):
        """
        接続確認を行う
        """
        try:
            self.client.models.list()
            return True, "接続成功"
        except Exception as e:
            return False, f"接続失敗: {str(e)}"

    def get_models(self):
        """
        利用可能なモデル一覧を取得する
        """
        try:
            models = self.client.models.list()
            return [m.id for m in models.data]
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []
