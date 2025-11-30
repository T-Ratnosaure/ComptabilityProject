"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { apiClient, OptimizationRequest, OptimizationResponse, Recommendation } from "@/lib/api"
import { ArrowLeft, MessageSquare, TrendingUp, AlertCircle, Sparkles } from "lucide-react"

export default function OptimizationsPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<OptimizationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [profileData, setProfileData] = useState({
    status: "micro-entrepreneur",
    chiffre_affaires: 0,
    charges_deductibles: 0,
    nb_parts: 1,
    activity_type: "services",
  })

  // Mock tax result for now - in production this would come from the simulator
  const mockTaxResult = {
    revenu_imposable: 0,
    quotient_familial: 0,
    impot: {
      impot_brut: 0,
      impot_net: 0,
      tmi: 0,
      taux_effectif: 0,
    },
    socials: {
      urssaf_expected: 0,
      difference: 0,
    },
    charge_totale: 0,
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const request: OptimizationRequest = {
        profile: profileData,
        tax_result: mockTaxResult,
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

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      "regime": "bg-blue-100 text-blue-700",
      "deductions": "bg-green-100 text-green-700",
      "timing": "bg-purple-100 text-purple-700",
      "investment": "bg-orange-100 text-orange-700",
      "structure": "bg-indigo-100 text-indigo-700",
      "default": "bg-slate-100 text-slate-700",
    }
    return colors[category.toLowerCase()] || colors.default
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

  const getComplexityIcon = (complexity: string) => {
    const level = complexity.toLowerCase()
    if (level.includes("faible") || level.includes("low")) return "⭐"
    if (level.includes("moyen") || level.includes("medium")) return "⭐⭐"
    return "⭐⭐⭐"
  }

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
            🇫🇷 FiscalOptim
          </h1>
          <Link href="/chat">
            <Button variant="outline" size="sm">
              <MessageSquare className="mr-2 h-4 w-4" />
              Chat IA
            </Button>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
              Optimisations fiscales
            </h2>
            <p className="text-slate-600 text-lg">
              Découvrez des stratégies personnalisées pour réduire vos impôts
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Form Column */}
            <div className="lg:col-span-1">
              <form onSubmit={handleSubmit} className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Votre profil</CardTitle>
                    <CardDescription>Informations pour personnaliser les recommandations</CardDescription>
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
                          <SelectItem value="micro-entrepreneur">Micro-entrepreneur</SelectItem>
                          <SelectItem value="indépendant">Indépendant (BNC/BIC réel)</SelectItem>
                          <SelectItem value="salarié">Salarié</SelectItem>
                          <SelectItem value="mixte">Mixte</SelectItem>
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
                          <SelectItem value="services">Prestations de services</SelectItem>
                          <SelectItem value="commerce">Commerce</SelectItem>
                          <SelectItem value="artisanat">Artisanat</SelectItem>
                          <SelectItem value="profession_liberale">Profession libérale</SelectItem>
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
                        onChange={(e) => setProfileData(prev => ({ ...prev, chiffre_affaires: parseFloat(e.target.value) }))}
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
                        onChange={(e) => setProfileData(prev => ({ ...prev, charges_deductibles: parseFloat(e.target.value) }))}
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
                        onChange={(e) => setProfileData(prev => ({ ...prev, nb_parts: parseFloat(e.target.value) }))}
                      />
                    </div>
                  </CardContent>
                </Card>

                <Button type="submit" size="lg" className="w-full" disabled={loading}>
                  <Sparkles className="mr-2 h-5 w-5" />
                  {loading ? "Analyse en cours..." : "Générer les optimisations"}
                </Button>
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
                      <div className="text-center py-4">
                        <p className="text-slate-600 mb-2">Économies totales estimées</p>
                        <p className="text-5xl font-bold text-violet-600">
                          {formatCurrency(result.potential_savings_total)}
                        </p>
                        <p className="text-slate-500 mt-2">par an</p>
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
                                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getCategoryColor(rec.category)}`}>
                                  {rec.category}
                                </span>
                                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
                                  {getComplexityIcon(rec.complexity)} {rec.complexity}
                                </span>
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
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <p className="text-slate-700 leading-relaxed">{rec.description}</p>
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
                      <Link href="/chat">
                        <Button size="lg" variant="secondary" className="w-full">
                          <MessageSquare className="mr-2 h-5 w-5" />
                          Discuter avec l'IA fiscale
                        </Button>
                      </Link>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <Card className="border-slate-200">
                  <CardHeader>
                    <CardTitle>Recommandations</CardTitle>
                    <CardDescription>
                      Remplissez le formulaire pour générer vos optimisations personnalisées
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
    </div>
  )
}
