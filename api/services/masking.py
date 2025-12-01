import hashlib
import uuid
from typing import List, Dict, Any
from api.services.detection import pii_detector
from api.services.vault import vault_service
from api.models.request import MaskRequest, UnmaskRequest
from api.models.response import MaskResponse, PIIEntity, UnmaskResponse

from api.services.audit import audit_service

class MaskingService:
    def mask(self, request: MaskRequest) -> MaskResponse:
        # 1. Detect PII
        detected_entities, detection_metadata = pii_detector.detect(request.text)
        
        # 2. Generate Tokens and Mask
        masked_text = request.text
        entities_result = []
        
        # Sort entities by start index in reverse order to replace without messing up indices
        detected_entities.sort(key=lambda x: x['start'], reverse=True)
        
        pii_types_found = []
        
        for entity in detected_entities:
            original_text = entity['text']
            pii_type = entity['type']
            pii_types_found.append(pii_type)
            
            # Generate deterministic token for this session + value
            token_id = self._generate_token_id(request.session_id, pii_type, original_text)
            token = f"[{pii_type}_{token_id}]"
            
            # Store in Vault
            vault_data = {
                "original_value": original_text,
                "pii_type": pii_type,
                "source": entity.get('source', 'Unknown'),
                "context": request.context,
                "created_at": "now" # TODO: use real timestamp
            }
            vault_service.store_token(request.session_id, token_id, vault_data)
            
            # Replace in text
            start = entity['start']
            end = entity['end']
            masked_text = masked_text[:start] + token + masked_text[end:]
            
            entities_result.append(PIIEntity(
                type=pii_type,
                text=original_text,
                start=start,
                end=end,
                score=entity['score'],
                token=token
            ))
            
        # 3. Calculate Risk Score
        risk_score = min(len(detected_entities) * 1.5, 10.0)
        
        # 4. Audit Log
        context = request.context or {}
        audit_service.log_event(
            operation="MASK",
            session_id=request.session_id,
            user_id=context.get('user_id'),
            user_role=context.get('user_role'),
            pii_types=list(set(pii_types_found)),
            purpose=context.get('purpose'),
            success=True,
            metadata={
                "risk_score": risk_score, 
                "entities_count": len(entities_result),
                **detection_metadata
            }
        )
        
        return MaskResponse(
            success=True,
            masked_text=masked_text,
            entities=entities_result,
            session_id=request.session_id,
            risk_score=risk_score,
            metadata=detection_metadata
        )

    def _generate_token_id(self, session_id: str, pii_type: str, value: str) -> str:
        """Generate a short hash for the token."""
        data = f"{session_id}:{pii_type}:{value}"
        return hashlib.sha256(data.encode()).hexdigest()[:8]

    def unmask(self, request: UnmaskRequest) -> UnmaskResponse:
        unmasked_text = request.text
        entities_unmasked = []
        pii_types_unmasked = []
        
        # Simple regex to find tokens: [TYPE_ID]
        import re
        token_pattern = r"\[([A-Z_]+)_([a-f0-9]{8})\]"
        
        matches = list(re.finditer(token_pattern, unmasked_text))
        
        for match in reversed(matches):
            full_token = match.group(0)
            pii_type = match.group(1)
            token_id = match.group(2)
            
            # Check Access Control
            if not self._check_access(request.context, pii_type):
                continue
            
            # Retrieve from Vault
            vault_data = vault_service.get_token(request.session_id, token_id)
            
            if vault_data:
                original_value = vault_data.get("original_value")
                if original_value:
                    start = match.start()
                    end = match.end()
                    unmasked_text = unmasked_text[:start] + original_value + unmasked_text[end:]
                    
                    entities_unmasked.append({
                        "type": pii_type,
                        "token": full_token,
                        "original_text": original_value
                    })
                    pii_types_unmasked.append(pii_type)
        
        # Audit Log
        context = request.context or {}
        audit_id = audit_service.log_event(
            operation="UNMASK",
            session_id=request.session_id,
            user_id=context.get('user_id'),
            user_role=context.get('user_role'),
            pii_types=list(set(pii_types_unmasked)),
            purpose=context.get('purpose'),
            reason=context.get('reason'),
            success=True,
            metadata={"entities_count": len(entities_unmasked)}
        )
        
        return UnmaskResponse(
            success=True,
            unmasked_text=unmasked_text,
            entities_unmasked=entities_unmasked,
            audit_id=audit_id
        )

    def _check_access(self, context: Dict, pii_type: str) -> bool:
        """
        Simple access control check.
        """
        if context is None:
            context = {}
            
        user_role = context.get('user_role', 'guest')
        
        # Admin can unmask everything
        if user_role == 'admin':
            return True
            
        # Customer service can unmask everything except SSN/CC
        if user_role == 'customer_service':
            if pii_type in ['US_SSN', 'CREDIT_CARD', 'SSN']:
                return False
            return True
            
        return False

masking_service = MaskingService()

