import spacy
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from typing import List, Dict, Any, Optional
import logging
import requests
from api.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PIIDetector:
    """
    3-Phase PII Detection System:
    Phase 1: BERT Integration (Hugging Face API)
    Phase 2: Custom Recognizers (Global + India)
    Phase 3: Pipeline Optimization (Thresholds & Overlaps)
    """
    
    def __init__(self):
        # Initialize Presidio
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        
        # Use small spaCy model for Presidio's internal NLP
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        
        nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        self.anonymizer = AnonymizerEngine()
        
        # Load spaCy for local fallback/preprocessing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Phase 2: Configure Recognizers
        self._configure_recognizers()
        
        # Phase 1: BERT Configuration
        self.hf_api_key = settings.HUGGINGFACE_API_KEY
        self.hf_api_url = settings.HUGGINGFACE_API_URL or "https://api-inference.huggingface.co/models/dslim/bert-base-NER"
        self.use_bert = bool(self.hf_api_key)
        
        if self.use_bert:
            logger.info("✅ Phase 1: BERT Integration Enabled")
        else:
            logger.warning("⚠️ Phase 1: BERT Integration Disabled (No API Key)")

    def _configure_recognizers(self):
        """
        Phase 2: Configure Global and Indian Recognizers
        """
        # 1. Disable all default recognizers first to have clean slate? 
        # Presidio loads defaults. We will add specific ones.
        
        # Import Indian Recognizers (Available in Presidio 2.2.358+)
        try:
            from presidio_analyzer.predefined_recognizers import (
                InPanRecognizer, InAadhaarRecognizer, InPassportRecognizer,
                InVehicleRegistrationRecognizer, InVoterRecognizer, InGstinRecognizer
            )
            
            indian_recognizers = [
                InPanRecognizer(), InAadhaarRecognizer(), InPassportRecognizer(),
                InVehicleRegistrationRecognizer(), InVoterRecognizer(), InGstinRecognizer()
            ]
            
            for recognizer in indian_recognizers:
                self.analyzer.registry.add_recognizer(recognizer)
                
            logger.info(f"✅ Phase 2: Loaded {len(indian_recognizers)} Indian Recognizers")
            
        except ImportError:
            logger.error("❌ Phase 2: Failed to import Indian recognizers. Ensure presidio-analyzer>=2.2.358")

        # Global Recognizers are loaded by default in Presidio.
        # We ensure specific ones are present by checking or re-adding if needed.
        # For this implementation, we rely on Presidio's defaults for:
        # CREDIT_CARD, CRYPTO, DATE_TIME, EMAIL_ADDRESS, IBAN_CODE, IP_ADDRESS, 
        # LOCATION, PERSON, PHONE_NUMBER, MEDICAL_LICENSE, URL
        
        # Add Custom Fallback Recognizers (Regex)
        self._add_regex_fallbacks()

    def _add_regex_fallbacks(self):
        """Regex fallbacks for specific formats"""
        from presidio_analyzer import Pattern
        
        # International Phone (E.164)
        intl_phone = PatternRecognizer(
            supported_entity="PHONE_NUMBER",
            name="intl_phone_fallback",
            patterns=[
                Pattern("intl_phone", r"\+\d{1,4}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}", 0.6)
            ]
        )
        self.analyzer.registry.add_recognizer(intl_phone)

    def detect(self, text: str, language: str = 'en', confidence_threshold: float = 0.4) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Execute the 3-Phase Detection Pipeline
        Returns: (entities, metadata)
        """
        all_results = []
        bert_entity_ids = set()  # Track which entities came from BERT
        
        # --- Phase 1: BERT Integration ---
        bert_count = 0
        if self.use_bert:
            bert_results = self._detect_with_bert(text)
            bert_count = len(bert_results)
            # Mark BERT entities
            for res in bert_results:
                bert_entity_ids.add(f"{res.start}-{res.end}")
            all_results.extend(bert_results)
            
        # --- Phase 2: Presidio (Global + India) ---
        # We run Presidio to catch structured PII (IDs, Phones, Emails)
        presidio_results = self.analyzer.analyze(
            text=text,
            language=language,
            score_threshold=confidence_threshold
        )
        presidio_count = len(presidio_results)
        all_results.extend(presidio_results)
        
        # --- Phase 3: Pipeline Optimization ---
        # Handle overlaps and filter
        final_results = self._optimize_results(all_results, text)
        
        # Convert to response format and mark BERT entities
        entities = []
        for res in final_results:
            entity_id = f"{res.start}-{res.end}"
            entities.append({
                "type": res.entity_type,
                "start": res.start,
                "end": res.end,
                "score": res.score,
                "text": text[res.start:res.end],
                "source": "BERT" if entity_id in bert_entity_ids else "Presidio"
            })
        
        # Build metadata
        metadata = {
            "bert_enabled": self.use_bert,
            "bert_entities_found": bert_count,
            "presidio_entities_found": presidio_count,
            "total_before_optimization": len(all_results),
            "final_entity_count": len(entities)
        }
        
        return entities, metadata

    def _detect_with_bert(self, text: str) -> List[RecognizerResult]:
        """Call Hugging Face API for NER"""
        if not text: return []
        
        try:
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            response = requests.post(
                self.hf_api_url,
                headers=headers,
                json={"inputs": text},
                timeout=3.0 # Fast timeout to not block
            )
            
            if response.status_code != 200:
                logger.warning(f"BERT API Error: {response.status_code}")
                return []
                
            data = response.json()
            # Handle loading state
            if isinstance(data, dict) and 'error' in data:
                return []
                
            results = []
            # Mapping Deberta entities to Presidio types
            entity_map = {
                "PER": "PERSON", "LOC": "LOCATION", "ORG": "ORGANIZATION",
                "EMAIL": "EMAIL_ADDRESS", "PHONE": "PHONE_NUMBER",
                "DATE": "DATE_TIME", "TIME": "DATE_TIME",
                "MISC": "NRP"
            }
            
            for item in data:
                # Handle both aggregated and raw token responses
                label = item.get('entity_group') or item.get('entity')
                if not label: continue
                
                # Strip B- or I- prefix if present
                clean_label = label.replace('B-', '').replace('I-', '')
                
                presidio_type = entity_map.get(clean_label, "NRP")
                
                score = item.get('score', 0.0)
                start = item.get('start', 0)
                end = item.get('end', 0)
                
                results.append(RecognizerResult(
                    entity_type=presidio_type,
                    start=start,
                    end=end,
                    score=score
                ))
                
            return results
            
        except Exception as e:
            logger.error(f"BERT Detection Failed: {e}")
            return []

    def _optimize_results(self, results: List[RecognizerResult], text: str) -> List[RecognizerResult]:
        """
        Phase 3: Optimization
        - Deduplicate
        - Resolve overlaps (prefer higher score or longer match)
        """
        if not results: return []
        
        # Sort by start position
        results.sort(key=lambda x: x.start)
        
        merged = []
        if not results: return []
        
        curr = results[0]
        
        for next_res in results[1:]:
            # Check overlap
            if next_res.start < curr.end:
                # Overlap detected. Resolve.
                
                # 1. Prefer Presidio structured types over generic BERT types
                # e.g. IN_PAN (Presidio) > ORG (BERT)
                structured_types = {'IN_PAN', 'IN_AADHAAR', 'PHONE_NUMBER', 'EMAIL_ADDRESS', 'CREDIT_CARD'}
                curr_is_structured = curr.entity_type in structured_types
                next_is_structured = next_res.entity_type in structured_types
                
                if curr_is_structured and not next_is_structured:
                    continue # Keep curr
                elif next_is_structured and not curr_is_structured:
                    curr = next_res # Take next
                    continue
                
                # 2. Prefer Higher Score
                if next_res.score > curr.score:
                    curr = next_res
                # 3. If scores similar, prefer longer text
                elif next_res.score == curr.score:
                    if (next_res.end - next_res.start) > (curr.end - curr.start):
                        curr = next_res
            else:
                merged.append(curr)
                curr = next_res
                
        merged.append(curr)
        return merged

    def anonymize(self, text: str) -> str:
        """Pass-through to Presidio Anonymizer"""
        results = self.detect(text)
        # Convert dict results back to RecognizerResult for Anonymizer
        # Wait, detect returns dicts now. Anonymizer needs RecognizerResult or EngineResult.
        # Let's fix detect to return objects internally or handle this.
        # Actually, AnonymizerEngine.anonymize expects AnalyzerEngine results.
        
        # Re-construct RecognizerResults
        analyzer_results = [
            RecognizerResult(
                entity_type=r['type'],
                start=r['start'],
                end=r['end'],
                score=r['score']
            ) for r in results
        ]
        
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results
        )
        return anonymized.text

pii_detector = PIIDetector()
