export const en = {
  // Common
  common: {
    loading: 'Loading...',
    error: 'Error',
    yes: 'Yes',
    no: 'No',
    cancel: 'Cancel',
    tryAgain: 'Try Again',
    na: 'N/A',
  },

  // Navigation & Header
  nav: {
    home: 'Home',
    history: 'History',
    profile: 'Profile',
    logout: 'Logout',
    startNewAnalysis: 'Start New Analysis',
    builtWith: '© 2025 CarVisor',
  },

  // Brand
  brand: {
    tagline: 'See Beyond the Listing',
  },

  // Tab names
  tabs: {
    analysis: 'Analysis',
    listing: 'Listing',
    specs: 'Specs',
    parts: 'Parts',
    htmlMetadata: 'HTML/Metadata',
  },

  // Login page
  login: {
    createAccount: 'Create your account',
    welcomeBack: 'Welcome back',
    continueWithGoogle: 'Continue with Google',
    or: 'OR',
    fullName: 'Full Name',
    emailAddress: 'Email address',
    password: 'Password',
    createAccountBtn: 'Create Account',
    signIn: 'Sign In',
    alreadyHaveAccount: 'Already have an account?',
    dontHaveAccount: "Don't have an account?",
    signUp: 'Sign Up',
    processing: 'Processing...',
    errors: {
      enterName: 'Please enter your name',
      googleFailed: 'Google sign-in failed',
      authFailed: 'Authentication failed',
    },
  },

  // Home page
  home: {
    analysisHistory: 'Analysis History',
    previouslyAnalyzed: 'Your previously analyzed car listings',
    loadingListings: 'Loading your listings...',
    errorLoading: 'Error Loading Listings',
    pleaseLogin: 'Please log in to view your listings',
    noListingsYet: 'No Listings Yet',
    startAnalyzing: 'Start analyzing car listings to see them here',
    filtersSort: 'Filters & Sort',
    sortOptions: {
      newestFirst: 'Newest First',
      oldestFirst: 'Oldest First',
      priceLowHigh: 'Price: Low to High',
      priceHighLow: 'Price: High to Low',
      yearNewest: 'Year: Newest',
      yearOldest: 'Year: Oldest',
      mileageLowHigh: 'Mileage: Low to High',
      mileageHighLow: 'Mileage: High to Low',
      scoreHighLow: 'Score: High to Low',
      scoreLowHigh: 'Score: Low to High',
    },
    filters: {
      brand: 'Brand',
      brandPlaceholder: 'e.g., BMW, Mercedes',
      minPrice: 'Min Price (₺)',
      maxPrice: 'Max Price (₺)',
      minYear: 'Min Year',
      maxYear: 'Max Year',
      minScore: 'Min Score',
      scorePlaceholder: '0-100',
      clearAll: 'Clear All Filters',
    },
    noMatch: 'No listings match your filters. Try adjusting your criteria.',
    showing: 'Showing {count} of {total} listings',
    labels: {
      year: 'Year:',
      km: 'KM:',
      fuel: 'Fuel:',
      trans: 'Trans:',
      final: 'Final',
      quality: 'Quality',
    },
  },

  // Profile page
  profile: {
    loadingProfile: 'Loading profile...',
    accountCreated: 'Account Created',
    lastSignIn: 'Last Sign In',
    signInMethod: 'Sign-in Method',
    emailVerified: 'Email Verified',
    providers: {
      google: 'Google',
      emailPassword: 'Email/Password',
      unknown: 'Unknown',
    },
    dangerZone: 'Danger Zone',
    deleteWarning: 'Once you delete your account, there is no going back. Please be certain.',
    deleteAccount: 'Delete Account',
    deleteConfirm: 'Are you sure you want to delete your account? This action cannot be undone.',
    enterPassword: 'Enter your password to confirm:',
    yourPassword: 'Your password',
    googleDeleteNote: 'You will be prompted to sign in with Google to confirm deletion.',
    deleting: 'Deleting...',
    user: 'User',
  },

  // Crawl form
  crawlForm: {
    urlAnalyzer: 'URL Analyzer',
    enterUrl: 'Enter a URL to analyze and extract its content',
    urlToAnalyze: 'URL to Analyze',
    placeholder: 'https://example.com',
    errors: {
      required: 'URL is required',
      invalid: 'Invalid URL. Please enter a valid URL starting with http:// or https://',
    },
    startAnalysis: 'Start Analysis',
    analyzing: 'Analyzing...',
  },

  // Loading state
  loadingState: {
    analysisInProgress: 'Analysis in Progress',
    analyzing: 'Analyzing:',
    elapsed: 'Elapsed: {time}',
    tip: 'This may take a few seconds depending on the website...',
  },

  // Error display
  errorDisplay: {
    analysisFailed: 'Analysis Failed',
  },

  // Result display - Analysis section
  analysis: {
    analyzing: 'Analyzing...',
    analysisFailed: 'Analysis failed: {error}',
    statisticalHealthScore: 'Statistical Health Score',
    buyable: 'BUYABLE',
    notBuyable: 'NOT BUYABLE',
    featureScores: 'Feature Scores',
    riskFactors: 'Risk Factors',
    topFeatures: 'Top Contributing Features',
    mechanicalReliabilityScore: 'Mechanical Reliability Score',
    carComponents: 'Car Components',
    engineCode: 'Engine Code:',
    transmission: 'Transmission:',
    generation: 'Generation:',
    expertAnalysis: 'Expert Analysis',
    generalEvaluation: 'General Evaluation',
    engineReliability: 'Engine Reliability',
    transmissionReliability: 'Transmission Reliability',
    mileageEndurance: 'Mileage Endurance Check',
    expertRecommendation: 'Expert Recommendation',
    scoreReasoning: 'Score Reasoning:',
    llmNotAvailable: 'LLM Analysis Not Available',
    mechanicalAnalysisUnavailable: 'Mechanical reliability analysis is currently unavailable. Please review the statistical score.',
    apiKeyMissing: 'OpenAI API key may not be configured or vehicle information is missing.',
    damagePaintScore: 'Damage/Paint Score',
    summary: 'Summary',
    verdict: 'Verdict',
    partDetails: 'Part Details ({points} points deducted)',
    pristineCondition: 'Pristine Condition',
    noPaintedParts: 'This vehicle has no painted, locally painted, or changed parts.',
    damageScoreUnavailable: 'Damage Score Unavailable',
    noPaintedPartsInfo: 'Painted/changed parts information is not available.',
    riskLevels: {
      minimal: 'Minimal Risk - Excellent Condition',
      veryLow: 'Very Low Risk - Good Condition',
      low: 'Low Risk - Acceptable',
      medium: 'Medium Risk - Careful Review Recommended',
      high: 'High Risk - Serious Concerns',
    },
    mechanicalLevels: {
      legendary: 'Legendary Reliability',
      high: 'High Reliability',
      medium: 'Medium Reliability',
      low: 'Low Reliability - Caution',
      risk: 'High Mechanical Risk',
    },
    crashVerdicts: {
      excellent: 'EXCELLENT',
      good: 'GOOD',
      caution: 'CAUTION',
      danger: 'DANGER',
      notBuyable: 'NOT BUYABLE',
    },
    featureLabels: {
      carAge: 'Car Age',
      annualMileage: 'Annual Mileage',
      totalMileage: 'Total Mileage',
      modelYear: 'Model Year',
      enginePower: 'Engine Power',
      engineVolume: 'Engine Volume',
    },
    componentScores: {
      statistical: 'Statistical',
      mechanical: 'Mechanical',
      crash: 'Damage',
    },
    conditionLabels: {
      changed: 'Changed',
      painted: 'Painted',
      localPainted: 'Locally Painted',
    },
    // Turkish to English crash score translations
    crashScoreTranslations: {
      // Verdicts
      'MUKEMMEL - Hasar gecmisi yok veya minimumdur. Alinabilir.': 'EXCELLENT - No or minimal damage history. Safe to buy.',
      'IYI - Kucuk kozmetik onarimlar var. Alinabilir.': 'GOOD - Minor cosmetic repairs present. Safe to buy.',
      'DIKKAT - Belirgin hasar gecmisi var. Detayli inceleme sart.': 'CAUTION - Noticeable damage history. Detailed inspection required.',
      'TEHLIKE - Ciddi hasar gecmisi. Alinmasi onerilmez.': 'DANGER - Serious damage history. Purchase not recommended.',
      'KESINLIKLE ALINMAMALI - Arac agir hasarli. Guvenlik riski var.': 'DO NOT BUY - Vehicle heavily damaged. Safety risk present.',
      // Summaries
      'Arac neredeyse kusursuz durumda. Boyali veya degisen parca yok ya da cok az.': 'Vehicle is in near-pristine condition. No or very few painted or changed parts.',
      'Aracta kucuk kozmetik onarimlar mevcut ancak yapisal bir sorun gorulmuyor.': 'Vehicle has minor cosmetic repairs but no structural issues detected.',
      'Aracta belirgin onarim izleri var. Profesyonel ekspertiz onerilir.': 'Vehicle has noticeable repair signs. Professional inspection recommended.',
      'Arac ciddi hasar gecmisine sahip. Yapisal problemler olabilir.': 'Vehicle has serious damage history. Structural problems may exist.',
      'Arac cok agir hasar gecmisine sahip. Guvenlik acisindan tehlikeli olabilir.': 'Vehicle has very severe damage history. May be dangerous for safety.',
      // Risk levels
      'Minimal Risk': 'Minimal Risk',
      'Dusuk Risk': 'Low Risk',
      'Orta Risk': 'Medium Risk',
      'Yuksek Risk': 'High Risk',
      'Cok Yuksek Risk': 'Very High Risk',
      'Bilinmiyor': 'Unknown',
      // Part advices
      'Kritik yapisal risk. Takla veya agir kaza ihtimali yuksek. Satin alinmasi kesinlikle onerilmez.': 'Critical structural risk. High probability of rollover or severe accident. Purchase strongly not recommended.',
      'Yuksek risk. Takla veya agir cisim darbesi olabilir. Macun kalinligi ve ic direk hasarini kontrol edin.': 'High risk. Could indicate rollover or heavy object impact. Check filler thickness and inner pillar damage.',
      'Supheli. Kozmetik (kus piskligi vb.) veya anten onarimi olabilir, ancak dikkatli inceleme gerektirir.': 'Suspicious. Could be cosmetic (bird droppings etc.) or antenna repair, but requires careful inspection.',
      'Buyuk on carpisma ihtimali yuksek. Sasi, podya ve havayastiklarini dikkatle kontrol edin. Kaza fotograflari dogrulanmadikca onerilmez.': 'High probability of major front collision. Carefully check chassis, subframe, and airbags. Not recommended unless accident photos verified.',
      'Muhtemelen on darbe veya tas cizigidir. On panel ve radyator destek sacinda orijinal etiketleri kontrol edin.': 'Probably front impact or stone chip. Check front panel and radiator support for original labels.',
      'Kucuk kozmetik rotuş. Genellikle kabul edilebilir, renk uyumunu kontrol edin.': 'Small cosmetic touch-up. Generally acceptable, check color match.',
      'Onemli arkadan carpismayi gosterir. Bagaj havuzu ve arka sasi panelinde kaynak izlerini kontrol edin.': 'Indicates significant rear collision. Check trunk floor and rear chassis panel for weld marks.',
      'Orta seviye arka darbe. Ic yapi saglam ise genellikle kabul edilebilir.': 'Medium level rear impact. Generally acceptable if inner structure is intact.',
      'Kucuk kozmetik onarim. Arac degerine etkisi dusuk.': 'Small cosmetic repair. Low impact on vehicle value.',
      'Yapisal mudahale kesme ve kaynak gerektirmis. Yuksek deger kaybi. Ic camurluk boslugunu dikkatle kontrol edin.': 'Structural intervention required cutting and welding. High value loss. Carefully check inner fender cavity.',
      'Yaygin surtunen bolge. Derin macun kullanilmamissa kabul edilebilir.': 'Common rubbing area. Acceptable if no heavy filler used.',
      'Kucuk suruntme onarimi. Cok yaygin ve genellikle kabul edilebilir.': 'Small scuff repair. Very common and generally acceptable.',
      'Parcalar civatayla takilir, ancak degisim sert yan darbe anlamina gelir. Direkleri ve mentesteleri kontrol edin.': 'Parts are bolt-on, but replacement indicates hard side impact. Check pillars and hinges.',
      'Kozmetik cizik veya gocuk onarimi. Sehir trafiginde yaygin. Mekanik sagliga etkisi minimal.': 'Cosmetic scratch or dent repair. Common in city traffic. Minimal impact on mechanical health.',
      'Cok kucuk rotuş. Degere etkisi ihmal edilebilir.': 'Very small touch-up. Negligible impact on value.',
      'Plastik parca. Degisim yaygindir ve daha temiz bir gorunum saglar. Sensorleri ve sis farlarini kontrol edin.': 'Plastic part. Replacement is common and provides cleaner look. Check sensors and fog lights.',
      'Plastik parca. Estetik icin boyanir. Degere olumsuz etkisi yoktur.': 'Plastic part. Painted for aesthetics. No negative impact on value.',
      'Plastik parca. Onemsiz kozmetik onarim.': 'Plastic part. Insignificant cosmetic repair.',
      // No parts info messages
      'Boyali veya degisen parca bilgisi mevcut degil. Arac orijinal durumda kabul edildi.': 'No painted or changed parts information available. Vehicle assumed to be in original condition.',
      'Parca bilgisi yok - Orijinal kabul edildi': 'No parts info - Assumed original',
    },
  },

  // Result display - Listing section
  listing: {
    listingNo: 'Listing No',
    listingDate: 'Listing Date',
    price: 'Price',
    brand: 'Brand',
    series: 'Series',
    model: 'Model',
    year: 'Year',
    fuelType: 'Fuel Type',
    transmission: 'Transmission',
    vehicleCondition: 'Vehicle Condition',
    mileage: 'Mileage',
    bodyType: 'Body Type',
    enginePower: 'Engine Power',
    engineVolume: 'Engine Volume',
    drivetrain: 'Drivetrain',
    color: 'Color',
    warranty: 'Warranty',
    severelyDamaged: 'Severely Damaged',
    plateNationality: 'Plate / Nationality',
    sellerType: 'Seller Type',
    tradeIn: 'Trade-in',
    location: 'Location',
  },

  // Result display - Specs section
  specs: {
    technicalSpecs: 'Technical Specifications',
    noTechnicalSpecs: 'Technical specifications not found.',
    equipmentFeatures: 'Equipment Features',
    noEquipment: 'Equipment information not found.',
  },

  // Result display - Parts section
  parts: {
    paintedAndChanged: 'Painted and Changed Parts',
    paintedParts: 'Painted Parts',
    changedParts: 'Changed Parts',
    locallyPainted: 'Locally Painted Parts',
    noPaintedOrChanged: 'No painted or changed parts found.',
    noInfoAvailable: 'Painted or changed parts information not found.',
  },

  // Result display - HTML/Metadata section
  metadata: {
    metadata: 'Metadata',
    analysisInfo: 'Analysis Info',
    url: 'URL',
    duration: 'Duration',
    captchaSolved: 'CAPTCHA Solved',
    dataQuality: 'Data Quality',
    debugRawData: 'Debug: Raw Listing Data',
    noMetadata: 'Metadata not found',
  },
};

export type Translations = typeof en;
