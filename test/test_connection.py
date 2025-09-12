#!/usr/bin/env python3

import sys
import os
sys.path.append('..')

from provider_hub import LLM, ChatMessage, prepare_image_content
import json
import datetime

test_results = {
    "timestamp": datetime.datetime.now().isoformat(),
    "text_models": [],
    "vision_models": [],
    "thinking_models": [],
    "summary": {}
}

def test_all_text_models():
    print("=== Testing All Text Models ===\n")
    
    all_models = [
        {"model": "gpt-5", "provider": "OpenAI", "type": "chat"},
        {"model": "gpt-5-mini", "provider": "OpenAI", "type": "chat"},
        {"model": "gpt-5-nano", "provider": "OpenAI", "type": "chat"},
        {"model": "gpt-4.1", "provider": "OpenAI", "type": "chat"},
        {"model": "deepseek-chat", "provider": "DeepSeek", "type": "chat"},
        {"model": "deepseek-reasoner", "provider": "DeepSeek", "type": "reasoning"},
        {"model": "qwen3-max-preview", "provider": "Qwen", "type": "chat"},
        {"model": "qwen-plus", "provider": "Qwen", "type": "chat"},
        {"model": "qwen-flash", "provider": "Qwen", "type": "chat"},
        {"model": "qwen3-coder-plus", "provider": "Qwen", "type": "coding"},
        {"model": "qwen3-coder-flash", "provider": "Qwen", "type": "coding"},
        {"model": "doubao-seed-1-6-250615", "provider": "Doubao", "type": "chat"},
        {"model": "doubao-seed-1-6-flash-250828", "provider": "Doubao", "type": "chat"},
    ]
    
    for model_info in all_models:
        result = {
            "model": model_info['model'],
            "provider": model_info['provider'],
            "type": model_info['type'],
            "status": "failed",
            "tokens": 0,
            "response_preview": "",
            "error": ""
        }
        
        try:
            print(f"Testing {model_info['provider']} {model_info['model']} ({model_info['type']})...")
            
            llm = LLM(
                model=model_info['model'],
                temperature=0.7,
                max_tokens=50,
                timeout=15
            )
            
            if model_info['type'] == 'coding':
                prompt = "Write a simple hello world in Python"
            elif model_info['type'] == 'reasoning':
                prompt = "What is 2+3? Think step by step."
            else:
                prompt = "Hello, respond in one sentence"
            
            response = llm.chat(prompt)
            result["status"] = "success"
            result["response_preview"] = response.content[:100]
            if response.usage:
                result["tokens"] = response.usage.get('total_tokens', 0)
            
            print(f"✅ Success: {response.content[:100]}...")
            if response.usage:
                tokens = response.usage.get('total_tokens', 'N/A')
                print(f"📊 Tokens: {tokens}")
            print()
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Failed: {e}")
            print()
        
        test_results["text_models"].append(result)

def test_all_vision_models():
    print("=== Testing All Vision Models ===\n")
    
    vision_models = [
        {"model": "gpt-4.1", "provider": "OpenAI"},
        {"model": "qwen-vl-max", "provider": "Qwen"},
        {"model": "qwen-vl-plus", "provider": "Qwen"},
        {"model": "doubao-seed-1-6-vision-250815", "provider": "Doubao"},
    ]
    
    image_path = "../assets/meme.jpg"
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        print("Skipping vision model tests\n")
        return
    
    for model_info in vision_models:
        result = {
            "model": model_info['model'],
            "provider": model_info['provider'],
            "status": "failed",
            "tokens": 0,
            "response_preview": "",
            "error": ""
        }
        
        try:
            print(f"Testing {model_info['provider']} {model_info['model']} (vision)...")
            
            llm = LLM(
                model=model_info['model'],
                temperature=0.7,
                max_tokens=80,
                timeout=20
            )
            
            image_content = prepare_image_content(image_path)
            messages = [ChatMessage(
                role="user",
                content=[
                    {"type": "text", "text": "Describe this image briefly"},
                    image_content
                ]
            )]
            
            response = llm.chat(messages)
            result["status"] = "success"
            result["response_preview"] = response.content[:100]
            if response.usage:
                result["tokens"] = response.usage.get('total_tokens', 0)
            
            print(f"✅ Success: {response.content[:100]}...")
            if response.usage:
                tokens = response.usage.get('total_tokens', 'N/A')
                print(f"📊 Tokens: {tokens}")
            print()
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Failed: {e}")
            print()
        
        test_results["vision_models"].append(result)

