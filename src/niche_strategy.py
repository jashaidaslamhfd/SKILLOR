"""
Niche Strategy Module for SKILLOR Pipeline
OPTIMIZED FOR: HIGH RETENTION + PSYCHOLOGICAL PACING
"""

import logging
import random
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# ============================================
# 1. EXPANDED DARK TOPICS (100+ topics)
# ============================================
DARK_TOPICS = [
    # Cerebro / Mente / Neurociencia (25+)
    "Tu Corazón Tiene Su Propio Cerebro",
    "Esto Pasa Dentro de Tu Cerebro Cuando Duermes",
    "Por Qué Se Te Pone la Piel de Gallina",
    "Tu Cerebro Se Come a Sí Mismo Mientras Duermes",
    "La Parte de Tu Cerebro Que Nunca Duerme",
    "Por Qué Tu Cerebro Te Miente Todos los Días",
    "Esto Es Lo Que Realmente Es el Déjà Vu",
    "Tu Cerebro Puede Reconectarse en Una Noche",
    "La Razón Por la Que Hablas Contigo Mismo en Tu Mente",
    "Por Qué Existen las Pesadillas",
    "Tu Cerebro Borra Recuerdos a Propósito",
    "La Razón Real Por la Que Te Congelas Bajo Presión",
    "Por Qué Algunas Personas Nunca Olvidan un Rostro",
    "Tu Cerebro Tiene un Sistema de Respaldo Oculto",
    "El Químico Que Te Hace Enamorarte",
    "Por Qué Tu Cerebro Procesa el Miedo Más Rápido Que la Lógica",
    "La Parte de Tu Cerebro Que Nunca Deja de Crecer",
    "Por Qué No Puedes Recordar Cuando Eras Bebé",
    "Tu Cerebro Tiene Su Propio Sistema Inmune",
    "La Razón Por la Que Te Da Dolor de Cabeza por Frío",
    "Por Qué Tu Cerebro Se Encoge Cuando Estás Deprimido",
    "El Lenguaje Secreto de Tus Ondas Cerebrales",
    "Por Qué Tu Cerebro Te Hace Ver Fantasmas",
    "La Razón Por la Que Tu Cerebro Olvida Nombres",
    "Tu Cerebro Crea la Realidad, No Solo la Percibe",
    
    # Corazón / Sangre / Circulatorio (20+)
    "Tu Cuerpo Tiene 100,000 km de Venas",
    "Por Qué Tu Corazón Se Salta un Latido",
    "Tu Sangre Tiene un Arma Secreta",
    "Tu Corazón Late 100,000 Veces al Día Sin Preguntar",
    "El Sonido Que Hace Tu Corazón Que Nunca Has Escuchado",
    "Por Qué Tu Cara Se Pone Roja Cuando Estás Enojado",
    "La Razón Por la Que Manos Frías Significan un Corazón Cálido",
    "Tu Sangre Cambia de Color Dentro de Tu Cuerpo",
    "Tu Corazón Puede Predecir Tu Muerte",
    "El Secreto Detrás de Tu Latido",
    "Por Qué Tu Sangre Es Realmente Azul por Dentro",
    "Tu Corazón Tiene Su Propio Sistema Eléctrico",
    "La Razón Por la Que Tu Pulso Cambia Cuando Mientes",
    "Tus Vasos Sanguíneos Podrían Rodear la Tierra",
    "Por Qué Tu Corazón Se Rompe Cuando Estás Triste",
    "El Poder Oculto de Tu Tipo de Sangre",
    "Por Qué Tu Corazón Late Más Rápido en la Mañana",
    "La Razón Por la Que Tu Sangre Coagula Cuando Te Cortas",
    "Tu Corazón Tiene Su Propia Memoria",
    "Por Qué Tu Presión Sube Cuando Estás Estresado",
    
    # Pulmones / Respiración (15+)
    "Tus Pulmones Pueden Ahogarte Desde Adentro",
    "Por Qué Bostezas Cuando Ves a Alguien Bostezar",
    "La Razón Real Por la Que No Puedes Hacerte Cosquillas a Ti Mismo",
    "Por Qué Aguantar la Respiración Se Siente Como Pánico",
    "Tus Pulmones Tienen Su Propio Sistema de Limpieza",
    "La Razón Por la Que Estornudas al Ver la Luz",
    "Tu Respiración Cambia Cuando Piensas",
    "Por Qué Tus Pulmones Nunca Se Vacían del Todo",
    "El Poder Secreto de la Respiración Profunda",
    "Por Qué Respiras Diferente en la Noche",
    "La Razón Por la Que Te Duelen los Pulmones en el Frío",
    "Tus Pulmones Pueden Sanarse Solos",
    "Por Qué los Ataques de Asma Ocurren en la Noche",
    "La Conexión Oculta Entre la Respiración y la Ansiedad",
    "Por Qué Tu Respiración Se Hace Más Lenta Cuando Duermes",
    
    # Huesos / Músculos (15+)
    "El Hueso Que Más Se Rompe en Peleas",
    "Tus Huesos Se Están Reemplazando Ahora Mismo",
    "Por Qué Tronarte los Dedos Hace Ese Sonido",
    "El Músculo Más Fuerte de Tu Cuerpo No Es el Que Piensas",
    "Por Qué Pierdes Estatura Durante el Día",
    "Tus Huesos Son Más Fuertes Que el Acero",
    "El Músculo Que Nunca Se Cansa",
    "Por Qué Tu Mandíbula Es el Músculo Más Fuerte",
    "Tu Esqueleto Se Regenera Cada 10 Años",
    "El Hueso Que Realmente Está Fusionado al Nacer",
    "Por Qué Te Duelen los Músculos Después de Ejercitarte",
    "El Secreto Para Ganar Músculo Más Rápido",
    "Por Qué Tus Huesos Se Debilitan Con la Edad",
    "El Hueso Más Fuerte de Tu Cuerpo",
    "Por Qué No Puedes Moverte Cuando Duermes",
    
    # Digestivo / Órganos (15+)
    "Tu Estómago Puede Digerirse a Sí Mismo",
    "El Órgano Sin el Que Puedes Vivir",
    "Tu Intestino Tiene Su Propio Sistema Nervioso",
    "Por Qué Te Suena el Estómago Aunque No Tengas Hambre",
    "El Órgano Que Se Regenera Completamente",
    "Por Qué No Puedes Respirar y Tragar al Mismo Tiempo",
    "Tu Hígado Puede Regenerarse en 30 Días",
    "La Razón Por la Que Tienes Acidez",
    "Tu Intestino Tiene Más Neuronas Que Tu Médula Espinal",
    "El Órgano Que Decide Tu Estado de Ánimo",
    "Por Qué Tu Digestión Se Hace Más Lenta en la Noche",
    "El Secreto de un Intestino Sano",
    "Por Qué Te Duele el Estómago Cuando Estás Nervioso",
    "El Órgano Que Controla Tu Apetito",
    "Por Qué Te Dan Antojos de Comida",
    
    # Piel / Sentidos (15+)
    "Tu Piel Se Renueva Cada Mes",
    "Por Qué Tus Ojos Nunca Dejan de Moverse",
    "La Razón Por la Que Tus Orejas Nunca Dejan de Crecer",
    "Por Qué No Puedes Ver Tu Propio Punto Ciego",
    "Tus Huellas Digitales Empezaron a Formarse Antes de Nacer",
    "Tu Piel Tiene Su Propio Sistema Inmune",
    "Por Qué Tu Cabello Cambia de Color Con la Edad",
    "La Razón Por la Que Se Te Pone Piel de Gallina Con el Frío",
    "Tus Ojos Tienen un Punto Ciego Que Nunca Notas",
    "Por Qué Tu Olfato Cambia en la Noche",
    "El Secreto del Microbioma de Tu Piel",
    "Por Qué Tu Piel Cambia Con el Estrés",
    "La Razón Por la Que Tienes Ojeras",
    "Por Qué Se Arrugan Tus Dedos en el Agua",
    "El Poder Oculto de Tu Sentido del Tacto",
    
    # Misterio / Datos Oscuros (20+)
    "El Sonido Que Solo Tu Cuerpo Puede Oír",
    "Por Qué el Miedo Tiene un Olor Físico",
    "El Momento en Que Tu Cuerpo Sabe Que Estás Mintiendo",
    "Por Qué Tu Cuerpo Recuerda el Trauma Antes Que Tu Mente",
    "El Reflejo Que No Puedes Controlar Pase Lo Que Pase",
    "Por Qué Algunas Personas Sienten el Dolor Diferente",
    "La Señal Que Envía Tu Cuerpo Antes de Que Notes Que Estás Enfermo",
    "Por Qué Tu Temperatura Baja Justo Antes de Despertar",
    "Tu Cuerpo Tiene un Órgano de Respaldo Oculto",
    "La Razón Por la Que Te Dan Escalofríos Cuando Tienes Miedo",
    "Por Qué Tu Cuerpo Se Sacude Cuando Duermes",
    "La Señal Secreta de Muerte Que Envía Tu Cuerpo",
    "Por Qué Tu Cuerpo Huele Diferente Cuando Estás Ansioso",
    "El Lenguaje Oculto de Tu Lenguaje Corporal",
    "Por Qué Tu Cuerpo Se Congela Cuando Estás en Peligro",
    "La Razón Por la Que Tu Corazón Late Fuerte en una Multitud",
    "Por Qué Tu Cuerpo Puede Sanarse Sin Que Te Des Cuenta",
    "La Inteligencia Oculta de Tu Sistema Inmune",
    "Por Qué Tu Cuerpo Anhela la Naturaleza",
    "Los Ritmos Secretos de Tu Reloj Biológico",
]

