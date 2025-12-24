import { useLanguage, type Language } from '../i18n';
import './LanguageToggle.css';

export default function LanguageToggle() {
  const { language, setLanguage } = useLanguage();

  const toggleLanguage = () => {
    const newLang: Language = language === 'en' ? 'tr' : 'en';
    setLanguage(newLang);
  };

  return (
    <button
      className="language-toggle"
      onClick={toggleLanguage}
      title={language === 'en' ? 'Türkçe\'ye geç' : 'Switch to English'}
    >
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="2" y1="12" x2="22" y2="12" />
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
      </svg>
      <span className="language-code">{language.toUpperCase()}</span>
    </button>
  );
}