def test_thinking_modes():
    print("=== Testing Thinking Modes ===\n")
    
    thinking_models = [
        {"model": "deepseek-reasoner", "provider": "DeepSeek", "thinking": True},
        {"model": "qwen3-max-preview", "provider": "Qwen", "thinking": True},
        {"model": "doubao-seed-1-6-250615", "provider": "Doubao", "thinking": {"type": "enabled"}},
    ]
    
    for model_info in thinking_models:
        result = {
            "model": model_info['model'],
            "provider": model_info['provider'],
            "thinking_mode": model_info['thinking'],
            "status": "failed",
            "tokens": 0,
            "response_preview": "",
            "error": ""
        }
        
        try:
            print(f"Testing {model_info['provider']} {model_info['model']} (thinking mode)...")
            
            llm = LLM(
                model=model_info['model'],
                thinking=model_info['thinking'],
                max_tokens=100,
                timeout=25
            )
            
            response = llm.chat("Calculate 12 * 15 step by step")
            result["status"] = "success"
            result["response_preview"] = response.content[:100]
            if response.usage:
                result["tokens"] = response.usage.get('total_tokens', 0)
            
            print(f"✅ Success: {response.content[:100]}...")
            if response.usage:
                tokens = response.usage.get('total_tokens', 'N/A')
                print(f"📊 Tokens: {tokens}")
            print()
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Failed: {e}")
            print()
        
        test_results["thinking_models"].append(result)

def generate_report():
    total_text = len(test_results["text_models"])
    success_text = len([r for r in test_results["text_models"] if r["status"] == "success"])
    
    total_vision = len(test_results["vision_models"])
    success_vision = len([r for r in test_results["vision_models"] if r["status"] == "success"])
    
    total_thinking = len(test_results["thinking_models"])
    success_thinking = len([r for r in test_results["thinking_models"] if r["status"] == "success"])
    
    test_results["summary"] = {
        "text_models": {"total": total_text, "success": success_text, "success_rate": success_text/total_text if total_text > 0 else 0},
        "vision_models": {"total": total_vision, "success": success_vision, "success_rate": success_vision/total_vision if total_vision > 0 else 0},
        "thinking_models": {"total": total_thinking, "success": success_thinking, "success_rate": success_thinking/total_thinking if total_thinking > 0 else 0},
        "overall": {"total": total_text + total_vision + total_thinking, "success": success_text + success_vision + success_thinking}
    }
    
    with open("test_report.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    with open("test_report.md", "w") as f:
        f.write("# Provider Hub Test Report\n\n")
        f.write(f"**Test Date**: {test_results['timestamp']}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Text Models**: {success_text}/{total_text} ({success_text/total_text*100:.1f}%)\n")
        f.write(f"- **Vision Models**: {success_vision}/{total_vision} ({success_vision/total_vision*100:.1f}%)\n") 
        f.write(f"- **Thinking Models**: {success_thinking}/{total_thinking} ({success_thinking/total_thinking*100:.1f}%)\n")
        f.write(f"- **Overall Success**: {test_results['summary']['overall']['success']}/{test_results['summary']['overall']['total']} ({test_results['summary']['overall']['success']/test_results['summary']['overall']['total']*100:.1f}%)\n\n")
        
        f.write("## Detailed Results\n\n")
        
        f.write("### Text Models\n")
        for result in test_results["text_models"]:
            status = "✅" if result["status"] == "success" else "❌"
            f.write(f"- {status} **{result['provider']} {result['model']}** ({result['type']})\n")
            if result["status"] == "success":
                f.write(f"  - Tokens: {result['tokens']}\n")
                f.write(f"  - Response: {result['response_preview']}...\n")
            else:
                f.write(f"  - Error: {result['error']}\n")
        f.write("\n")
        
        f.write("### Vision Models\n")
        for result in test_results["vision_models"]:
            status = "✅" if result["status"] == "success" else "❌"
            f.write(f"- {status} **{result['provider']} {result['model']}**\n")
            if result["status"] == "success":
                f.write(f"  - Tokens: {result['tokens']}\n")
                f.write(f"  - Response: {result['response_preview']}...\n")
            else:
                f.write(f"  - Error: {result['error']}\n")
        f.write("\n")
        
        f.write("### Thinking Models\n")
        for result in test_results["thinking_models"]:
            status = "✅" if result["status"] == "success" else "❌"
            f.write(f"- {status} **{result['provider']} {result['model']}**\n")
            if result["status"] == "success":
                f.write(f"  - Tokens: {result['tokens']}\n")
                f.write(f"  - Response: {result['response_preview']}...\n")
            else:
                f.write(f"  - Error: {result['error']}\n")
    
    print("📄 Reports generated:")
    print("  - test_report.json")
    print("  - test_report.md")

def main():
    print("🔥 Provider Hub - Complete Model Testing")
    print("=" * 50)
    print()
    
    if not os.path.exists("../.env"):
        print("❌ .env file not found")
        return
    
    test_all_text_models()
    test_all_vision_models()
    test_thinking_modes()
    
    generate_report()
    
    print("\n🎉 Testing completed with reports generated!")

if __name__ == "__main__":
    main()