# ============================================
# 2. HOOK FORMULAS (25+ with CLIFFHANGER ENDINGS)
# ============================================
HOOK_FORMULAS = [
    "Esto le pasa a tu cuerpo cada noche... y no tienes idea.",
    "Los médicos no quieren que sepas esto sobre {topic}...",
    "Tu cuerpo te está mintiendo sobre {topic}. Aquí está la verdad.",
    "Nadie te dijo que esto está pasando dentro de ti ahora mismo.",
    "Esta es la parte de {topic} que tu profesor de biología se saltó.",
    "Has hecho esto un millón de veces y nunca te preguntaste por qué.",
    "Algo en tu cuerpo está pasando sin tu permiso.",
    "Esto suena falso, pero {topic} es 100% real.",
    "Los científicos apenas descubrieron esto sobre {topic} hace poco.",
    "Tu cuerpo te ha estado ocultando esto toda tu vida.",
    "Por esto {topic} se siente tan inquietante cuando lo sabes.",
    "La mayoría de la gente pasa toda su vida sin saber esto sobre {topic}.",
    "Si esto te pasó, tu cuerpo hizo algo increíble.",
    "Hay una razón por la que nadie habla de {topic}.",
    "Esto es lo más espeluznante que hace tu propio cuerpo.",
    "¿Y si te dijera que {topic} es completamente diferente a lo que piensas?",
    "La verdad sobre {topic} que nadie quiere admitir.",
    "Este dato sobre {topic} cambiará cómo te ves a ti mismo.",
    "No vas a creer lo que {topic} realmente significa para tu cuerpo.",
    "Esto es lo que pasa por dentro cuando ocurre {topic}.",
    "El secreto oculto de {topic} que ha estado frente a ti todo este tiempo.",
    "Por qué {topic} es lo más incomprendido de tu cuerpo.",
    "Cada vez que pasa {topic}, tu cuerpo está tratando de decirte algo.",
    "La ciencia detrás de {topic} es más extraña que la ficción.",
    "Esta es la razón real por la que {topic} pasa en tu cuerpo.",
]

