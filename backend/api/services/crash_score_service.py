"""
Crash Score Calculation Service

Calculates a crash/damage score based on painted (boyali), locally painted (lokal_boyali),
and changed (degisen) parts. Score starts at 100 (pristine condition) and deducts points
based on the condition of each part.
"""
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
from loguru import logger

Language = Literal["en", "tr"]


@dataclass
class PartConditionConfig:
    """Configuration for a single part condition (changed/painted/local_painted)"""
    deduction: int
    advice_tr: str
    advice_en: str

    def get_advice(self, lang: Language = "en") -> str:
        return self.advice_tr if lang == "tr" else self.advice_en


@dataclass
class PartConfig:
    """Configuration for a car part with all possible conditions"""
    name: str
    changed: PartConditionConfig
    painted: PartConditionConfig
    local_painted: PartConditionConfig
    note: Optional[str] = None


# Parts configuration with Turkish names for matching
PARTS_CONFIG: Dict[str, PartConfig] = {
    # Roof - Tavan
    "roof": PartConfig(
        name="Tavan",
        changed=PartConditionConfig(
            deduction=60,
            advice_tr="Kritik yapisal risk. Takla veya agir kaza ihtimali yuksek. Satin alinmasi kesinlikle onerilmez.",
            advice_en="Critical structural risk. High probability of rollover or severe accident. Purchase strongly not recommended."
        ),
        painted=PartConditionConfig(
            deduction=30,
            advice_tr="Yuksek risk. Takla veya agir cisim darbesi olabilir. Macun kalinligi ve ic direk hasarini kontrol edin.",
            advice_en="High risk. Could indicate rollover or heavy object impact. Check filler thickness and inner pillar damage."
        ),
        local_painted=PartConditionConfig(
            deduction=15,
            advice_tr="Supheli. Kozmetik (kus piskligi vb.) veya anten onarimi olabilir, ancak dikkatli inceleme gerektirir.",
            advice_en="Suspicious. Could be cosmetic (bird droppings etc.) or antenna repair, but requires careful inspection."
        )
    ),
    # Hood - Motor Kaputu
    "hood": PartConfig(
        name="Motor Kaputu",
        changed=PartConditionConfig(
            deduction=35,
            advice_tr="Buyuk on carpisma ihtimali yuksek. Sasi, podya ve havayastiklarini dikkatle kontrol edin. Kaza fotograflari dogrulanmadikca onerilmez.",
            advice_en="High probability of major front collision. Carefully check chassis, subframe, and airbags. Not recommended unless accident photos verified."
        ),
        painted=PartConditionConfig(
            deduction=15,
            advice_tr="Muhtemelen on darbe veya tas cizigidir. On panel ve radyator destek sacinda orijinal etiketleri kontrol edin.",
            advice_en="Probably front impact or stone chip. Check front panel and radiator support for original labels."
        ),
        local_painted=PartConditionConfig(
            deduction=8,
            advice_tr="Kucuk kozmetik rotuş. Genellikle kabul edilebilir, renk uyumunu kontrol edin.",
            advice_en="Small cosmetic touch-up. Generally acceptable, check color match."
        )
    ),
    # Trunk Lid - Bagaj Kapagi
    "trunk_lid": PartConfig(
        name="Bagaj Kapagi",
        changed=PartConditionConfig(
            deduction=20,
            advice_tr="Onemli arkadan carpismayi gosterir. Bagaj havuzu ve arka sasi panelinde kaynak izlerini kontrol edin.",
            advice_en="Indicates significant rear collision. Check trunk floor and rear chassis panel for weld marks."
        ),
        painted=PartConditionConfig(
            deduction=10,
            advice_tr="Orta seviye arka darbe. Ic yapi saglam ise genellikle kabul edilebilir.",
            advice_en="Medium level rear impact. Generally acceptable if inner structure is intact."
        ),
        local_painted=PartConditionConfig(
            deduction=5,
            advice_tr="Kucuk kozmetik onarim. Arac degerine etkisi dusuk.",
            advice_en="Small cosmetic repair. Low impact on vehicle value."
        )
    ),
    # Rear Fender - Arka Camurluk
    "rear_fender": PartConfig(
        name="Arka Camurluk",
        note="Sol/Sag",
        changed=PartConditionConfig(
            deduction=20,
            advice_tr="Yapisal mudahale kesme ve kaynak gerektirmis. Yuksek deger kaybi. Ic camurluk boslugunu dikkatle kontrol edin.",
            advice_en="Structural intervention required cutting and welding. High value loss. Carefully check inner fender cavity."
        ),
        painted=PartConditionConfig(
            deduction=10,
            advice_tr="Yaygin surtunen bolge. Derin macun kullanilmamissa kabul edilebilir.",
            advice_en="Common rubbing area. Acceptable if no heavy filler used."
        ),
        local_painted=PartConditionConfig(
            deduction=5,
            advice_tr="Kucuk suruntme onarimi. Cok yaygin ve genellikle kabul edilebilir.",
            advice_en="Small scuff repair. Very common and generally acceptable."
        )
    ),
    # Side Parts - Kapilar ve On Camurluklar
    "side_part": PartConfig(
        name="Kapilar ve On Camurluklar",
        note="On Camurluklar, Tum Kapilar icin kullanin",
        changed=PartConditionConfig(
            deduction=12,
            advice_tr="Parcalar civatayla takilir, ancak degisim sert yan darbe anlamina gelir. Direkleri ve mentesteleri kontrol edin.",
            advice_en="Parts are bolt-on, but replacement indicates hard side impact. Check pillars and hinges."
        ),
        painted=PartConditionConfig(
            deduction=6,
            advice_tr="Kozmetik cizik veya gocuk onarimi. Sehir trafiginde yaygin. Mekanik sagliga etkisi minimal.",
            advice_en="Cosmetic scratch or dent repair. Common in city traffic. Minimal impact on mechanical health."
        ),
        local_painted=PartConditionConfig(
            deduction=3,
            advice_tr="Cok kucuk rotuş. Degere etkisi ihmal edilebilir.",
            advice_en="Very small touch-up. Negligible impact on value."
        )
    ),
    # Bumper - Tamponlar
    "bumper": PartConfig(
        name="Tamponlar",
        changed=PartConditionConfig(
            deduction=5,
            advice_tr="Plastik parca. Degisim yaygindir ve daha temiz bir gorunum saglar. Sensorleri ve sis farlarini kontrol edin.",
            advice_en="Plastic part. Replacement is common and provides cleaner look. Check sensors and fog lights."
        ),
        painted=PartConditionConfig(
            deduction=2,
            advice_tr="Plastik parca. Estetik icin boyanir. Degere olumsuz etkisi yoktur.",
            advice_en="Plastic part. Painted for aesthetics. No negative impact on value."
        ),
        local_painted=PartConditionConfig(
            deduction=1,
            advice_tr="Plastik parca. Onemsiz kozmetik onarim.",
            advice_en="Plastic part. Insignificant cosmetic repair."
        )
    ),
}

