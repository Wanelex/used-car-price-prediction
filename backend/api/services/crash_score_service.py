"""
Crash Score Calculation Service

Calculates a crash/damage score based on painted (boyali), locally painted (lokal_boyali),
and changed (degisen) parts. Score starts at 100 (pristine condition) and deducts points
based on the condition of each part.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger


@dataclass
class PartConditionConfig:
    """Configuration for a single part condition (changed/painted/local_painted)"""
    deduction: int
    advice: str


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
            advice="Kritik yapisal risk. Takla veya agir kaza ihtimali yuksek. Satin alinmasi kesinlikle onerilmez."
        ),
        painted=PartConditionConfig(
            deduction=30,
            advice="Yuksek risk. Takla veya agir cisim darbesi olabilir. Macun kalinligi ve ic direk hasarini kontrol edin."
        ),
        local_painted=PartConditionConfig(
            deduction=15,
            advice="Supheli. Kozmetik (kus piskligi vb.) veya anten onarimi olabilir, ancak dikkatli inceleme gerektirir."
        )
    ),
    # Hood - Motor Kaputu
    "hood": PartConfig(
        name="Motor Kaputu",
        changed=PartConditionConfig(
            deduction=35,
            advice="Buyuk on carpisma ihtimali yuksek. Sasi, podya ve havayastiklarini dikkatle kontrol edin. Kaza fotograflari dogrulanmadikca onerilmez."
        ),
        painted=PartConditionConfig(
            deduction=15,
            advice="Muhtemelen on darbe veya tas cizigidir. On panel ve radyator destek sacinda orijinal etiketleri kontrol edin."
        ),
        local_painted=PartConditionConfig(
            deduction=8,
            advice="Kucuk kozmetik rotuş. Genellikle kabul edilebilir, renk uyumunu kontrol edin."
        )
    ),
    # Trunk Lid - Bagaj Kapagi
    "trunk_lid": PartConfig(
        name="Bagaj Kapagi",
        changed=PartConditionConfig(
            deduction=20,
            advice="Onemli arkadan carpismayi gosterir. Bagaj havuzu ve arka sasi panelinde kaynak izlerini kontrol edin."
        ),
        painted=PartConditionConfig(
            deduction=10,
            advice="Orta seviye arka darbe. Ic yapi saglam ise genellikle kabul edilebilir."
        ),
        local_painted=PartConditionConfig(
            deduction=5,
            advice="Kucuk kozmetik onarim. Arac degerine etkisi dusuk."
        )
    ),
    # Rear Fender - Arka Camurluk
    "rear_fender": PartConfig(
        name="Arka Camurluk",
        note="Sol/Sag",
        changed=PartConditionConfig(
            deduction=20,
            advice="Yapisal mudahale kesme ve kaynak gerektirmis. Yuksek deger kaybi. Ic camurluk boslugunu dikkatle kontrol edin."
        ),
        painted=PartConditionConfig(
            deduction=10,
            advice="Yaygin surtunen bolge. Derin macun kullanilmamissa kabul edilebilir."
        ),
        local_painted=PartConditionConfig(
            deduction=5,
            advice="Kucuk suruntme onarimi. Cok yaygin ve genellikle kabul edilebilir."
        )
    ),
    # Side Parts - Kapilar ve On Camurluklar
    "side_part": PartConfig(
        name="Kapilar ve On Camurluklar",
        note="On Camurluklar, Tum Kapilar icin kullanin",
        changed=PartConditionConfig(
            deduction=12,
            advice="Parcalar civatayla takilir, ancak degisim sert yan darbe anlamina gelir. Direkleri ve mentesteleri kontrol edin."
        ),
        painted=PartConditionConfig(
            deduction=6,
            advice="Kozmetik cizik veya gocuk onarimi. Sehir trafiginde yaygin. Mekanik sagliga etkisi minimal."
        ),
        local_painted=PartConditionConfig(
            deduction=3,
            advice="Cok kucuk rotuş. Degere etkisi ihmal edilebilir."
        )
    ),
    # Bumper - Tamponlar
    "bumper": PartConfig(
        name="Tamponlar",
        changed=PartConditionConfig(
            deduction=5,
            advice="Plastik parca. Degisim yaygindir ve daha temiz bir gorunum saglar. Sensorleri ve sis farlarini kontrol edin."
        ),
        painted=PartConditionConfig(
            deduction=2,
            advice="Plastik parca. Estetik icin boyanir. Degere olumsuz etkisi yoktur."
        ),
        local_painted=PartConditionConfig(
            deduction=1,
            advice="Plastik parca. Onemsiz kozmetik onarim."
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


def calculate_crash_score(
    painted_parts: Optional[List[str]] = None,
    changed_parts: Optional[List[str]] = None,
    local_painted_parts: Optional[List[str]] = None
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
                    advice=config.changed.advice
                ))
            else:
                # Unknown part, apply default deduction
                default_deduction = 15
                total_deduction += default_deduction
                deductions.append(PartDeduction(
                    part_name=part,
                    condition="degisen",
                    deduction=default_deduction,
                    advice=f"Bilinmeyen parca degisimi: {part}. Detayli inceleme onerilir."
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
                    advice=config.painted.advice
                ))
            else:
                # Unknown part, apply default deduction
                default_deduction = 8
                total_deduction += default_deduction
                deductions.append(PartDeduction(
                    part_name=part,
                    condition="boyali",
                    deduction=default_deduction,
                    advice=f"Bilinmeyen parca boyasi: {part}. Onarim gecmisini arastirin."
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
                    advice=config.local_painted.advice
                ))
            else:
                # Unknown part, apply default deduction
                default_deduction = 4
                total_deduction += default_deduction
                deductions.append(PartDeduction(
                    part_name=part,
                    condition="lokal_boyali",
                    deduction=default_deduction,
                    advice=f"Bilinmeyen parca lokal boya: {part}. Kozmetik onarim olabilir."
                ))
                logger.warning(f"Unknown local painted part: {part}")

    # Calculate final score (minimum 0)
    score = max(0, 100 - total_deduction)

    # Determine risk level and verdict
    if score >= 90:
        risk_level = "Minimal Risk"
        verdict = "MUKEMMEL - Hasar gecmisi yok veya minimumdur. Alinabilir."
        summary = "Arac neredeyse kusursuz durumda. Boyali veya degisen parca yok ya da cok az."
    elif score >= 70:
        risk_level = "Dusuk Risk"
        verdict = "IYI - Kucuk kozmetik onarimlar var. Alinabilir."
        summary = "Aracta kucuk kozmetik onarimlar mevcut ancak yapisal bir sorun gorulmuyor."
    elif score >= 50:
        risk_level = "Orta Risk"
        verdict = "DIKKAT - Belirgin hasar gecmisi var. Detayli inceleme sart."
        summary = "Aracta belirgin onarim izleri var. Profesyonel ekspertiz onerilir."
    elif score >= 25:
        risk_level = "Yuksek Risk"
        verdict = "TEHLIKE - Ciddi hasar gecmisi. Alinmasi onerilmez."
        summary = "Arac ciddi hasar gecmisine sahip. Yapisal problemler olabilir."
    else:
        risk_level = "Cok Yuksek Risk"
        verdict = "KESINLIKLE ALINMAMALI - Arac agir hasarli. Guvenlik riski var."
        summary = "Arac cok agir hasar gecmisine sahip. Guvenlik acisindan tehlikeli olabilir."

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