# ============================================
# 3. TRANSITION HOOKS (For Scene-to-Scene Retention)
# ============================================
TRANSITION_HOOKS = [
    "pero eso es solo la mitad de la historia...",
    "y no vas a creer por qué...",
    "aquí es donde se pone realmente extraño...",
    "pero espera... hay más...",
    "y esta es la parte que nadie te cuenta...",
    "pero aquí está la parte impactante...",
    "y ahí es cuando las cosas se ponen oscuras...",
    "pero tu cuerpo tiene un secreto...",
    "y esto lo cambia todo...",
    "pero la razón real te va a sorprender...",
    "y se pone aún más raro...",
    "pero aquí está el giro...",
]

# ============================================
# 4. PAIN POINTS (15+)
# ============================================
PAIN_POINTS = [
    "Preocupados de que algo esté mal con su cuerpo",
    "No pueden dormir porque su mente no se apaga",
    "Sienten ansiedad por síntomas corporales random",
    "Notan algo en su cuerpo y no lo pueden explicar",
    "Sienten que su cuerpo es un misterio hasta para ellos mismos",
    "Se asustan por síntomas que no entienden",
    "Se preguntan si lo que les pasa es normal",
    "Se sienten desconectados de cómo funciona su propio cuerpo",
    "Buscan síntomas en Google de noche y entran en pánico",
    "Sienten que nadie explica esto de forma clara",
    "Se preocupan por envejecer y lo que eso significa para su cuerpo",
    "Se sienten impotentes cuando su cuerpo no coopera",
    "Quieren entender por qué su cuerpo reacciona diferente a otros",
    "Sienten vergüenza de funciones corporales que no pueden controlar",
    "Se preguntan si su cuerpo está funcionando bien",
]

# ============================================
# 5. CTAS (15+)
# ============================================
CTAS = [
    "Sígueme para más secretos oscuros del cuerpo",
    "Comparte esto si te voló la mente",
    "Comenta: ¿Te ha pasado esto a ti?",
    "Guarda esto antes de que se te olvide",
    "Sígueme si tu cuerpo te acaba de hacer esto",
    "Etiqueta a alguien que necesita ver esto",
    "Comenta 'igual' si esto también te pasa a ti",
    "Comparte esto con alguien que piensa demasiado las cosas",
    "Sígueme para el próximo dato oscuro del cuerpo",
    "Envíaselo al amigo que siempre está frío/cansado/ansioso",
    "Deja un ❤️ si aprendiste algo nuevo",
    "Comenta '🤯' si esto te sorprendió",
    "Guarda esto para cuando quieras impresionar a alguien con datos",
    "Comparte para que alguien piense dos veces sobre su cuerpo",
    "Sígueme para desbloquear más misterios del cuerpo",
]

