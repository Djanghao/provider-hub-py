from .core import LLM, LLMConfig, ChatMessage, ChatResponse
from .utils import EnvManager, encode_image_to_base64, prepare_image_content
from . import exceptions

__version__ = "0.1.0"

def test_connection():
    """Quick connection test for representative models from each provider"""
    try:
        # Test one model from each provider
        models_to_test = [
            "doubao-seed-1-6-250615",  # Doubao
            "qwen-flash",              # Qwen
            "deepseek-chat",           # DeepSeek  
            "gpt-4.1"                  # OpenAI
        ]
        success_count = 0
        
        print("🔍 Testing Provider Hub connections...")
        print("Testing representative models from each provider...")
        
        for model in models_to_test:
            try:
                llm = LLM(model=model, max_tokens=20, timeout=10)
                response = llm.chat("Hi")
                print(f"✅ {model}: {response.content[:50]}...")
                success_count += 1
            except Exception as e:
                print(f"❌ {model}: {str(e)[:50]}...")
        
        print(f"\n🎉 {success_count}/{len(models_to_test)} providers working")
        print("💡 For comprehensive testing of all 17 models, run: python test_connection.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

__all__ = ["LLM", "LLMConfig", "ChatMessage", "ChatResponse", "EnvManager", "encode_image_to_base64", "prepare_image_content", "exceptions", "test_connection"]