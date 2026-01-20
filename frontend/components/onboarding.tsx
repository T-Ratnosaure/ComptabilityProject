"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, ArrowLeft, Briefcase, TrendingUp, Shield, Check } from "lucide-react"

// Profession profiles with default values
const PROFESSION_PROFILES = {
  dev_consultant: {
    label: "Développeur / Consultant IT",
    icon: "💻",
    defaults: {
      status: "micro_bnc",
      activity_type: "BNC",
      typical_ca: 80000,
      investment_capacity: 30000,
      risk_tolerance: "moderate",
      stable_income: true,
    },
    tips: [
      "Le passage en SASU peut être intéressant au-delà de 70k€ de CA",
      "Le PER est très avantageux avec un TMI à 30% ou plus",
      "Les frais de matériel et coworking sont déductibles en réel",
    ],
  },
  health_professional: {
    label: "Professionnel de santé",
    icon: "🏥",
    defaults: {
      status: "reel_bnc",
      activity_type: "BNC",
      typical_ca: 120000,
      investment_capacity: 50000,
      risk_tolerance: "conservative",
      stable_income: true,
    },
    tips: [
      "La SELARL peut réduire significativement votre imposition",
      "Les contrats Madelin sont déductibles pour la retraite et prévoyance",
      "La CARMF offre des options de rachat de trimestres",
    ],
  },
  creator: {
    label: "Créateur de contenu / Influenceur",
    icon: "🎬",
    defaults: {
      status: "micro_bic_service",
      activity_type: "BIC",
      typical_ca: 50000,
      investment_capacity: 20000,
      risk_tolerance: "moderate",
      stable_income: false,
    },
    tips: [
      "Les droits d'auteur peuvent être imposés séparément (plus avantageux)",
      "Le matériel vidéo/photo est amortissable en réel",
      "Une société à l'IS peut optimiser si revenus irréguliers",
    ],
  },
  liberal_other: {
    label: "Autre profession libérale",
    icon: "📋",
    defaults: {
      status: "micro_bnc",
      activity_type: "BNC",
      typical_ca: 60000,
      investment_capacity: 25000,
      risk_tolerance: "moderate",
      stable_income: true,
    },
    tips: [
      "Comparez micro-BNC vs réel selon vos charges réelles",
      "Le PER reste l'optimisation la plus simple et efficace",
      "Un expert-comptable peut identifier des charges oubliées",
    ],
  },
}

const CA_RANGES = [
  { value: 30000, label: "Moins de 40k€", description: "Micro-entreprise classique" },
  { value: 60000, label: "40k€ - 80k€", description: "Seuils micro à surveiller" },
  { value: 100000, label: "80k€ - 120k€", description: "Réel souvent plus avantageux" },
  { value: 150000, label: "Plus de 120k€", description: "Optimisations avancées possibles" },
]

const ACCOMPAGNEMENT_OPTIONS = [
  { value: "none", label: "Pas d'accompagnement", icon: "🙋" },
  { value: "accountant", label: "Expert-comptable", icon: "📊" },
  { value: "advisor", label: "Conseiller en gestion de patrimoine", icon: "💼" },
]

interface OnboardingProps {
  onComplete: (data: {
    profession: string
    ca: number
    accompagnement: string
    defaults: typeof PROFESSION_PROFILES.dev_consultant.defaults
    tips: string[]
  }) => void
  onSkip: () => void
}

export function Onboarding({ onComplete, onSkip }: OnboardingProps) {
  const [step, setStep] = useState(1)
  const [profession, setProfession] = useState<string | null>(null)
  const [ca, setCa] = useState<number | null>(null)
  const [accompagnement, setAccompagnement] = useState<string | null>(null)

  const totalSteps = 3

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1)
    } else if (profession && ca !== null && accompagnement) {
      const profile = PROFESSION_PROFILES[profession as keyof typeof PROFESSION_PROFILES]
      onComplete({
        profession,
        ca,
        accompagnement,
        defaults: {
          ...profile.defaults,
          typical_ca: ca,
        },
        tips: profile.tips,
      })
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  const canProceed = () => {
    switch (step) {
      case 1:
        return profession !== null
      case 2:
        return ca !== null
      case 3:
        return accompagnement !== null
      default:
        return false
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 to-white flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="flex justify-center gap-2 mb-4">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`w-3 h-3 rounded-full transition-colors ${
                  s === step
                    ? "bg-violet-600"
                    : s < step
                    ? "bg-violet-400"
                    : "bg-slate-200"
                }`}
              />
            ))}
          </div>
          <CardTitle className="text-2xl">
            {step === 1 && "Quelle est votre activité ?"}
            {step === 2 && "Quel est votre chiffre d'affaires annuel ?"}
            {step === 3 && "Êtes-vous accompagné ?"}
          </CardTitle>
          <CardDescription>
            {step === 1 && "Nous adapterons les recommandations à votre secteur"}
            {step === 2 && "Pour calibrer les optimisations pertinentes"}
            {step === 3 && "Pour éviter les recommandations redondantes"}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Step 1: Profession */}
          {step === 1 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(PROFESSION_PROFILES).map(([key, profile]) => (
                <button
                  key={key}
                  onClick={() => setProfession(key)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    profession === key
                      ? "border-violet-600 bg-violet-50"
                      : "border-slate-200 hover:border-violet-300"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{profile.icon}</span>
                    <div>
                      <p className="font-medium">{profile.label}</p>
                      <p className="text-sm text-slate-500">
                        {profile.defaults.status.replace("_", "-")}
                      </p>
                    </div>
                    {profession === key && (
                      <Check className="ml-auto h-5 w-5 text-violet-600" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Step 2: CA */}
          {step === 2 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {CA_RANGES.map((range) => (
                <button
                  key={range.value}
                  onClick={() => setCa(range.value)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    ca === range.value
                      ? "border-violet-600 bg-violet-50"
                      : "border-slate-200 hover:border-violet-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{range.label}</p>
                      <p className="text-sm text-slate-500">{range.description}</p>
                    </div>
                    {ca === range.value && (
                      <Check className="h-5 w-5 text-violet-600" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Step 3: Accompagnement */}
          {step === 3 && (
            <div className="space-y-3">
              {ACCOMPAGNEMENT_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setAccompagnement(option.value)}
                  className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                    accompagnement === option.value
                      ? "border-violet-600 bg-violet-50"
                      : "border-slate-200 hover:border-violet-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{option.icon}</span>
                      <p className="font-medium">{option.label}</p>
                    </div>
                    {accompagnement === option.value && (
                      <Check className="h-5 w-5 text-violet-600" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between pt-4">
            <div>
              {step > 1 ? (
                <Button variant="ghost" onClick={handleBack}>
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Retour
                </Button>
              ) : (
                <Button variant="ghost" onClick={onSkip}>
                  Passer
                </Button>
              )}
            </div>
            <Button onClick={handleNext} disabled={!canProceed()}>
              {step === totalSteps ? "Voir mes optimisations" : "Continuer"}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export { PROFESSION_PROFILES }