# ============================================
# 6. CATEGORY TAGS (SEO)
# ============================================
CATEGORY_TAGS = {
    "Brain": [
        "neurociencia", "datoscerebro", "psicologia", "mentevolada",
        "cienciacerebral", "cerebrohumano", "sistemanervioso", "trucosmentales",
        "saludcerebral", "neuroplasticidad", "cognicion", "memoria",
    ],
    "Body": [
        "cuerpohumano", "datoscuerpo", "anatomia", "partesdelcuerpo", "datoshumanos",
        "concienciacorporal", "misteriocorporal", "tucuerpo", "fisiologia",
        "anatomiahumana", "cienciacorporal", "datosdesalud",
    ],
    "Mystery": [
        "cienciamisterio", "datosraros", "datosespeluznantes", "datosdesconocidos",
        "cienciaoscura", "secretosdelcuerpo", "ahorayasabes", "mentevolada",
        "datosaterradores", "inexplicable", "paranormal",
    ],
    "Health": [
        "datosdesalud", "trucosdesalud", "datoscientificos", "cienciadesalud",
        "misteriomedico", "saludhumana", "bienestar", "consejosdesalud",
        "viajedebienestar", "vidasaludable",
    ],
}

# ============================================
# 7. BASE TAGS
# ============================================
BASE_TAGS = [
    "datososcuros", "datos", "shorts", "youtubeshorts", "ciencia",
    "sabiasque", "mentevolada", "datoscuriosos", "datosaterradores", "viral",
    "misterio", "desconocido", "espeluznante", "interesante", "educacion",
]

# ============================================
# 8. CONSTANTS
# ============================================
TARGET_WORD_RANGE = (130, 170)
MAX_TAGS = 15
MAX_TITLE_LENGTH = 55
SCENES_PER_SCRIPT = 9  # Optimized for 3-5 second scenes

# ============================================
# 9. MEDICAL RED FLAGS
# ============================================
_MEDICAL_ADVICE_RED_FLAGS = [
    "cura", "diagnostica", "tienes", "deja de tomar", "no necesitas un médico",
    "en lugar de medicamento", "garantizado para sanar", "definitivamente significa que tienes",
    "deberías", "debes", "nunca vayas al médico", "ignora a tu médico",
    "esta es la única cura", "mejor que la medicina", "reemplaza tu medicamento",
]

# ============================================
# 10. RETENTION-OPTIMIZED PROMPT GENERATION
# ============================================

