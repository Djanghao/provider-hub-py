
import asyncio
import sys
import json
import datetime
import time
import base64
sys.path.append('.')

from providers import ProviderHub
from models import Message, ChatRequest, Role, encode_image_to_base64

class TestLogger:
    def __init__(self):
        self.results = {
            "test_info": {
                "timestamp": datetime.datetime.now().isoformat(),
                "config_file": "config.yaml",
                "purpose": "Comprehensive Provider Hub test with cheapest models"
            },
            "tests": []
        }
        self.log_content = []
    
    def log_test(self, test_name, provider, model, success, response_time, 
                 request_details, response_details, error=None):
        test_result = {
            "test_name": test_name,
            "provider": provider,
            "model": model,
            "success": success,
            "response_time_seconds": response_time,
            "request_details": request_details,
            "response_details": response_details,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if error:
            test_result["error"] = str(error)
        
        self.results["tests"].append(test_result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name} - {provider} ({model}) - {response_time:.2f}s")
        if success and response_details.get("content"):
            print(f"   Response: {response_details['content'][:100]}...")
        elif error:
            print(f"   Error: {str(error)[:100]}...")
        
        self._log_detailed_result(test_name, provider, model, success, response_time, 
                                request_details, response_details, error)
    
    def _log_detailed_result(self, test_name, provider, model, success, response_time, 
                           request_details, response_details, error=None):
        self.log_content.append(f"\n{'='*60}")
        self.log_content.append(f"Test: {test_name}")
        self.log_content.append(f"Provider: {provider}")
        self.log_content.append(f"Model: {model}")
        self.log_content.append(f"Success: {'✅' if success else '❌'}")
        self.log_content.append(f"Response Time: {response_time:.2f}s")
        self.log_content.append(f"Timestamp: {datetime.datetime.now().isoformat()}")
        
        self.log_content.append(f"\n--- INPUT ---")
        if 'message' in request_details:
            self.log_content.append(f"Message: {request_details['message']}")
        if 'messages' in request_details:
            self.log_content.append(f"Messages Count: {request_details['messages']}")
        if 'max_tokens' in request_details:
            self.log_content.append(f"Max Tokens: {request_details['max_tokens']}")
        if 'image_size' in request_details:
            self.log_content.append(f"Image Size: {request_details['image_size']} bytes")
        if 'question' in request_details:
            self.log_content.append(f"Question: {request_details['question']}")
        if 'thinking_enabled' in request_details:
            self.log_content.append(f"Thinking Mode: {request_details['thinking_enabled']}")
        if 'math_problem' in request_details:
            self.log_content.append(f"Math Problem: {request_details['math_problem']}")
        if 'context_messages' in request_details:
            self.log_content.append(f"Context Messages: {request_details['context_messages']}")
        if 'topic' in request_details:
            self.log_content.append(f"Topic: {request_details['topic']}")
        
        self.log_content.append(f"\n--- OUTPUT ---")
        if success:
            if 'content' in response_details:
                self.log_content.append(f"Content: {response_details['content']}")
            if 'model' in response_details:
                self.log_content.append(f"Response Model: {response_details['model']}")
            if 'usage' in response_details and response_details['usage']:
                usage = response_details['usage']
                if isinstance(usage, dict):
                    self.log_content.append(f"Token Usage:")
                    if 'prompt_tokens' in usage:
                        self.log_content.append(f"  Prompt: {usage['prompt_tokens']} tokens")
                    if 'completion_tokens' in usage:
                        self.log_content.append(f"  Completion: {usage['completion_tokens']} tokens")
                    if 'total_tokens' in usage:
                        self.log_content.append(f"  Total: {usage['total_tokens']} tokens")
        else:
            self.log_content.append(f"Error: {error}")
        
        self.log_content.append("")
    
    def save_results(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Test results saved to: {filename}")
    
    def save_detailed_log(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Provider Hub Test Report\n")
            f.write(f"========================\n")
            f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Config: config.yaml\n")
            f.write(f"Purpose: Comprehensive Provider Hub test with cheapest models\n")
            f.write(f"\n")
            f.write('\n'.join(self.log_content))
        print(f"📄 Detailed test log saved to: {filename}")


async def test_basic_text_chat(hub, logger):
    print("\n💬 Testing Basic Text Chat")
    print("=" * 40)
    
    test_message = "Say 'Hello from AI!' in your native language and nothing more."
    
    for provider_name in hub.list_providers():
        start_time = time.time()
        try:
            response = hub.quick_chat(provider_name, test_message)
            response_time = time.time() - start_time
            
            provider = hub.get_provider(provider_name)
            model = provider.config.default_model
            
            logger.log_test(
                "Basic Text Chat",
                provider_name,
                model,
                True,
                response_time,
                {"message": test_message, "method": "quick_chat"},
                {"content": response, "length": len(response)}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_test(
                "Basic Text Chat",
                provider_name, 
                "unknown",
                False,
                response_time,
                {"message": test_message, "method": "quick_chat"},
                {},
                error=e
            )

async def test_async_chat(hub, logger):
    print("\n🔄 Testing Async Chat")
    print("=" * 40)
    
    messages = [
        Message.text(Role.SYSTEM, "You are a helpful assistant."),
        Message.text(Role.USER, "What is 2+2? Answer with just the number.")
    ]
    
    for provider_name in hub.list_providers():
        provider = hub.get_provider(provider_name)
        if not provider:
            continue
            
        start_time = time.time()
        try:
            request = ChatRequest(
                messages=messages,
                model=provider.config.default_model,
                max_tokens=50
            )
            
            response = await hub.achat(provider_name, request)
            response_time = time.time() - start_time
            
            logger.log_test(
                "Async Chat",
                provider_name,
                provider.config.default_model,
                True,
                response_time,
                {"messages": len(messages), "max_tokens": 50},
                {"content": response.content, "model": response.model}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_test(
                "Async Chat",
                provider_name,
                provider.config.default_model,
                False,
                response_time,
                {"messages": len(messages), "max_tokens": 50},
                {},
                error=e
            )

async def test_vision_capabilities(hub, logger):
    print("\n🖼️ Testing Vision Capabilities")
    print("=" * 40)
    
    image_path = "assets/meme.jpg"
    image_data = encode_image_to_base64(image_path)
    vision_providers = {
        "openai": "gpt-4o-mini",
        "qwen": "qwen-vl-plus",
        "doubao": "doubao-seed-1-6-vision-250815"
    }
    
    for provider_name, vision_model in vision_providers.items():
        if provider_name not in hub.list_providers():
            continue
            
        start_time = time.time()
        try:
            message = Message.with_image(
                Role.USER,
                "What do you see in this image?",
                image_data
            )
            
            request = ChatRequest(
                messages=[message],
                model=vision_model,
                max_tokens=100
            )
            
            response = await hub.achat(provider_name, request)
            response_time = time.time() - start_time
            
            logger.log_test(
                "Vision Analysis",
                provider_name,
                vision_model,
                True,
                response_time,
                {"image_size": len(image_data), "question": message.content[0].text},
                {"content": response.content, "usage": response.usage}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_test(
                "Vision Analysis",
                provider_name,
                vision_model,
                False,
                response_time,
                {"image_size": len(image_data)},
                {},
                error=e
            )

async def test_thinking_mode(hub, logger):
    print("\n🤔 Testing Thinking Mode")
    print("=" * 40)
    
    if "doubao" not in hub.list_providers():
        print("⚠️  Doubao provider not available")
        return
    
    start_time = time.time()
    try:
        request = ChatRequest(
            messages=[Message.text(Role.USER, "What is 15 × 23? Show your calculation.")],
            model="doubao-seed-1-6-thinking-250715",
            thinking={"type": "enabled"},
            max_tokens=300
        )
        
        response = await hub.achat("doubao", request)
        response_time = time.time() - start_time
        
        logger.log_test(
            "Thinking Mode",
            "doubao",
            "doubao-seed-1-6-thinking-250715",
            True,
            response_time,
            {"thinking_enabled": True, "math_problem": "15 × 23"},
            {"content": response.content, "usage": response.usage}
        )
        
    except Exception as e:
        response_time = time.time() - start_time
        logger.log_test(
            "Thinking Mode",
            "doubao",
            "doubao-seed-1-6-thinking-250715",
            False,
            response_time,
            {"thinking_enabled": True, "math_problem": "15 × 23"},
            {},
            error=e
        )

async def test_multi_turn_conversation(hub, logger):
    print("\n💭 Testing Multi-turn Conversation")
    print("=" * 40)
    
    for provider_name in hub.list_providers():
        print(f"\n🧪 Testing {provider_name} multi-turn...")
        provider = hub.get_provider(provider_name)
        if not provider:
            continue
            
        start_time = time.time()
        try:
            messages = [
                Message.text(Role.SYSTEM, "You are a helpful assistant."),
                Message.text(Role.USER, "What is Python?"),
                Message.text(Role.ASSISTANT, "Python is a programming language."),
                Message.text(Role.USER, "Is it popular? Just yes or no.")
            ]
            
            request = ChatRequest(
                messages=messages,
                model=provider.config.default_model,
                max_tokens=50
            )
            
            response = await hub.achat(provider_name, request)
            response_time = time.time() - start_time
            
            logger.log_test(
                "Multi-turn Conversation",
                provider_name,
                provider.config.default_model,
                True,
                response_time,
                {
                    "approach": "single_request_with_history",
                    "turns": 2,
                    "context_messages": len(messages),
                    "topic": "Python programming"
                },
                {"content": response.content, "length": len(response.content)}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_test(
                "Multi-turn Conversation",
                provider_name,
                provider.config.default_model,
                False,
                response_time,
                {"approach": "single_request_with_history", "turns": 2},
                {},
                error=e
            )

def analyze_results(logger):
    print("\n📊 Test Results Analysis")
    print("=" * 50)
    
    tests = logger.results["tests"]
    total_tests = len(tests)
    successful_tests = sum(1 for t in tests if t["success"])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    provider_stats = {}
    for test in tests:
        provider = test["provider"]
        if provider not in provider_stats:
            provider_stats[provider] = {"success": 0, "total": 0, "avg_time": 0}
        
        provider_stats[provider]["total"] += 1
        if test["success"]:
            provider_stats[provider]["success"] += 1
        provider_stats[provider]["avg_time"] += test["response_time_seconds"]
    
    print(f"\n📈 Provider Performance:")
    for provider, stats in provider_stats.items():
        success_rate = (stats["success"] / stats["total"]) * 100
        avg_time = stats["avg_time"] / stats["total"]
        print(f"   {provider}: {stats['success']}/{stats['total']} ({success_rate:.1f}%) - {avg_time:.2f}s avg")
    
    successful_tests_sorted = sorted([t for t in tests if t["success"]], 
                                   key=lambda x: x["response_time_seconds"])
    if successful_tests_sorted:
        fastest = successful_tests_sorted[0]
        print(f"\n⚡ Fastest Response: {fastest['provider']} - {fastest['response_time_seconds']:.2f}s")

async def main():
    print("🚀 Provider Hub - Connection Test")
    print("=" * 60)
    print("🎯 Purpose: Test all functionality with cheapest models")
    print("📋 Config: config.yaml")
    print("💰 Focus: Minimize API costs while testing all features")
    print("=" * 60)
    
    logger = TestLogger()
    
    try:
        hub = ProviderHub("config.yaml")
        providers = hub.list_providers()
        print(f"🔧 Initialized providers: {providers}")
        
        print(f"\n📱 Model Configuration (Cheapest Models):")
        for provider_name in providers:
            provider = hub.get_provider(provider_name)
            print(f"   {provider_name}: {provider.config.default_model}")
        
    except Exception as e:
        print(f"❌ Failed to initialize hub: {e}")
        return
    
    start_time = datetime.datetime.now()
    
    await test_basic_text_chat(hub, logger)
    await test_async_chat(hub, logger)
    await test_vision_capabilities(hub, logger)
    await test_thinking_mode(hub, logger)
    await test_multi_turn_conversation(hub, logger)
    
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    
    logger.results["summary"] = {
        "total_duration_seconds": duration.total_seconds(),
        "total_tests": len(logger.results["tests"]),
        "successful_tests": sum(1 for t in logger.results["tests"] if t["success"]),
        "providers_tested": list(set(t["provider"] for t in logger.results["tests"]))
    }
    
    analyze_results(logger)
    
    logger.save_detailed_log("test_report.log")
    
    print(f"\n🎉 Testing completed in {duration.total_seconds():.1f} seconds")

if __name__ == "__main__":
    asyncio.run(main())