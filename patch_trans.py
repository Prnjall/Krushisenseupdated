import re
import sys
import shutil
import os

if len(sys.argv) < 2:
    print("Usage: python patch_trans.py <path_to_CropDetailsPage.tsx>")
    sys.exit(1)

path = sys.argv[1]
if not os.path.exists(path):
    print(f"Error: File not found at {path}")
    sys.exit(1)

with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Imports
text = re.sub(
    r"import \{ getCropBySlug \} from '\.\./data/cropData';",
    "import { getCropBySlug } from '../data/cropData';\nimport { useTranslation } from '../contexts/LanguageContext';\nimport { cropTranslations } from './PredictCrop';",
    text
)

# 2. Add useTranslation and useEffect hooks
hook_addition = """  const { cropName } = useParams<{ cropName: string }>();
  const navigate = useNavigate();
  const { t, language, translateBatch } = useTranslation();

  const slug = cropName?.toLowerCase() || '';
  const crop = getCropBySlug(slug);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [slug]);

  useEffect(() => {
    if (language !== 'en' && crop) {
      translateBatch([
        crop.description,
        crop.season,
        crop.temperature,
        crop.soil,
        crop.climate,
        crop.note,
        crop.why,
        crop.water,
        crop.water_mm
      ]);
    }
  }, [language, crop, translateBatch]);"""

text = re.sub(
    r"  const \{ cropName \} = useParams.*?\}, \[slug\]\);",
    hook_addition,
    text,
    flags=re.DOTALL
)

# 3. Handle Top Nav
text = text.replace(
    "Back to Results",
    "{t(\"Back to Results\")}"
)

# 4. Handle Title format
title_original = """          <h1 className="font-headline font-bold text-lg tracking-tight text-black">
            {crop.name}
          </h1>"""
title_new = """          <h1 className="font-headline font-bold text-lg tracking-tight text-black flex items-center gap-2">
            {cropTranslations[slug]?.en || crop.name}
            {cropTranslations[slug] && (cropTranslations[slug].hi || cropTranslations[slug].mr) && (
              <span className="text-sm text-neutral-500 font-normal">
                {cropTranslations[slug].hi && `• ${cropTranslations[slug].hi}`}
                {cropTranslations[slug].mr && ` • ${cropTranslations[slug].mr}`}
              </span>
            )}
          </h1>"""
text = text.replace(title_original, title_new)

# 5. Handle Text nodes & labels
replacements = [
    ('About this Crop', '{t("About this Crop")}'),
    ('{crop.description}', '{t(crop.description)}'),
    ('Why this crop is<br />recommended', '{t("Why this crop is recommended")}'),
    ('{crop.why}', '{t(crop.why)}'),
    ('Cultivation Window', '{t("Cultivation Window")}'),
    ('{crop.season}', '{t(crop.season)}'),
    ('Temperature', '{t("Temperature")}'),
    ('{crop.temperature}', '{t(crop.temperature)}'),
    ('Soil Type', '{t("Soil Type")}'),
    ('{crop.soil}', '{t(crop.soil)}'),
    ('Climate', '{t("Climate")}'),
    ('{crop.climate}', '{t(crop.climate)}'),
    ('Water Requirement:', '{t("Water Requirement")}:'),
    ('Water Requirement', '{t("Water Requirement")}'),
    ('Approx:', '{t("Approx")}:'),
    ('{crop.water}', '{t(crop.water)}'),
    ('{crop.water_mm}', '{t(crop.water_mm)}'),
    ('{crop.note}', '{t(crop.note)}')
]

for old, new in replacements:
    text = text.replace(old, new)


# Backup original file
shutil.copy2(path, path + ".bak")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Successfully patched {path}. Original saved as .bak")