def get_script_prompt_for_niche(
    topic: str, 
    hook_preference: Optional[str] = None
) -> str:
    """
    Generates a RETENTION-OPTIMIZED prompt for script generation.
    Focuses on: Psychological Pacing, Visual Stimulation, and Cliffhangers.
    
    Args:
        topic: Topic string
        hook_preference: Specific hook to use (optional)
    
    Returns:
        Prompt string for AI
    """
    # Select hook
    if not hook_preference:
        hook_preference = random.choice(HOOK_FORMULAS)
        if "{topic}" in hook_preference:
            hook_preference = hook_preference.format(topic=topic)
    
    # Select pain point and CTA
    pain_point = random.choice(PAIN_POINTS)
    cta = random.choice(CTAS)
    
    # Word count and scene configuration
    min_w, max_w = TARGET_WORD_RANGE
    num_scenes = SCENES_PER_SCRIPT
    per_scene_lo = min_w // num_scenes
    per_scene_hi = max_w // num_scenes
    
    # Select random transitions for cliffhangers
    transitions = random.sample(TRANSITION_HOOKS, min(5, len(TRANSITION_HOOKS)))
    
    # Build RETENTION-OPTIMIZED prompt (in Spanish)
    prompt = f"""
Eres un comunicador científico experto creando YouTube Shorts de ALTA RETENCIÓN para adultos hispanohablantes 18+.

**IMPORTANTE - ESCRIBE TODO EN ESPAÑOL NATURAL:**
- Escribe como un HUMANO hablando con un amigo, no como una IA
- Usa un español neutro, natural y conversacional (evita modismos muy regionales)
- Usa lenguaje coloquial: "honestamente", "en serio", "literalmente"
- EVITA palabras robóticas: "por lo tanto", "asimismo", "no obstante"
- Que suene NATURAL al leerlo en voz alta

TEMA: {topic}

🎯 ESTRATEGIA DE RETENCIÓN (CRÍTICO):
- Cada escena debe terminar con un GANCHO DE SUSPENSO que haga que el espectador QUIERA ver la siguiente escena
- Usa lenguaje directo con "TÚ" en todo momento (ej. "Tu cerebro", "Tú sientes") - hazlo PERSONAL
- Cada escena DEBE ser de 3-5 segundos de contenido hablado (corto, directo, intenso)
- Construye el patrón CURIOSIDAD > REVELACIÓN > GANCHO en cada escena

ESTRUCTURA DEL GUION:
1. GANCHO OSCURO: "{hook_preference}"
2. RELACIONA la información con la vida diaria del espectador
3. CIENCIA detrás del fenómeno (simplificada, intrigante)
4. REVELACIÓN que impacta o sorprende
5. Transición de GANCHO hacia la siguiente escena
6. CTA: "{cta}"
7. AVISO: Solo con fines educativos/de entretenimiento, no es consejo médico

TONO: Oscuro, misterioso, factual, atractivo, personal
PUNTO DE DOLOR: {pain_point}
TRANSICIONES DE GANCHO SUGERIDAS (usa un estilo similar entre escenas): {', '.join(transitions)}

📝 REQUISITOS DE ESCENA:

CONTEO DE PALABRAS (REQUISITO ESTRICTO):
- El total de la voz en off DEBE ser {min_w}-{max_w} palabras
- Divide en exactamente {num_scenes} escenas
- Cada texto de escena: {per_scene_lo}-{per_scene_hi} palabras
- Cada escena = 3-5 segundos de habla

CALIDAD DEL TEXTO PARA RETENCIÓN:
- Empieza cada escena con un MICRO-GANCHO (ej. "Pero aquí está el giro...")
- Termina cada escena con un GANCHO DE SUSPENSO (ej. "...y ahí es cuando se pone raro")
- Usa oraciones cortas y directas (5-10 palabras máximo por oración)
- Construye tensión con cada oración
- SIN relleno - cada palabra debe aportar valor
- Conecta cada escena con la experiencia personal del espectador

🎨 DESCRIPCIÓN VISUAL (CRÍTICO PARA RETENCIÓN):
- "visual": Describe una imagen VISUALMENTE ESTIMULANTE (en inglés, para el generador de imágenes)
- Usa palabras como: cinematic, high-contrast, macro-lens, motion blur, dark, moody
- Cada visual debe ser ÚNICO y DINÁMICO (sin imágenes estáticas)
- Considera: iluminación dramática, primeros planos, representaciones abstractas, metáforas

FORMATO DE ESCENA:
Para cada escena, proporciona:
- "visual": 5-8 palabras describiendo una imagen CINEMATOGRÁFICA, en inglés (ej. "Macro shot of a beating heart, dark background")
- "caption": El texto EXACTO hablado, en ESPAÑOL (directo, con gancho, personal)

FORMATO DE SALIDA:
Devuelve SOLO JSON válido, sin ningún otro texto (las claves quedan en inglés, los valores en español):

{{
  "title": "Título corto y llamativo en español (menos de 55 caracteres)",
  "hook": "{hook_preference}",
  "scenes": [
    {{"visual": "...", "caption": "..."}},
    ...
  ],
  "cta": "{cta}",
  "description": "Descripción del video en español, 1-2 oraciones"
}}

⚡ LISTA DE VERIFICACIÓN DE RETENCIÓN (ANTES DE FINALIZAR):
✓ Cada escena termina con un gancho de suspenso
✓ Lenguaje con "TÚ" usado en todo momento
✓ Cada escena es de 3-5 segundos de habla
✓ Las descripciones visuales son CINEMATOGRÁFICAS y ÚNICAS (en inglés)
✓ Conteo total de palabras: {min_w}-{max_w}
✓ Exactamente {num_scenes} escenas
✓ Sin consejos médicos
✓ Tono oscuro, misterioso, científico
✓ Todo el texto hablado (hook, caption, cta, title, description) está en ESPAÑOL

RECUERDA: El espectador debe sentirse OBLIGADO a ver la siguiente escena. Hazlo ADICTIVO.
"""
    return prompt


def get_random_transition_hook() -> str:
    """Get a random transition hook for scene endings"""
    return random.choice(TRANSITION_HOOKS)


def get_transition_hooks(count: int = 3) -> List[str]:
    """Get multiple transition hooks"""
    return random.sample(TRANSITION_HOOKS, min(count, len(TRANSITION_HOOKS)))

# ============================================
# 11. CORE FUNCTIONS
# ============================================

