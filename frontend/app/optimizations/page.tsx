"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { apiClient, OptimizationRequest, OptimizationResponse, TaxCalculationRequest, TaxCalculationResponse } from "@/lib/api"
import { ArrowLeft, TrendingUp, AlertCircle, Sparkles, Lightbulb, CheckCircle } from "lucide-react"
import { Onboarding, PROFESSION_PROFILES } from "@/components/onboarding"
import { ChatPanel } from "@/components/chat-panel"

interface OnboardingData {
  profession: string
  ca: number
  accompagnement: string
  defaults: typeof PROFESSION_PROFILES.dev_consultant.defaults
  tips: string[]
}

export default function OptimizationsPage() {
  const [showOnboarding, setShowOnboarding] = useState(true)
  const [onboardingData, setOnboardingData] = useState<OnboardingData | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<OptimizationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [simulatorData, setSimulatorData] = useState<TaxCalculationRequest | null>(null)
  const [simulatorResult, setSimulatorResult] = useState<TaxCalculationResponse | null>(null)
  const [hasSimulatorData, setHasSimulatorData] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(false)

  const [profileData, setProfileData] = useState({
    status: "micro_bnc",
    chiffre_affaires: 50000,
    charges_deductibles: 0,
    nb_parts: 1,
    activity_type: "BNC",
  })

  const [contextData, setContextData] = useState({
    investment_capacity: 50000,
    risk_tolerance: "moderate",
    stable_income: true,
  })

  // Charger les données du simulateur depuis sessionStorage
  useEffect(() => {
    const storedProfile = sessionStorage.getItem("fiscalOptim_profileData")
    const storedResult = sessionStorage.getItem("fiscalOptim_taxResult")

    if (storedProfile && storedResult) {
      try {
        const profile: TaxCalculationRequest = JSON.parse(storedProfile)
        const result: TaxCalculationResponse = JSON.parse(storedResult)

        setSimulatorData(profile)
        setSimulatorResult(result)
        setHasSimulatorData(true)

        // Pré-remplir les données du profil avec celles du simulateur
        setProfileData({
          status: profile.person.status,
          chiffre_affaires: profile.income.professional_gross,
          charges_deductibles: profile.income.deductible_expenses,
          nb_parts: profile.person.nb_parts,
          activity_type: profile.person.status.includes("bnc") ? "BNC" : "BIC",
        })

        // Skip onboarding si on a des données du simulateur
        setShowOnboarding(false)
      } catch {
        console.error("Erreur lors du chargement des données du simulateur")
      }
    }
  }, [])

  const handleOnboardingComplete = (data: OnboardingData) => {
    setOnboardingData(data)
    // Apply defaults from profile
    setProfileData({
      status: data.defaults.status,
      chiffre_affaires: data.ca,
      charges_deductibles: 0,
      nb_parts: 1,
      activity_type: data.defaults.activity_type,
    })
    setContextData({
      investment_capacity: data.defaults.investment_capacity,
      risk_tolerance: data.defaults.risk_tolerance,
      stable_income: data.defaults.stable_income,
    })
    setShowOnboarding(false)
  }

  const handleSkipOnboarding = () => {
    setShowOnboarding(false)
  }

  // Calculate realistic tax values based on French tax brackets (2024)
  // Abattement varies by status
  const getAbattement = (status: string): number => {
    switch (status) {
      case "micro_bnc":
        return 0.34 // 34% abattement
      case "micro_bic_service":
        return 0.50 // 50% abattement
      case "micro_bic_vente":
        return 0.71 // 71% abattement
      case "reel_bnc":
      case "reel_bic":
        return 0 // No abattement, use actual charges
      default:
        return 0.34
    }
  }

  const abattement = getAbattement(profileData.status)
  const revenuImposable = profileData.status.startsWith("reel")
    ? profileData.chiffre_affaires - profileData.charges_deductibles
    : profileData.chiffre_affaires * (1 - abattement)
  const partIncome = revenuImposable / profileData.nb_parts

  // Simplified French tax calculation (2025 brackets)
  const calculateImpot = (income: number): { impot: number; tmi: number } => {
    const brackets = [
      { limit: 11497, rate: 0 },
      { limit: 29315, rate: 0.11 },
      { limit: 83884, rate: 0.30 },
      { limit: 180271, rate: 0.41 },
      { limit: Infinity, rate: 0.45 },
    ]
    let impot = 0
    let previousLimit = 0
    let tmi = 0
    for (const bracket of brackets) {
      if (income > previousLimit) {
        const taxableInBracket = Math.min(income, bracket.limit) - previousLimit
        impot += taxableInBracket * bracket.rate
        if (income > previousLimit) tmi = bracket.rate
      }
      previousLimit = bracket.limit
    }
    return { impot, tmi }
  }

  const taxCalc = calculateImpot(partIncome)
  const impotBrut = taxCalc.impot * profileData.nb_parts

  const mockTaxResult = {
    tax_year: 2025,
    impot: {
      revenu_imposable: revenuImposable,
      part_income: partIncome,
      impot_brut: impotBrut,
      impot_net: impotBrut,
      tmi: taxCalc.tmi,
      tax_reductions: {},
      per_deduction_applied: 0,
      per_deduction_excess: 0,
      per_plafond_detail: null,
      tranches_detail: [],
      pas_withheld: 0,
      due_now: impotBrut,
    },
    socials: {
      urssaf_expected: profileData.chiffre_affaires * 0.218,
      urssaf_paid: 0,
      delta: 0,
      rate_used: 0.218,
    },
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Utiliser les vraies données du simulateur si disponibles
      const taxResult = hasSimulatorData && simulatorResult ? simulatorResult : mockTaxResult

      const request: OptimizationRequest = {
        profile: profileData,
        tax_result: taxResult,
        context: contextData,
      }
      const response = await apiClient.runOptimization(request)
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur d'optimisation")
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(value)
  }

  const getCategoryInfo = (category: string): { label: string; color: string } => {
    const categories: Record<string, { label: string; color: string }> = {
      "regime": { label: "Régime fiscal", color: "bg-blue-100 text-blue-700" },
      "deduction": { label: "Déduction", color: "bg-green-100 text-green-700" },
      "investment": { label: "Investissement", color: "bg-orange-100 text-orange-700" },
      "structure": { label: "Structure", color: "bg-indigo-100 text-indigo-700" },
      "family": { label: "Famille", color: "bg-pink-100 text-pink-700" },
    }
    return categories[category.toLowerCase()] || { label: category, color: "bg-slate-100 text-slate-700" }
  }

  const getRiskColor = (risk: string) => {
    const colors: Record<string, string> = {
      "low": "text-green-600",
      "faible": "text-green-600",
      "medium": "text-orange-600",
      "moyen": "text-orange-600",
      "high": "text-red-600",
      "élevé": "text-red-600",
    }
    return colors[risk.toLowerCase()] || "text-slate-600"
  }

  const getComplexityInfo = (complexity: string): { stars: string; label: string; color: string } => {
    const level = complexity.toLowerCase()
    if (level.includes("easy") || level.includes("facile") || level.includes("simple")) {
      return { stars: "⭐", label: "Facile", color: "bg-green-100 text-green-700" }
    }
    if (level.includes("moderate") || level.includes("modéré") || level.includes("moyen")) {
      return { stars: "⭐⭐", label: "Modéré", color: "bg-yellow-100 text-yellow-700" }
    }
    // complex, complexe, difficile
    return { stars: "⭐⭐⭐", label: "Complexe", color: "bg-red-100 text-red-700" }
  }

  // Format description: handle newlines and basic markdown (safe - no dangerouslySetInnerHTML)
  const formatDescription = (text: string) => {
    return text.split('\n').map((line, lineIndex) => {
      // Parse **text** into bold spans safely using React components
      const parts: React.ReactNode[] = []
      const regex = /\*\*([^*]+)\*\*/g
      let lastIndex = 0
      let match
      let partIndex = 0

      while ((match = regex.exec(line)) !== null) {
        // Add text before the bold
        if (match.index > lastIndex) {
          parts.push(<span key={`${lineIndex}-${partIndex++}`}>{line.slice(lastIndex, match.index)}</span>)
        }
        // Add bold text
        parts.push(<strong key={`${lineIndex}-${partIndex++}`}>{match[1]}</strong>)
        lastIndex = match.index + match[0].length
      }
      // Add remaining text
      if (lastIndex < line.length) {
        parts.push(<span key={`${lineIndex}-${partIndex++}`}>{line.slice(lastIndex)}</span>)
      }
      // If no parts, add the whole line
      if (parts.length === 0) {
        parts.push(<span key={`${lineIndex}-0`}>{line}</span>)
      }

      return <span key={`line-${lineIndex}`}>{parts}</span>
    }).reduce((acc: React.ReactNode[], curr, i, arr) => {
      acc.push(curr)
      if (i < arr.length - 1) acc.push(<br key={`br-${i}`} />)
      return acc
    }, [])
  }

  // Show onboarding if not completed
  if (showOnboarding) {
    return (
      <Onboarding
        onComplete={handleOnboardingComplete}
        onSkip={handleSkipOnboarding}
      />
    )
  }

  const professionLabel = onboardingData
    ? PROFESSION_PROFILES[onboardingData.profession as keyof typeof PROFESSION_PROFILES]?.label
    : null

  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/simulator" className="flex items-center gap-2 text-slate-600 hover:text-slate-900">
            <ArrowLeft className="h-4 w-4" />
            Retour au simulateur
          </Link>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
            FiscalOptim
          </h1>
          <div className="w-20" />
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
              Optimisations fiscales
            </h2>
            {professionLabel && (
              <p className="text-slate-600 text-lg">
                Stratégies personnalisées pour <span className="font-semibold">{professionLabel}</span>
              </p>
            )}
          </div>

          {/* Indicateur des données du simulateur */}
          {hasSimulatorData && simulatorResult && (
            <Card className="mb-4 border-green-200 bg-green-50">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2 text-green-800">
                  <CheckCircle className="h-5 w-5" />
                  Données du simulateur chargées
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-green-700 text-sm">
                  Vos données de simulation sont utilisées : CA {profileData.chiffre_affaires.toLocaleString("fr-FR")}€,
                  Statut {profileData.status}, Impôt calculé {formatCurrency(simulatorResult.impot.impot_net)}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Tips from onboarding */}
          {onboardingData && onboardingData.tips.length > 0 && (
            <Card className="mb-8 border-amber-200 bg-amber-50">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2 text-amber-800">
                  <Lightbulb className="h-5 w-5" />
                  Conseils pour votre profil
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1">
                  {onboardingData.tips.map((tip, i) => (
                    <li key={i} className="text-amber-900 text-sm flex items-start gap-2">
                      <span className="text-amber-600">•</span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Form Column */}
            <div className="lg:col-span-1">
              <form onSubmit={handleSubmit} className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Votre profil</CardTitle>
                    <CardDescription>
                      {onboardingData
                        ? "Valeurs pré-remplies selon votre profil"
                        : "Informations pour personnaliser les recommandations"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="status">Statut fiscal</Label>
                      <Select
                        value={profileData.status}
                        onValueChange={(value) => setProfileData(prev => ({ ...prev, status: value }))}
                      >
                        <SelectTrigger id="status">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="micro_bnc">Micro-BNC (Professions libérales)</SelectItem>
                          <SelectItem value="micro_bic_service">Micro-BIC Services</SelectItem>
                          <SelectItem value="micro_bic_vente">Micro-BIC Ventes</SelectItem>
                          <SelectItem value="reel_bnc">Réel BNC</SelectItem>
                          <SelectItem value="reel_bic">Réel BIC</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="activity_type">Type d'activité</Label>
                      <Select
                        value={profileData.activity_type}
                        onValueChange={(value) => setProfileData(prev => ({ ...prev, activity_type: value }))}
                      >
                        <SelectTrigger id="activity_type">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="BNC">BNC (Bénéfices Non Commerciaux)</SelectItem>
                          <SelectItem value="BIC">BIC (Bénéfices Industriels et Commerciaux)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="ca">Chiffre d'affaires annuel</Label>
                      <Input
                        id="ca"
                        type="number"
                        step="1000"
                        min="0"
                        value={profileData.chiffre_affaires}
                        onChange={(e) => setProfileData(prev => ({ ...prev, chiffre_affaires: parseFloat(e.target.value) || 0 }))}
                        placeholder="50000"
                      />
                    </div>

                    <div>
                      <Label htmlFor="charges">Charges déductibles</Label>
                      <Input
                        id="charges"
                        type="number"
                        step="100"
                        min="0"
                        value={profileData.charges_deductibles}
                        onChange={(e) => setProfileData(prev => ({ ...prev, charges_deductibles: parseFloat(e.target.value) || 0 }))}
                        placeholder="5000"
                      />
                    </div>

                    <div>
                      <Label htmlFor="nb_parts">Nombre de parts fiscales</Label>
                      <Input
                        id="nb_parts"
                        type="number"
                        step="0.5"
                        min="1"
                        value={profileData.nb_parts}
                        onChange={(e) => setProfileData(prev => ({ ...prev, nb_parts: parseFloat(e.target.value) || 1 }))}
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Investment Context Card */}
                <Card>
                  <CardHeader>
                    <CardTitle>Capacité d'investissement</CardTitle>
                    <CardDescription>Pour débloquer les stratégies avancées</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="investment_capacity">Capacité d'investissement (€)</Label>
                      <Input
                        id="investment_capacity"
                        type="number"
                        step="10000"
                        min="0"
                        value={contextData.investment_capacity}
                        onChange={(e) => setContextData(prev => ({ ...prev, investment_capacity: parseFloat(e.target.value) || 0 }))}
                        placeholder="50000"
                      />
                    </div>

                    <div>
                      <Label htmlFor="risk_tolerance">Tolérance au risque</Label>
                      <Select
                        value={contextData.risk_tolerance}
                        onValueChange={(value) => setContextData(prev => ({ ...prev, risk_tolerance: value }))}
                      >
                        <SelectTrigger id="risk_tolerance">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="conservative">Faible (prudent)</SelectItem>
                          <SelectItem value="moderate">Moyen (équilibré)</SelectItem>
                          <SelectItem value="aggressive">Élevé (dynamique)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="stable_income"
                        checked={contextData.stable_income}
                        onChange={(e) => setContextData(prev => ({ ...prev, stable_income: e.target.checked }))}
                        className="h-4 w-4 rounded border-gray-300"
                      />
                      <Label htmlFor="stable_income">Revenus stables (activité pérenne)</Label>
                    </div>
                  </CardContent>
                </Card>

                <Button type="submit" size="lg" className="w-full" disabled={loading}>
                  <Sparkles className="mr-2 h-5 w-5" />
                  {loading ? "Analyse en cours..." : "Générer les optimisations"}
                </Button>

                {onboardingData && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="w-full"
                    onClick={() => setShowOnboarding(true)}
                  >
                    Modifier mon profil métier
                  </Button>
                )}
              </form>
            </div>

            {/* Results Column */}
            <div className="lg:col-span-2">
              {error && (
                <Card className="border-red-200 bg-red-50 mb-6">
                  <CardHeader>
                    <CardTitle className="text-red-600 flex items-center gap-2">
                      <AlertCircle className="h-5 w-5" />
                      Erreur
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-red-600">{error}</p>
                  </CardContent>
                </Card>
              )}

              {result ? (
                <div className="space-y-6">
                  {/* Summary Card */}
                  <Card className="border-violet-200 bg-gradient-to-br from-violet-50 to-indigo-50">
                    <CardHeader>
                      <CardTitle className="text-2xl flex items-center gap-2">
                        <TrendingUp className="h-6 w-6 text-violet-600" />
                        Potentiel d'économies
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex justify-around py-4">
                        <div className="text-center">
                          <p className="text-slate-600 mb-2">Impôt actuel</p>
                          <p className="text-3xl font-bold text-slate-700">
                            {formatCurrency(impotBrut)}
                          </p>
                          <p className="text-slate-500 mt-1">avant optimisation</p>
                        </div>
                        <div className="text-center">
                          <p className="text-slate-600 mb-2">Économies possibles</p>
                          <p className="text-5xl font-bold text-green-600">
                            -{formatCurrency(result.potential_savings_total)}
                          </p>
                          <p className="text-slate-500 mt-1">par an</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Recommendations */}
                  <div className="space-y-4">
                    <h3 className="text-2xl font-bold text-slate-900">
                      {result.recommendations.length} recommandations personnalisées
                    </h3>

                    {result.recommendations.map((rec, index) => (
                      <Card key={index} className="hover:shadow-lg transition-shadow">
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <CardTitle className="text-xl mb-2">{rec.title}</CardTitle>
                              <div className="flex gap-2 flex-wrap">
                                {(() => {
                                  const categoryInfo = getCategoryInfo(rec.category)
                                  return (
                                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${categoryInfo.color}`}>
                                      {categoryInfo.label}
                                    </span>
                                  )
                                })()}
                                {(() => {
                                  const complexityInfo = getComplexityInfo(rec.complexity)
                                  return (
                                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${complexityInfo.color}`}>
                                      {complexityInfo.stars} {complexityInfo.label}
                                    </span>
                                  )
                                })()}
                                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getRiskColor(rec.risk)}`}>
                                  Risque: {rec.risk}
                                </span>
                              </div>
                            </div>
                            <div className="ml-4 text-right">
                              <p className="text-sm text-slate-600">Économie estimée</p>
                              <p className="text-2xl font-bold text-green-600">
                                {formatCurrency(rec.impact_estimated)}
                              </p>
                              {rec.required_investment && rec.required_investment > 0 && (
                                <>
                                  <div className="mt-2">
                                    <p className="text-sm text-slate-600">Investissement</p>
                                    <p className="text-lg font-bold text-orange-600">
                                      {formatCurrency(rec.required_investment)}
                                    </p>
                                  </div>
                                  <div className="mt-2">
                                    <p className="text-sm text-slate-600">Rendement</p>
                                    <p className="text-lg font-bold text-violet-600">
                                      {((rec.impact_estimated / rec.required_investment) * 100).toFixed(0)}%
                                    </p>
                                  </div>
                                </>
                              )}
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="text-slate-700 leading-relaxed">{formatDescription(rec.description)}</div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  {/* CTA */}
                  <Card className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white border-0">
                    <CardHeader>
                      <CardTitle className="text-white text-xl">Besoin de conseils personnalisés ?</CardTitle>
                      <CardDescription className="text-white/90">
                        Discutez avec notre IA pour obtenir des recommandations adaptées à votre situation
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Button
                        size="lg"
                        variant="secondary"
                        className="w-full"
                        onClick={() => setIsChatOpen(true)}
                      >
                        <Sparkles className="mr-2 h-5 w-5" />
                        Discuter avec l'IA fiscale
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <Card className="border-slate-200">
                  <CardHeader>
                    <CardTitle>Recommandations</CardTitle>
                    <CardDescription>
                      Cliquez sur "Générer les optimisations" pour voir vos recommandations
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="py-16 text-center text-slate-400">
                    <Sparkles className="mx-auto h-16 w-16 mb-4 opacity-50" />
                    <p>En attente d'analyse...</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Chat Panel intégré */}
      <ChatPanel
        profileData={simulatorData}
        taxResult={hasSimulatorData ? simulatorResult : mockTaxResult}
        optimizationResult={result}
        isOpen={isChatOpen}
        onToggle={() => setIsChatOpen(!isChatOpen)}
      />
    </div>
  )
}
