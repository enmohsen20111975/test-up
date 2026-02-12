import openai
import os
from config import settings

class DeepSeekClient:
    def __init__(self):
        self.client = openai.OpenAI(
            base_url=settings.DEEPSEEK_BASE_URL,
            api_key=settings.DEEPSEEK_API_KEY
        )
        self.model = "deepseek-chat"
    
    async def explain_calculation(self, calc_type: str, inputs: dict, results: dict):
        system_prompt = """أنت مهندس مصري خبير في الهندسة الكهربائية، الميكانيكية وال אז civil. 
        عليك شرح الحسابات الهندسية بتفاصيل، مرجعاً للقواعد المصرية والمعادلات المستخدمة.
        اكتب باللغة العربية الرسمية واشرح الخطوات خطوة بخطوة."""
        
        prompt = (f"شرح الحساب الكهربائي للـ {calc_type} مع المدخلات التالية: {inputs}. "
                 f"النتائج: {results}. مرجعاً للقواعد الهندسية المطبقة.")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"DeepSeek error: {e}")
            return None
    
    async def analyze_data(self, data_summary: str):
        system_prompt = """أنت تحليل بيانات مهندسي متخصص في البيانات الهندسية. 
        عليك تحليل الملفات وجد الأثراء والاتجاهات والاستثنائيات.
        اكتب باللغة العربية الرسمية وقدم توصيات عملية."""
        
        prompt = f"تحليل بيانات الهندسة التالية: {data_summary}. اضف توصيات عملية."
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"DeepSeek error: {e}")
            return None
    
    async def generate_report(self, calc_results: dict, analysis_data: str, template: str):
        system_prompt = """أنت مهندس مصري خبير يكتب تقارير هندسية احترافية باللغة العربية الرسمية.
        احتفظ بالتنسيق الرسمي واملأ جميع الحقول المطلوبة. استخدم التخطيطات المقدمة."""
        
        prompt = f"اكتب تقرير هندسي باستخدام النتائج: {calc_results} والتحليل: {analysis_data}."
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"DeepSeek error: {e}")
            return None
    
    async def chat(self, message: str, context: str = ""):
        system_prompt = """أنت مساعد مهندسي مصري حديث باللغة العامية المصرية. 
        أجب على الأسئلة بسرعة ووضوح. استخدم العبارات المحلية مثل "حاضر", "ماشي", "فهمت".
        إذا كان السؤال عن حساب هندسي، اشرح بالتفاصيل."""
        
        prompt = f"{context}\n{message}"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"DeepSeek error: {e}")
            return None