def get_random_topic(exclude: Optional[List[str]] = None) -> str:
    """
    Picks a topic for the next video.
    
    Priority:
    1. Live trend-research topics (60% chance when available)
    2. Static DARK_TOPICS pool (fallback)
    3. Skips recently used topics from exclude list
    
    Args:
        exclude: List of topics to exclude (recently used)
    
    Returns:
        Selected topic string
    """
    exclude_set = {t.strip().lower() for t in (exclude or []) if t}
    logger.debug(f"Excluding {len(exclude_set)} recent topics")

    # Try to get trending topics
    trending = []
    try:
        from trend_research import fetch_trending_topics
        trending = fetch_trending_topics()
        logger.debug(f"Fetched {len(trending)} trending topics")
    except ImportError:
        logger.debug("Trend research module not available")
    except Exception as e:
        logger.warning(f"Trend research failed: {e}")

    # Filter trending topics
    trend_candidates = [
        t for t in trending 
        if t.strip().lower() not in exclude_set
    ]
    
    # 60% chance to use trending if available
    if trend_candidates and random.random() < 0.6:
        chosen = random.choice(trend_candidates)
        logger.info(f"Selected trending topic: {chosen}")
        return chosen

    # Fallback to static pool
    static_candidates = [
        t for t in DARK_TOPICS 
        if t.strip().lower() not in exclude_set
    ]
    
    if static_candidates:
        chosen = random.choice(static_candidates)
        logger.info(f"Selected static topic: {chosen}")
        return chosen
    
    # If everything is excluded, allow a repeat
    logger.warning("All topics recently used - allowing repeat from static pool")
    return random.choice(DARK_TOPICS)


def get_topic_category(topic: str) -> str:
    """
    Categorizes a topic into Brain, Body, Mystery, or Health.
    
    Args:
        topic: Topic string
    
    Returns:
        Category name
    """
    topic_lower = topic.lower()
    
    # NOTE: Use word-boundary regex, not plain substring "in" checks.
    # Spanish adverbs commonly end in "-mente" (realmente, literalmente,
    # verdaderamente...), which would falsely match a bare "mente"
    # substring check and misclassify almost every topic as "Brain".
    brain_keywords = ['cerebro', 'mente', 'dormir', 'duermes', 'sueño', 'nervio', 'psico', 'memoria', 'pensamiento', 'conciencia', 'consciente']
    body_keywords = ['corazón', 'corazon', 'sangre', 'pulmon', 'pulmón', 'riñon', 'riñón', 'hueso', 'órgano', 'organo', 'músculo', 'musculo', 'vena', 'arteria']
    mystery_keywords = ['miedo', 'secreto', 'oscuro', 'misterio', 'oculto', 'desconocido', 'espeluznante', 'raro', 'aterrador']
    
    def _has_word(words):
        return any(re.search(r'\b' + re.escape(w) + r'\b', topic_lower) for w in words)
    
    if _has_word(brain_keywords):
        return "Brain"
    elif _has_word(mystery_keywords):
        return "Mystery"
    elif _has_word(body_keywords):
        return "Body"
    else:
        return "Body"  # Default


def get_seo_tags(topic: str, category: str = "Body") -> List[str]:
    """
    Returns YouTube-optimized tags (max 15).
    Priority order (most video-specific first, so with MAX_TAGS capping
    the list, unique/relevant tags always win over generic filler):
      1. Topic-specific keywords (unique per video)
      2. Category tags (Brain/Body/Mystery/Health - varies by topic)
      3. Related niche phrases
      4. Generic base/reach tags (same every video - filler only)
    
    Args:
        topic: Topic string
        category: Category name
    
    Returns:
        List of SEO tags
    """
    # 1. Topic-specific keywords FIRST - these make each video's tags unique
    topic_words = [
        w for w in topic.lower().split()
        if len(w) > 3 and w not in ['esto', 'este', 'esta', 'para', 'como', 'cuando', 'porque', 'tiene', 'tienen']
    ]
    tags = topic_words[:5]

    # 2. Category-specific tags (varies by Brain/Body/Mystery/Health)
    tags.extend(CATEGORY_TAGS.get(category, []))

    # 3. Related niche phrases
    related_phrases = [
        "cuerpo humano", "datos de ciencia", "ciencia oscura",
        "secretos del cuerpo", "datos misteriosos", "anatomia humana"
    ]
    tags.extend(related_phrases)

    # 4. Generic discovery tags LAST - only fill whatever slots remain
    tags.extend(BASE_TAGS)
    
    # Deduplicate and limit
    seen = set()
    result = []
    for tag in tags:
        clean = tag.strip().lower()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(tag)
        if len(result) >= MAX_TAGS:
            break
    
    return result


def generate_seo_tags(topic: str, category: str = "Body", title: str = "") -> List[str]:
    """
    Wrapper for get_seo_tags for compatibility.
    
    Args:
        topic: Topic string
        category: Category name
        title: Video title (optional)
    
    Returns:
        List of SEO tags
    """
    return get_seo_tags(topic, category)


