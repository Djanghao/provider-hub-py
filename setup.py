from setuptools import setup, find_packages

setup(
    name="provider_hub",
    version="0.5.0",
    description="Unified LLM provider interface for multi-agent systems",
    author="Djanghao",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "volcengine-python-sdk[ark]>=1.0.0",
        "python-dotenv>=0.19.0",
        "tenacity>=8.0.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)