
import re
import math
import collections

class SimpleSummarizer:
    def __init__(self):
        pass

    def _get_ngrams(self, text, n=2):
        """文字N-gramを生成する"""
        if not text:
            return []
        # 空白を除去して文字単位で処理
        text = text.replace(" ", "").replace("　", "")
        return [text[i:i+n] for i in range(len(text) - n + 1)]

    def _calculate_similarity(self, sent1, sent2):
        """
        2つの文の類似度を計算する。
        包含率（Containment）を使用する。
        短い文が長い文にどれだけ含まれているかを見ることで、重複を検出する。
        """
        if not sent1 or not sent2:
            return 0.0
            
        # 平仮名を除去する正規表現
        def extract_content_words(text):
            return re.sub(r'[ぁ-ん、。]', '', text)
            
        content1 = extract_content_words(sent1)
        content2 = extract_content_words(sent2)
        
        if len(content1) < 2: content1 = sent1
        if len(content2) < 2: content2 = sent2
        
        set1 = set(content1)
        set2 = set(content2)
        
        intersection = len(set1.intersection(set2))
        min_len = min(len(set1), len(set2))
        
        if min_len == 0:
            return 0.0
            
        return intersection / min_len



    def _preprocess(self, text):
        """
        前処理を行う
        1. 短すぎる文やフィラーを除去
        2. 意味のある単位で文を整形
        """
        # 単純な行分割
        raw_lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        cleaned_sentences = []
        blacklist = ["はい", "ええ", "あの", "その", "まあ", "ですね", "よろしくお願いします", "お疲れ様です", "ありがとうございます", "そうですね"]
        
        for line in raw_lines:
            # 1. フィラー除去 (完全一致)
            if line in blacklist:
                continue
            
            # 2. 短すぎる文の除去 (例えば10文字以下で、かつ「重要」などのキーワードを含まない場合)
            if len(line) < 10 and not any(k in line for k in ["重要", "結論", "ポイント", "つまり"]):
                continue

            cleaned_sentences.append(line)
            
        # 重複削除 (順序維持)
        seen = set()
        unique_sentences = []
        for s in cleaned_sentences:
            if s not in seen:
                unique_sentences.append(s)
                seen.add(s)
                
        return unique_sentences

    def summarize(self, text, ratio=0.3, max_sentences=5, damping=0.85, iterations=30):
        """
        TextRankアルゴリズム + MMR (Maximal Marginal Relevance) による抽出要約
        """
        if not text:
            return ""

        # 1. 前処理と文分割
        sentences = self._preprocess(text)
        n_sentences = len(sentences)
        
        if n_sentences == 0:
            return ""
        
        # 文が少なければそのまま返す
        if n_sentences <= max_sentences:
            return "\n".join(sentences)

        # 2. TextRankによる重要度計算
        similarity_matrix = [[0.0] * n_sentences for _ in range(n_sentences)]
        
        for i in range(n_sentences):
            for j in range(i + 1, n_sentences):
                sim = self._calculate_similarity(sentences[i], sentences[j])
                # 閾値を設定してノイズエッジを減らす
                if sim > 0.2:
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim

        scores = [1.0] * n_sentences
        
        for _ in range(iterations):
            new_scores = [0.0] * n_sentences
            for i in range(n_sentences):
                incoming_score = 0.0
                for j in range(n_sentences):
                    if i == j: continue
                    sum_out_weight = sum(similarity_matrix[j])
                    if sum_out_weight > 0:
                        incoming_score += (scores[j] * similarity_matrix[j][i]) / sum_out_weight
                new_scores[i] = (1 - damping) + damping * incoming_score
            scores = new_scores

        # 3. MMRによる冗長性の排除と抽出
        # MMR score = lambda * Importance - (1 - lambda) * Similarity_to_selected
        
        selected_indices = []
        candidate_indices = list(range(n_sentences))
        
        target_count = min(max_sentences, max(1, int(n_sentences * ratio)))
        mmr_lambda = 0.4 # 重複排除を重視 (0.4)
        
        while len(selected_indices) < target_count and candidate_indices:
            best_mmr_score = -float('inf')
            best_idx = -1
            
            for idx in candidate_indices:
                # Importance part (Normalized TextRank score)
                importance = scores[idx]
                
                # Redundancy part
                max_similarity = 0.0
                if selected_indices:
                    max_similarity = max([similarity_matrix[idx][sel_idx] for sel_idx in selected_indices])
                
                mmr_score = mmr_lambda * importance - (1 - mmr_lambda) * max_similarity
                
                # print(f"Idx: {idx}, Imp: {importance:.4f}, Sim: {max_similarity:.4f}, Score: {mmr_score:.4f} Content: {sentences[idx]}")
                
                if mmr_score > best_mmr_score:
                    best_mmr_score = mmr_score
                    best_idx = idx
            
            if best_idx != -1:
                # print(f"Selected: {best_idx} -> {sentences[best_idx]}")
                selected_indices.append(best_idx)
                candidate_indices.remove(best_idx)
            else:
                break
        
        # 元の順序に戻して結合
        selected_indices.sort()
        summary_sentences = [sentences[i] for i in selected_indices]
        
        return "\n".join(summary_sentences)


if __name__ == "__main__":
    # Test
    sample_text = """
    今日はMojiOkoshiプロジェクトの進捗報告会を行います。
    まず、新しいUIデザインについて議論します。
    UIはユーザー体験に直結する重要な要素です。
    次に、音声認識エンジンの精度向上について話し合います。
    精度が低いと修正の手間が増えるため、改善が必要です。
    また、要約機能の実装についても検討します。
    要約機能があれば、長い会議の内容をすぐに把握できます。
    最後に、今後のスケジュールを確認します。
    来週までにプロトタイプを完成させる予定です。
    """
    summarizer = SimpleSummarizer()
    print("--- Original ---")
    print(sample_text)
    print("\n--- Summary ---")
    print(summarizer.summarize(sample_text))