def validate_script_for_medical_accuracy(script_data: Dict) -> Dict:
    """
    Validates that script doesn't contain medical advice.
    
    Args:
        script_data: Script dictionary
    
    Returns:
        Dict with 'valid' boolean and 'flags' list
    """
    # Extract voiceover text
    voiceover = script_data.get('voiceover', '')
    if not voiceover:
        voiceover = ' '.join([
            s.get('caption', '') 
            for s in script_data.get('scenes', []) 
            if isinstance(s, dict)
        ])
    
    # Check for red flags
    lowered = voiceover.lower()
    flags = [
        phrase for phrase in _MEDICAL_ADVICE_RED_FLAGS 
        if phrase in lowered
    ]
    
    return {
        "valid": len(flags) == 0,
        "flags": flags,
        "has_red_flags": len(flags) > 0
    }


def auto_add_disclaimer(script_data: Dict) -> Dict:
    """
    Adds medical disclaimer to script.
    
    Args:
        script_data: Script dictionary
    
    Returns:
        Modified script dictionary
    """
    disclaimer = "Este video es solo para fines educativos/de entretenimiento y no es un consejo médico. Consulta a un médico si tienes alguna preocupación de salud."
    
    # Add to CTA
    script_data['cta'] = (
        script_data.get('cta', '') + " " + disclaimer
    ).strip()
    
    # Add to description
    if 'description' in script_data:
        script_data['description'] = (
            script_data['description'] + " " + disclaimer
        ).strip()
    
    # Add flag
    script_data['disclaimer_added'] = True
    
    logger.info("Added medical disclaimer to script")
    return script_data


_EMOJI_PATTERN = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]+\\s*"
)


# Emoji chosen by matching actual topic keywords (most specific first),
# not just a generic per-category icon - and placed at the END of the
# title, not the start, so the keyword text leads (better for YouTube
# search matching / SEO than a leading emoji).
_TOPIC_EMOJI_MAP = [
    (['hueso', 'huesos', 'esqueleto'], '🦴'),
    (['pierna', 'piernas', 'rodilla', 'rodillas'], '🦵'),
    (['oreja', 'orejas', 'oído', 'oido', 'oidos', 'oídos', 'escuchar', 'sonido'], '👂'),
    (['corazón', 'corazon', 'sangre', 'pulso', 'latido', 'latidos'], '🫀'),
    (['inmune', 'microbioma', 'bacteria', 'germen', 'germenes', 'gérmenes', 'virus'], '🦠'),
    (['huella', 'huellas', 'dedo', 'dedos'], '🫆'),
    (['frío', 'frio', 'escalofrío', 'escalofrio', 'escalofríos', 'temperatura', 'fiebre'], '🥶'),
    (['ojo', 'ojos', 'ver', 'vista', 'mirar', 'punto ciego'], '👁️'),
    (['músculo', 'musculo', 'músculos', 'musculos', 'fuerza', 'ejercicio'], '💪'),
    (['sueño', 'dormir', 'duermes', 'noche', 'pesadilla', 'pesadillas'], '😴'),
    (['cerebro', 'mente', 'memoria', 'pensamiento'], '🧠'),
]


def _pick_topic_emoji(topic: str) -> str:
    """Pick the most relevant emoji for a topic from the approved emoji
    set, based on keyword match. Falls back to a category default."""
    topic_lower = topic.lower()
    for keywords, emoji in _TOPIC_EMOJI_MAP:
        if any(re.search(r'\b' + re.escape(kw) + r'\b', topic_lower) for kw in keywords):
            return emoji
    
    # Fallback by category if no specific keyword matched
    category = get_topic_category(topic)
    return {"Brain": "🧠", "Body": "🫀", "Mystery": "👁️", "Health": "🦠"}.get(category, "🫀")


def _make_seo_title(title: str, topic: str) -> str:
    """
    Enhances title for SEO while keeping under 55 chars.
    
    Args:
        title: Original title
        topic: Topic string
    
    Returns:
        SEO-optimized title
    """
    # Strip any emoji the LLM may have already put at the start of the
    # title - otherwise we'd stack a second emoji on top of it below.
    clean_title = _EMOJI_PATTERN.sub('', title, count=1).strip()
    
    # If title already has power words, keep it (already punchy, skip emoji)
    power_words = ["secreto", "nadie", "nunca", "en realidad", "oscuro", "aterrador",
                   "real", "oculto", "cuidado", "impactante", "dato", "verdad"]
    if any(pw in clean_title.lower() for pw in power_words):
        return clean_title[:MAX_TITLE_LENGTH]
    
    emoji = _pick_topic_emoji(topic)
    
    # Emoji goes at the END - keyword text leads for search matching
    enhanced = f"{clean_title} {emoji}"
    if len(enhanced) <= MAX_TITLE_LENGTH:
        return enhanced
    
    return clean_title[:MAX_TITLE_LENGTH]


# ============================================
# 12. UTILITY FUNCTIONS
# ============================================

