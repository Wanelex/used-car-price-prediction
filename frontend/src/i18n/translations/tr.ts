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
    // Identity mappings for Turkish (text stays the same - Turkish source to Turkish display)
    crashScoreTranslations: {
      // Verdicts
      'MUKEMMEL - Hasar gecmisi yok veya minimumdur. Alinabilir.': 'MÜKEMMEL - Hasar geçmişi yok veya minimumdur. Alınabilir.',
      'IYI - Kucuk kozmetik onarimlar var. Alinabilir.': 'İYİ - Küçük kozmetik onarımlar var. Alınabilir.',
      'DIKKAT - Belirgin hasar gecmisi var. Detayli inceleme sart.': 'DİKKAT - Belirgin hasar geçmişi var. Detaylı inceleme şart.',
      'TEHLIKE - Ciddi hasar gecmisi. Alinmasi onerilmez.': 'TEHLİKE - Ciddi hasar geçmişi. Alınması önerilmez.',
      'KESINLIKLE ALINMAMALI - Arac agir hasarli. Guvenlik riski var.': 'KESİNLİKLE ALINMAMALI - Araç ağır hasarlı. Güvenlik riski var.',
      // Summaries
      'Arac neredeyse kusursuz durumda. Boyali veya degisen parca yok ya da cok az.': 'Araç neredeyse kusursuz durumda. Boyalı veya değişen parça yok ya da çok az.',
      'Aracta kucuk kozmetik onarimlar mevcut ancak yapisal bir sorun gorulmuyor.': 'Araçta küçük kozmetik onarımlar mevcut ancak yapısal bir sorun görülmüyor.',
      'Aracta belirgin onarim izleri var. Profesyonel ekspertiz onerilir.': 'Araçta belirgin onarım izleri var. Profesyonel ekspertiz önerilir.',
      'Arac ciddi hasar gecmisine sahip. Yapisal problemler olabilir.': 'Araç ciddi hasar geçmişine sahip. Yapısal problemler olabilir.',
      'Arac cok agir hasar gecmisine sahip. Guvenlik acisindan tehlikeli olabilir.': 'Araç çok ağır hasar geçmişine sahip. Güvenlik açısından tehlikeli olabilir.',
      // Risk levels
      'Minimal Risk': 'Minimal Risk',
      'Dusuk Risk': 'Düşük Risk',
      'Orta Risk': 'Orta Risk',
      'Yuksek Risk': 'Yüksek Risk',
      'Cok Yuksek Risk': 'Çok Yüksek Risk',
      'Bilinmiyor': 'Bilinmiyor',
      // Part advices
      'Kritik yapisal risk. Takla veya agir kaza ihtimali yuksek. Satin alinmasi kesinlikle onerilmez.': 'Kritik yapısal risk. Takla veya ağır kaza ihtimali yüksek. Satın alınması kesinlikle önerilmez.',
      'Yuksek risk. Takla veya agir cisim darbesi olabilir. Macun kalinligi ve ic direk hasarini kontrol edin.': 'Yüksek risk. Takla veya ağır cisim darbesi olabilir. Macun kalınlığı ve iç direk hasarını kontrol edin.',
      'Supheli. Kozmetik (kus piskligi vb.) veya anten onarimi olabilir, ancak dikkatli inceleme gerektirir.': 'Şüpheli. Kozmetik (kuş pisliği vb.) veya anten onarımı olabilir, ancak dikkatli inceleme gerektirir.',
      'Buyuk on carpisma ihtimali yuksek. Sasi, podya ve havayastiklarini dikkatle kontrol edin. Kaza fotograflari dogrulanmadikca onerilmez.': 'Büyük ön çarpışma ihtimali yüksek. Şasi, podya ve hava yastıklarını dikkatle kontrol edin. Kaza fotoğrafları doğrulanmadıkça önerilmez.',
      'Muhtemelen on darbe veya tas cizigidir. On panel ve radyator destek sacinda orijinal etiketleri kontrol edin.': 'Muhtemelen ön darbe veya taş çiziğidir. Ön panel ve radyatör destek sacında orijinal etiketleri kontrol edin.',
      'Kucuk kozmetik rotuş. Genellikle kabul edilebilir, renk uyumunu kontrol edin.': 'Küçük kozmetik rötuş. Genellikle kabul edilebilir, renk uyumunu kontrol edin.',
      'Onemli arkadan carpismayi gosterir. Bagaj havuzu ve arka sasi panelinde kaynak izlerini kontrol edin.': 'Önemli arkadan çarpışmayı gösterir. Bagaj havuzu ve arka şasi panelinde kaynak izlerini kontrol edin.',
      'Orta seviye arka darbe. Ic yapi saglam ise genellikle kabul edilebilir.': 'Orta seviye arka darbe. İç yapı sağlam ise genellikle kabul edilebilir.',
      'Kucuk kozmetik onarim. Arac degerine etkisi dusuk.': 'Küçük kozmetik onarım. Araç değerine etkisi düşük.',
      'Yapisal mudahale kesme ve kaynak gerektirmis. Yuksek deger kaybi. Ic camurluk boslugunu dikkatle kontrol edin.': 'Yapısal müdahale kesme ve kaynak gerektirmiş. Yüksek değer kaybı. İç çamurluk boşluğunu dikkatle kontrol edin.',
      'Yaygin surtunen bolge. Derin macun kullanilmamissa kabul edilebilir.': 'Yaygın sürtünen bölge. Derin macun kullanılmamışsa kabul edilebilir.',
      'Kucuk suruntme onarimi. Cok yaygin ve genellikle kabul edilebilir.': 'Küçük sürtünme onarımı. Çok yaygın ve genellikle kabul edilebilir.',
      'Parcalar civatayla takilir, ancak degisim sert yan darbe anlamina gelir. Direkleri ve mentesteleri kontrol edin.': 'Parçalar civatayla takılır, ancak değişim sert yan darbe anlamına gelir. Direkleri ve menteşeleri kontrol edin.',
      'Kozmetik cizik veya gocuk onarimi. Sehir trafiginde yaygin. Mekanik sagliga etkisi minimal.': 'Kozmetik çizik veya göçük onarımı. Şehir trafiğinde yaygın. Mekanik sağlığa etkisi minimal.',
      'Cok kucuk rotuş. Degere etkisi ihmal edilebilir.': 'Çok küçük rötuş. Değere etkisi ihmal edilebilir.',
      'Plastik parca. Degisim yaygindir ve daha temiz bir gorunum saglar. Sensorleri ve sis farlarini kontrol edin.': 'Plastik parça. Değişim yaygındır ve daha temiz bir görünüm sağlar. Sensörleri ve sis farlarını kontrol edin.',
      'Plastik parca. Estetik icin boyanir. Degere olumsuz etkisi yoktur.': 'Plastik parça. Estetik için boyanır. Değere olumsuz etkisi yoktur.',
      'Plastik parca. Onemsiz kozmetik onarim.': 'Plastik parça. Önemsiz kozmetik onarım.',
      // No parts info messages
      'Boyali veya degisen parca bilgisi mevcut degil. Arac orijinal durumda kabul edildi.': 'Boyalı veya değişen parça bilgisi mevcut değil. Araç orijinal durumda kabul edildi.',
      'Parca bilgisi yok - Orijinal kabul edildi': 'Parça bilgisi yok - Orijinal kabul edildi',
    },
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