# Mapping from Turkish part names to config keys
PART_NAME_MAPPING: Dict[str, str] = {
    # Roof
    "tavan": "roof",
    # Hood
    "motor kaputu": "hood",
    "kaput": "hood",
    # Trunk
    "bagaj kapagi": "trunk_lid",
    "bagaj": "trunk_lid",
    # Rear fenders
    "arka camurluk sol": "rear_fender",
    "arka camurluk sag": "rear_fender",
    "sol arka camurluk": "rear_fender",
    "sag arka camurluk": "rear_fender",
    # Front fenders
    "on camurluk sol": "side_part",
    "on camurluk sag": "side_part",
    "sol on camurluk": "side_part",
    "sag on camurluk": "side_part",
    # Doors
    "sol on kapi": "side_part",
    "sag on kapi": "side_part",
    "sol arka kapi": "side_part",
    "sag arka kapi": "side_part",
    "on kapi sol": "side_part",
    "on kapi sag": "side_part",
    "arka kapi sol": "side_part",
    "arka kapi sag": "side_part",
    # Bumpers
    "on tampon": "bumper",
    "arka tampon": "bumper",
    "tampon": "bumper",
}


def normalize_part_name(part_name: str) -> str:
    """Normalize Turkish part name to lowercase without Turkish characters"""
    tr_map = {
        'ı': 'i', 'İ': 'i', 'ğ': 'g', 'Ğ': 'g',
        'ü': 'u', 'Ü': 'u', 'ş': 's', 'Ş': 's',
        'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c'
    }
    normalized = part_name.lower().strip()
    for tr_char, en_char in tr_map.items():
        normalized = normalized.replace(tr_char, en_char)
    return normalized