def get_random_hook(topic: Optional[str] = None) -> str:
    """
    Get a random hook formula, optionally with topic.
    
    Args:
        topic: Topic to insert into hook (optional)
    
    Returns:
        Hook string
    """
    hook = random.choice(HOOK_FORMULAS)
    if topic and "{topic}" in hook:
        hook = hook.format(topic=topic)
    return hook


def get_random_pain_point() -> str:
    """Get a random pain point."""
    return random.choice(PAIN_POINTS)


def get_random_cta() -> str:
    """Get a random CTA."""
    return random.choice(CTAS)


def get_category_tags(category: str) -> List[str]:
    """Get tags for a specific category."""
    return CATEGORY_TAGS.get(category, CATEGORY_TAGS["Body"])


def get_scene_count() -> int:
    """Get the optimal number of scenes for retention."""
    return SCENES_PER_SCRIPT

# ============================================
# 13. RETENTION ANALYSIS FUNCTIONS
# ============================================

def analyze_retention_potential(script_data: Dict) -> Dict:
    """
    Analyzes script for retention potential.
    
    Returns:
        Dict with retention scores and suggestions
    """
    scenes = script_data.get('scenes', [])
    score = 0
    suggestions = []
    
    # Check scene count
    if len(scenes) == SCENES_PER_SCRIPT:
        score += 20
    else:
        suggestions.append(f"Optimal scene count is {SCENES_PER_SCRIPT}, currently {len(scenes)}")
    
    # Check for cliffhangers
    cliffhanger_count = 0
    for scene in scenes:
        caption = scene.get('caption', '')
        if any(word in caption.lower() for word in ['...', 'pero', 'sin embargo', 'aún', 'aun', 'todavía', 'todavia', 'aunque']):
            cliffhanger_count += 1
    
    cliffhanger_ratio = cliffhanger_count / len(scenes) if scenes else 0
    if cliffhanger_ratio >= 0.7:
        score += 30
    else:
        suggestions.append(f"Only {cliffhanger_ratio:.0%} scenes have cliffhangers - aim for 70%+")
    
    # Check "TÚ" language (Spanish personal address)
    you_count = 0
    for scene in scenes:
        caption = scene.get('caption', '')
        you_count += caption.lower().count('tú') + caption.lower().count('tu ') + caption.lower().count('te ')
    
    if you_count >= len(scenes) * 2:
        score += 25
    else:
        suggestions.append("Use more 'YOU' language for personal connection")
    
    # Check visual quality
    visual_quality = 0
    for scene in scenes:
        visual = scene.get('visual', '')
        if any(word in visual.lower() for word in ['cinematic', 'macro', 'close', 'dark', 'dramatic']):
            visual_quality += 1
    
    if visual_quality >= len(scenes) * 0.6:
        score += 25
    else:
        suggestions.append("Make visuals more CINEMATIC and DYNAMIC")
    
    return {
        'retention_score': min(100, score),
        'suggestions': suggestions,
        'cliffhanger_ratio': cliffhanger_ratio,
        'you_count': you_count,
        'visual_quality': visual_quality / len(scenes) if scenes else 0
    }

# ============================================
# 14. MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    # Test functionality
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("RETENTION-OPTIMIZED NICHE STRATEGY TEST")
    print("="*60)
    print()
    
    # Test topic selection
    print("1. Topic Selection:")
    for i in range(3):
        topic = get_random_topic()
        print(f"   - {topic}")
    print()
    
    # Test categorization
    test_topics = [
        "Your Brain Lies to You",
        "Your Heart Has Its Own Brain",
        "Why Fear Has a Physical Smell"
    ]
    print("2. Topic Categorization:")
    for topic in test_topics:
        category = get_topic_category(topic)
        print(f"   {topic} → {category}")
    print()
    
    # Test prompt generation
    print("3. Retention-Optimized Prompt Generation:")
    topic = "Why Your Brain Lies to You"
    prompt = get_script_prompt_for_niche(topic)
    print(f"   Generated prompt ({len(prompt)} chars)")
    print(f"   First 200 chars: {prompt[:200]}...")
    print()
    
    # Test transition hooks
    print("4. Transition Hooks:")
    transitions = get_transition_hooks(3)
    for hook in transitions:
        print(f"   - {hook}")
    print()
    
    # Test SEO tags
    print("5. SEO Tags:")
    tags = get_seo_tags("Brain Secrets", "Brain")
    print(f"   Tags: {', '.join(tags[:5])}...")
    print()
    
    # Test medical validation
    print("6. Medical Validation:")
    script = {
        "voiceover": "This can help diagnose your condition",
        "scenes": [{"caption": "Test caption"}]
    }
    result = validate_script_for_medical_accuracy(script)
    print(f"   Valid: {result['valid']}")
    print(f"   Flags: {result['flags']}")
    print()
    
    print("="*60)
    print("✅ RETENTION-OPTIMIZED MODULE READY!")
    print("="*60)
