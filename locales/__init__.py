import yaml

async def get_translation(language, key):
    """
    Функція для витягу тексту (вона не потрібна якщо ви використувуєте locale мідлварь)
    """
    try:
        with open(f'locales/{language}.yaml', 'r') as f:
            translations = yaml.safe_load(f)
        
        if key in translations:
            # Якщо переклад є словником (наприклад, content)
            if isinstance(translations[key], dict):
                return translations[key]
            # Якщо переклад є простим рядком (наприклад, faq)
            return translations[key]
        else:
            raise KeyError(f'Translation key "{key}" not found')
    
    except FileNotFoundError:
        raise ValueError(f'Language file for {language} not found')
    except yaml.YAMLError:
        raise RuntimeError('Error parsing YAML file')
