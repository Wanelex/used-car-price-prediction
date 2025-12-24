import type { Translations } from './en';

export const tr: Translations = {
  // Common
  common: {
    loading: 'Yükleniyor...',
    error: 'Hata',
    yes: 'Evet',
    no: 'Hayır',
    cancel: 'İptal',
    tryAgain: 'Tekrar Dene',
    na: 'Yok',
  },

  // Navigation & Header
  nav: {
    home: 'Ana Sayfa',
    history: 'Geçmiş',
    profile: 'Profil',
    logout: 'Çıkış',
    startNewAnalysis: 'Yeni Analiz Başlat',
    builtWith: '© 2025 CarVisor',
  },

  // Brand
  brand: {
    tagline: 'İlanın Ötesini Gör',
  },

  // Tab names
  tabs: {
    analysis: 'Analiz',
    listing: 'İlan',
    specs: 'Teknik',
    parts: 'Boyalı',
    htmlMetadata: 'HTML/Metadata',
  },

  // Login page
  login: {
    createAccount: 'Hesabınızı oluşturun',
    welcomeBack: 'Tekrar hoş geldiniz',
    continueWithGoogle: 'Google ile devam et',
    or: 'VEYA',
    fullName: 'Ad Soyad',
    emailAddress: 'E-posta adresi',
    password: 'Şifre',
    createAccountBtn: 'Hesap Oluştur',
    signIn: 'Giriş Yap',
    alreadyHaveAccount: 'Zaten hesabınız var mı?',
    dontHaveAccount: 'Hesabınız yok mu?',
    signUp: 'Kayıt Ol',
    processing: 'İşleniyor...',
    errors: {
      enterName: 'Lütfen adınızı girin',
      googleFailed: 'Google girişi başarısız oldu',
      authFailed: 'Kimlik doğrulama başarısız oldu',
    },
  },

  // Home page
  home: {
    analysisHistory: 'Analiz Geçmişi',
    previouslyAnalyzed: 'Daha önce analiz ettiğiniz araç ilanları',
    loadingListings: 'İlanlarınız yükleniyor...',
    errorLoading: 'İlanlar Yüklenirken Hata',
    pleaseLogin: 'İlanlarınızı görmek için lütfen giriş yapın',
    noListingsYet: 'Henüz İlan Yok',
    startAnalyzing: 'Araç ilanlarını analiz etmeye başlayın',
    filtersSort: 'Filtreler & Sıralama',
    sortOptions: {
      newestFirst: 'En Yeni',
      oldestFirst: 'En Eski',
      priceLowHigh: 'Fiyat: Düşükten Yükseğe',
      priceHighLow: 'Fiyat: Yüksekten Düşüğe',
      yearNewest: 'Yıl: En Yeni',
      yearOldest: 'Yıl: En Eski',
      mileageLowHigh: 'KM: Düşükten Yükseğe',
      mileageHighLow: 'KM: Yüksekten Düşüğe',
      scoreHighLow: 'Puan: Yüksekten Düşüğe',
      scoreLowHigh: 'Puan: Düşükten Yükseğe',
    },
    filters: {
      brand: 'Marka',
      brandPlaceholder: 'örn. BMW, Mercedes',
      minPrice: 'Min Fiyat (₺)',
      maxPrice: 'Max Fiyat (₺)',
      minYear: 'Min Yıl',
      maxYear: 'Max Yıl',
      minScore: 'Min Puan',
      scorePlaceholder: '0-100',
      clearAll: 'Filtreleri Temizle',
    },
    noMatch: 'Filtrelerinize uygun ilan bulunamadı. Kriterlerinizi değiştirmeyi deneyin.',
    showing: '{total} ilandan {count} tanesi gösteriliyor',
    labels: {
      year: 'Yıl:',
      km: 'KM:',
      fuel: 'Yakıt:',
      trans: 'Vites:',
      final: 'Final',
      quality: 'Kalite',
    },
  },

  // Profile page
  profile: {
    loadingProfile: 'Profil yükleniyor...',
    accountCreated: 'Hesap Oluşturulma',
    lastSignIn: 'Son Giriş',
    signInMethod: 'Giriş Yöntemi',
    emailVerified: 'E-posta Doğrulandı',
    providers: {
      google: 'Google',
      emailPassword: 'E-posta/Şifre',
      unknown: 'Bilinmiyor',
    },
    dangerZone: 'Tehlikeli Bölge',
    deleteWarning: 'Hesabınızı sildiğinizde geri dönüş yoktur. Lütfen emin olun.',
    deleteAccount: 'Hesabı Sil',
    deleteConfirm: 'Hesabınızı silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.',
    enterPassword: 'Onaylamak için şifrenizi girin:',
    yourPassword: 'Şifreniz',
    googleDeleteNote: 'Silme işlemini onaylamak için Google ile giriş yapmanız istenecektir.',
    deleting: 'Siliniyor...',
    user: 'Kullanıcı',
  },

  // Crawl form
  crawlForm: {
    urlAnalyzer: 'URL Analiz',
    enterUrl: 'Analiz etmek için bir URL girin',
    urlToAnalyze: 'Analiz Edilecek URL',
    placeholder: 'https://example.com',
    errors: {
      required: 'URL gereklidir',
      invalid: 'Geçersiz URL. Lütfen http:// veya https:// ile başlayan geçerli bir URL girin',
    },
    startAnalysis: 'Analizi Başlat',
    analyzing: 'Analiz ediliyor...',
  },

  // Loading state
  loadingState: {
    analysisInProgress: 'Analiz Devam Ediyor',
    analyzing: 'Analiz ediliyor:',
    elapsed: 'Geçen süre: {time}',
    tip: 'Web sitesine bağlı olarak bu işlem birkaç saniye sürebilir...',
  },

  // Error display
  errorDisplay: {
    analysisFailed: 'Analiz Başarısız',
  },

  // Result display - Analysis section
  analysis: {
    analyzing: 'Analiz yapılıyor...',
    analysisFailed: 'Analiz yapılamadı: {error}',
    statisticalHealthScore: 'İstatistiksel Sağlık Skoru',
    buyable: 'ALINABİLİR',
    notBuyable: 'ALINMAMALI',
    featureScores: 'Özellik Puanları',
    riskFactors: 'Risk Faktörleri',
    topFeatures: 'En Önemli Özellikler',
    mechanicalReliabilityScore: 'Mekanik Güvenilirlik Skoru',
    carComponents: 'Araç Bileşenleri',
    engineCode: 'Motor Kodu:',
    transmission: 'Şanzıman:',
    generation: 'Nesil:',
    expertAnalysis: 'Uzman Analizi',
    generalEvaluation: 'Genel Değerlendirme',
    engineReliability: 'Motor Güvenilirliği',
    transmissionReliability: 'Şanzıman Güvenilirliği',
    mileageEndurance: 'KM Dayanıklılık Kontrolü',
    expertRecommendation: 'Uzman Önerisi',
    scoreReasoning: 'Puan Açıklaması:',
    llmNotAvailable: 'LLM Analizi Mevcut Değil',
    mechanicalAnalysisUnavailable: 'Mekanik güvenilirlik analizi şu anda kullanılamıyor. Lütfen istatistiksel skoru inceleyin.',
    apiKeyMissing: 'OpenAI API anahtarı yapılandırılmamış veya araç bilgileri eksik olabilir.',
    damagePaintScore: 'Hasar/Boya Skoru',
    summary: 'Özet',
    verdict: 'Değerlendirme',
    partDetails: 'Parça Detayları ({points} puan düşüldü)',
    pristineCondition: 'Kusursuz Durum',
    noPaintedParts: 'Bu araçta boyalı, lokal boyalı veya değişen parça bulunmamaktadır.',
    damageScoreUnavailable: 'Hasar Skoru Hesaplanamadı',
    noPaintedPartsInfo: 'Boyalı/değişen parça bilgisi mevcut değil.',
    riskLevels: {
      minimal: 'Minimal Risk - Mükemmel Durum',
      veryLow: 'Çok Düşük Risk - İyi Durum',
      low: 'Düşük Risk - Kabul Edilebilir',
      medium: 'Orta Risk - Dikkatli İnceleme Önerilir',
      high: 'Yüksek Risk - Ciddi Endişeler Var',
    },
    mechanicalLevels: {
      legendary: 'Efsanevi Güvenilirlik',
      high: 'Yüksek Güvenilirlik',
      medium: 'Orta Güvenilirlik',
      low: 'Düşük Güvenilirlik - Dikkat',
      risk: 'Mekanik Risk Yüksek',
    },
    crashVerdicts: {
      excellent: 'MÜKEMMEL',
      good: 'İYİ',
      caution: 'DİKKAT',
      danger: 'TEHLİKE',
      notBuyable: 'ALINMAMALI',
    },
    featureLabels: {
      carAge: 'Araç Yaşı',
      annualMileage: 'Yıllık KM',
      totalMileage: 'Toplam KM',
      modelYear: 'Model Yılı',
      enginePower: 'Motor Gücü',
      engineVolume: 'Motor Hacmi',
    },
    componentScores: {
      statistical: 'İstatistiksel',
      mechanical: 'Mekanik',
      crash: 'Hasar',
    },
    conditionLabels: {
      changed: 'Değişen',
      painted: 'Boyalı',
      localPainted: 'Lokal Boyalı',
    },
    // Identity mappings for Turkish (text stays the same)
    crashScoreTranslations: {} as Record<string, string>,
  },

  // Result display - Listing section
  listing: {
    listingNo: 'İlan No',
    listingDate: 'İlan Tarihi',
    price: 'Fiyat',
    brand: 'Marka',
    series: 'Seri',
    model: 'Model',
    year: 'Yıl',
    fuelType: 'Yakıt Tipi',
    transmission: 'Vites',
    vehicleCondition: 'Araç Durumu',
    mileage: 'KM',
    bodyType: 'Kasa Tipi',
    enginePower: 'Motor Gücü',
    engineVolume: 'Motor Hacmi',
    drivetrain: 'Çekiş',
    color: 'Renk',
    warranty: 'Garanti',
    severelyDamaged: 'Ağır Hasar Kayıtlı',
    plateNationality: 'Plaka / Uyruk',
    sellerType: 'Kimden',
    tradeIn: 'Takas',
    location: 'Konum',
  },

  // Result display - Specs section
  specs: {
    technicalSpecs: 'Teknik Özellikler',
    noTechnicalSpecs: 'Teknik özellik bilgisi bulunamadı.',
    equipmentFeatures: 'Donanım Özellikleri',
    noEquipment: 'Donanım bilgisi bulunamadı.',
  },

  // Result display - Parts section
  parts: {
    paintedAndChanged: 'Boyalı ve Değişen Parçalar',
    paintedParts: 'Boyalı Parçalar',
    changedParts: 'Değişen Parçalar',
    locallyPainted: 'Lokal Boyalı Parçalar',
    noPaintedOrChanged: 'Boyalı veya değişen parça bulunmamaktadır.',
    noInfoAvailable: 'Boyalı veya değişen parça bilgisi bulunamadı.',
  },

  // Result display - HTML/Metadata section
  metadata: {
    metadata: 'Metadata',
    analysisInfo: 'Analiz Bilgisi',
    url: 'URL',
    duration: 'Süre',
    captchaSolved: 'CAPTCHA Çözüldü',
    dataQuality: 'Veri Kalitesi',
    debugRawData: 'Debug: Ham İlan Verisi',
    noMetadata: 'Metadata bulunamadı',
  },
};
