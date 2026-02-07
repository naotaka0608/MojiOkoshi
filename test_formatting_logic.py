def test_formatting_logic():
    segments_with_speaker = [
        {"display_name": "Aさん", "text": "こんにちは。"},
        {"display_name": "Aさん", "text": "元気ですか？"},
        {"display_name": "Bさん", "text": "はい、元気です。"},
        {"display_name": "Bさん", "text": "あなたは？"},
        {"display_name": "Aさん", "text": "私も元気です。"}
    ]

    final_lines = []
    
    # Copy of the logic from transcriber.py
    current_speaker = None
    current_block_text = []
    
    for seg in segments_with_speaker:
        speaker = seg["display_name"]
        text = seg["text"].strip()
        
        if speaker != current_speaker:
            if current_block_text:
                block_content = "".join(current_block_text)
                
                block_content = block_content.replace("。", "。\n")
                block_content = block_content.replace("?", "?\n")
                block_content = block_content.replace("？", "？\n")
                
                final_lines.append(f"{current_speaker}:")
                final_lines.append(block_content)
                final_lines.append("") # Empty line
            
            current_speaker = speaker
            current_block_text = []
        
        current_block_text.append(text)
    
    if current_block_text:
        block_content = "".join(current_block_text)
        block_content = block_content.replace("。", "。\n")
        block_content = block_content.replace("?", "?\n")
        block_content = block_content.replace("？", "？\n")
        
        final_lines.append(f"{current_speaker}:")
        final_lines.append(block_content)

    print("\n--- FORMATTED OUTPUT START ---")
    print("\n".join(final_lines))
    print("--- FORMATTED OUTPUT END ---")

if __name__ == "__main__":
    test_formatting_logic()