def get_part_config_key(part_name: str) -> Optional[str]:
    """Get the config key for a given part name"""
    normalized = normalize_part_name(part_name)

    # Direct match
    if normalized in PART_NAME_MAPPING:
        return PART_NAME_MAPPING[normalized]

    # Partial match
    for mapped_name, config_key in PART_NAME_MAPPING.items():
        if mapped_name in normalized or normalized in mapped_name:
            return config_key

    return None


@dataclass
class PartDeduction:
    """Details of a single part deduction"""
    part_name: str
    condition: str  # 'changed', 'painted', 'local_painted'
    deduction: int
    advice: str


@dataclass
class CrashScoreResult:
    """Complete crash score analysis result"""
    score: int
    total_deduction: int
    deductions: List[PartDeduction]
    summary: str
    risk_level: str
    verdict: str


# Translations for risk levels, verdicts, and summaries
CRASH_SCORE_TRANSLATIONS = {
    "en": {
        "risk_levels": {
            "minimal": "Minimal Risk",
            "low": "Low Risk",
            "medium": "Medium Risk",
            "high": "High Risk",
            "very_high": "Very High Risk"
        },
        "verdicts": {
            "excellent": "EXCELLENT - No or minimal damage history. Safe to buy.",
            "good": "GOOD - Minor cosmetic repairs present. Safe to buy.",
            "caution": "CAUTION - Noticeable damage history. Detailed inspection required.",
            "danger": "DANGER - Serious damage history. Purchase not recommended.",
            "not_buyable": "DO NOT BUY - Vehicle heavily damaged. Safety risk present."
        },
        "summaries": {
            "excellent": "Vehicle is in near-pristine condition. No or very few painted or changed parts.",
            "good": "Vehicle has minor cosmetic repairs but no structural issues detected.",
            "caution": "Vehicle has noticeable repair signs. Professional inspection recommended.",
            "danger": "Vehicle has serious damage history. Structural problems may exist.",
            "not_buyable": "Vehicle has very severe damage history. May be dangerous for safety."
        },
        "unknown_part": {
            "changed": "Unknown part replacement: {part}. Detailed inspection recommended.",
            "painted": "Unknown part paint: {part}. Investigate repair history.",
            "local_painted": "Unknown part local paint: {part}. Could be cosmetic repair."
        }
    },
    "tr": {
        "risk_levels": {
            "minimal": "Minimal Risk",
            "low": "Dusuk Risk",
            "medium": "Orta Risk",
            "high": "Yuksek Risk",
            "very_high": "Cok Yuksek Risk"
        },
        "verdicts": {
            "excellent": "MUKEMMEL - Hasar gecmisi yok veya minimumdur. Alinabilir.",
            "good": "IYI - Kucuk kozmetik onarimlar var. Alinabilir.",
            "caution": "DIKKAT - Belirgin hasar gecmisi var. Detayli inceleme sart.",
            "danger": "TEHLIKE - Ciddi hasar gecmisi. Alinmasi onerilmez.",
            "not_buyable": "KESINLIKLE ALINMAMALI - Arac agir hasarli. Guvenlik riski var."
        },
        "summaries": {
            "excellent": "Arac neredeyse kusursuz durumda. Boyali veya degisen parca yok ya da cok az.",
            "good": "Aracta kucuk kozmetik onarimlar mevcut ancak yapisal bir sorun gorulmuyor.",
            "caution": "Aracta belirgin onarim izleri var. Profesyonel ekspertiz onerilir.",
            "danger": "Arac ciddi hasar gecmisine sahip. Yapisal problemler olabilir.",
            "not_buyable": "Arac cok agir hasar gecmisine sahip. Guvenlik acisindan tehlikeli olabilir."
        },
        "unknown_part": {
            "changed": "Bilinmeyen parca degisimi: {part}. Detayli inceleme onerilir.",
            "painted": "Bilinmeyen parca boyasi: {part}. Onarim gecmisini arastirin.",
            "local_painted": "Bilinmeyen parca lokal boya: {part}. Kozmetik onarim olabilir."
        }
    }
}


