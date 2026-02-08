
import google.generativeai as genai
import os

class GeminiSummarizer:
    def __init__(self, api_key, model="gemini-pro"):
        self.api_key = api_key
        self.model_name = model
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    def summarize(self, text, prompt_prefix="以下の文章を要点ごとに箇条書きで要約してください:\n\n"):
        """
        Gemini APIを使って要約を生成する
        """
        if not self.api_key:
            return "APIキーが設定されていません。"
        
        if not text:
            return "テキストが空です。"

        try:
            response = self.model.generate_content(f"{prompt_prefix}{text}")
            return response.text
        except Exception as e:
            return f"エラーが発生しました: {str(e)}"

    def update_api_key(self, api_key):
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