def calculate_crash_score(
    painted_parts: Optional[List[str]] = None,
    changed_parts: Optional[List[str]] = None,
    local_painted_parts: Optional[List[str]] = None,
    language: Language = "en"
) -> CrashScoreResult:
    """
    Calculate crash score based on damaged/painted/changed parts.

    Args:
        painted_parts: List of painted (boyali) part names in Turkish
        changed_parts: List of changed (degisen) part names in Turkish
        local_painted_parts: List of locally painted (lokal boyali) part names in Turkish

    Returns:
        CrashScoreResult with score, deductions, and advice
    """
    score = 100
    total_deduction = 0
    deductions: List[PartDeduction] = []
    translations = CRASH_SCORE_TRANSLATIONS[language]

    # Process changed parts (highest severity)
    if changed_parts:
        for part in changed_parts:
            config_key = get_part_config_key(part)
            if config_key and config_key in PARTS_CONFIG:
                config = PARTS_CONFIG[config_key]
                deduction = config.changed.deduction
                total_deduction += deduction
                deductions.append(PartDeduction(
                    part_name=part,
                    condition="degisen",
                    deduction=deduction,
                    advice=config.changed.get_advice(language)
                ))
            else:
                # Unknown part, apply default deduction
                default_deduction = 15
                total_deduction += default_deduction
                deductions.append(PartDeduction(
                    part_name=part,
                    condition="degisen",
                    deduction=default_deduction,
                    advice=translations["unknown_part"]["changed"].format(part=part)
                ))
                logger.warning(f"Unknown changed part: {part}")

    # Process painted parts (medium severity)
    if painted_parts:
        for part in painted_parts:
            config_key = get_part_config_key(part)
            if config_key and config_key in PARTS_CONFIG:
                config = PARTS_CONFIG[config_key]
                deduction = config.painted.deduction
                total_deduction += deduction
                deductions.append(PartDeduction(
                    part_name=part,
                    condition="boyali",
                    deduction=deduction,
                    advice=config.painted.get_advice(language)
                ))
            else:
                # Unknown part, apply default deduction
                default_deduction = 8
                total_deduction += default_deduction
                deductions.append(PartDeduction(
                    part_name=part,
                    condition="boyali",
                    deduction=default_deduction,
                    advice=translations["unknown_part"]["painted"].format(part=part)
                ))
                logger.warning(f"Unknown painted part: {part}")

    # Process locally painted parts (lowest severity)
    if local_painted_parts:
        for part in local_painted_parts:
            config_key = get_part_config_key(part)
            if config_key and config_key in PARTS_CONFIG:
                config = PARTS_CONFIG[config_key]
                deduction = config.local_painted.deduction
                total_deduction += deduction
                deductions.append(PartDeduction(
                    part_name=part,
                    condition="lokal_boyali",
                    deduction=deduction,
                    advice=config.local_painted.get_advice(language)
                ))
            else:
                # Unknown part, apply default deduction
                default_deduction = 4
                total_deduction += default_deduction
                deductions.append(PartDeduction(
                    part_name=part,
                    condition="lokal_boyali",
                    deduction=default_deduction,
                    advice=translations["unknown_part"]["local_painted"].format(part=part)
                ))
                logger.warning(f"Unknown local painted part: {part}")

    # Calculate final score (minimum 0)
    score = max(0, 100 - total_deduction)

    # Determine risk level and verdict using translations
    if score >= 90:
        risk_level = translations["risk_levels"]["minimal"]
        verdict = translations["verdicts"]["excellent"]
        summary = translations["summaries"]["excellent"]
    elif score >= 70:
        risk_level = translations["risk_levels"]["low"]
        verdict = translations["verdicts"]["good"]
        summary = translations["summaries"]["good"]
    elif score >= 50:
        risk_level = translations["risk_levels"]["medium"]
        verdict = translations["verdicts"]["caution"]
        summary = translations["summaries"]["caution"]
    elif score >= 25:
        risk_level = translations["risk_levels"]["high"]
        verdict = translations["verdicts"]["danger"]
        summary = translations["summaries"]["danger"]
    else:
        risk_level = translations["risk_levels"]["very_high"]
        verdict = translations["verdicts"]["not_buyable"]
        summary = translations["summaries"]["not_buyable"]

    return CrashScoreResult(
        score=score,
        total_deduction=total_deduction,
        deductions=deductions,
        summary=summary,
        risk_level=risk_level,
        verdict=verdict
    )


def crash_score_to_dict(result: CrashScoreResult) -> Dict[str, Any]:
    """Convert CrashScoreResult to dictionary for JSON serialization"""
    return {
        "score": result.score,
        "total_deduction": result.total_deduction,
        "deductions": [
            {
                "part_name": d.part_name,
                "condition": d.condition,
                "deduction": d.deduction,
                "advice": d.advice
            }
            for d in result.deductions
        ],
        "summary": result.summary,
        "risk_level": result.risk_level,
        "verdict": result.verdict
    }
