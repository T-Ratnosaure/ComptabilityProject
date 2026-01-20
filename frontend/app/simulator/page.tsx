"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { apiClient, TaxCalculationRequest, TaxCalculationResponse } from "@/lib/api"
import { ArrowLeft, Calculator, TrendingUp } from "lucide-react"
import { LegalDisclaimerBanner, LegalDisclaimerFooter } from "@/components/legal-disclaimer"

export default function SimulatorPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TaxCalculationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [formData, setFormData] = useState<TaxCalculationRequest>({
    tax_year: 2025,
    person: {
      name: "",
      nb_parts: 1,
      status: "micro_bnc",
      situation_familiale: "celibataire",
    },
    income: {
      professional_gross: 0,
      salary: 0,
      rental_income: 0,
      capital_income: 0,
      deductible_expenses: 0,
    },
    deductions: {
      per_contributions: 0,
      alimony: 0,
      other_deductions: 0,
    },
    social: {
      urssaf_declared_ca: 0,
      urssaf_paid: 0,
    },
    pas_withheld: 0,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await apiClient.calculateTax(formData)
      setResult(response)

      // Sauvegarder les données dans sessionStorage pour le chat IA
      sessionStorage.setItem("fiscalOptim_profileData", JSON.stringify(formData))
      sessionStorage.setItem("fiscalOptim_taxResult", JSON.stringify(response))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur de calcul")
    } finally {
      setLoading(false)
    }
  }

  const updatePerson = (key: keyof typeof formData.person, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      person: { ...prev.person, [key]: value }
    }))
  }

  const updateIncome = (key: keyof typeof formData.income, value: number) => {
    setFormData(prev => ({
      ...prev,
      income: { ...prev.income, [key]: value }
    }))
  }

  const updateDeductions = (key: keyof typeof formData.deductions, value: number) => {
    setFormData(prev => ({
      ...prev,
      deductions: { ...prev.deductions, [key]: value }
    }))
  }

  const updateSocial = (key: keyof typeof formData.social, value: number) => {
    setFormData(prev => ({
      ...prev,
      social: { ...prev.social, [key]: value }
    }))
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 2
    }).format(value / 100)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 text-slate-600 hover:text-slate-900">
            <ArrowLeft className="h-4 w-4" />
            Retour
          </Link>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
            🇫🇷 FiscalOptim
          </h1>
          <div className="w-20" />
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Legal Disclaimer Banner */}
          <div className="mb-6">
            <LegalDisclaimerBanner />
          </div>

          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
              Simulateur d'impôts (Estimation)
            </h2>
            <p className="text-slate-600 text-lg">
              Estimez vos impôts et cotisations sociales - résultats indicatifs uniquement
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Form Column */}
            <div>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Personal Information */}
                <Card>
                  <CardHeader>
                    <CardTitle>Informations personnelles</CardTitle>
                    <CardDescription>Votre situation fiscale</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="name">Nom</Label>
                      <Input
                        id="name"
                        value={formData.person.name}
                        onChange={(e) => updatePerson("name", e.target.value)}
                        placeholder="Jean Dupont"
                      />
                    </div>

                    <div>
                      <Label htmlFor="status">Statut</Label>
                      <Select
                        value={formData.person.status}
                        onValueChange={(value) => updatePerson("status", value)}
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
                      <Label htmlFor="nb_parts">Nombre de parts fiscales</Label>
                      <Input
                        id="nb_parts"
                        type="number"
                        step="0.5"
                        min="1"
                        value={formData.person.nb_parts}
                        onChange={(e) => updatePerson("nb_parts", parseFloat(e.target.value))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="situation_familiale">Situation familiale</Label>
                      <Select
                        value={formData.person.situation_familiale || "celibataire"}
                        onValueChange={(value) => updatePerson("situation_familiale", value)}
                      >
                        <SelectTrigger id="situation_familiale">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="celibataire">Célibataire / Divorcé(e) / Veuf(ve)</SelectItem>
                          <SelectItem value="couple">Marié(e) / Pacsé(e) (imposition commune)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="tax_year">Année fiscale</Label>
                      <Input
                        id="tax_year"
                        type="number"
                        value={formData.tax_year}
                        onChange={(e) => setFormData(prev => ({ ...prev, tax_year: parseInt(e.target.value) }))}
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Income */}
                <Card>
                  <CardHeader>
                    <CardTitle>Revenus</CardTitle>
                    <CardDescription>Vos différentes sources de revenus</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="professional_gross">Chiffre d'affaires brut</Label>
                      <Input
                        id="professional_gross"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.income.professional_gross}
                        onChange={(e) => updateIncome("professional_gross", parseFloat(e.target.value))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="salary">Salaire net imposable</Label>
                      <Input
                        id="salary"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.income.salary}
                        onChange={(e) => updateIncome("salary", parseFloat(e.target.value))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="rental_income">Revenus fonciers</Label>
                      <Input
                        id="rental_income"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.income.rental_income}
                        onChange={(e) => updateIncome("rental_income", parseFloat(e.target.value))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="capital_income">Revenus de capitaux</Label>
                      <Input
                        id="capital_income"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.income.capital_income}
                        onChange={(e) => updateIncome("capital_income", parseFloat(e.target.value))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="deductible_expenses">Charges déductibles</Label>
                      <Input
                        id="deductible_expenses"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.income.deductible_expenses}
                        onChange={(e) => updateIncome("deductible_expenses", parseFloat(e.target.value))}
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Deductions */}
                <Card>
                  <CardHeader>
                    <CardTitle>Déductions</CardTitle>
                    <CardDescription>Réductions et déductions fiscales</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="per_contributions">Versements PER</Label>
                      <Input
                        id="per_contributions"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.deductions.per_contributions}
                        onChange={(e) => updateDeductions("per_contributions", parseFloat(e.target.value))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="alimony">Pensions alimentaires</Label>
                      <Input
                        id="alimony"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.deductions.alimony}
                        onChange={(e) => updateDeductions("alimony", parseFloat(e.target.value))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="other_deductions">Autres déductions</Label>
                      <Input
                        id="other_deductions"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.deductions.other_deductions}
                        onChange={(e) => updateDeductions("other_deductions", parseFloat(e.target.value))}
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Social Contributions */}
                <Card>
                  <CardHeader>
                    <CardTitle>Cotisations sociales</CardTitle>
                    <CardDescription>URSSAF et prélèvement à la source</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="urssaf_declared_ca">CA déclaré URSSAF</Label>
                      <Input
                        id="urssaf_declared_ca"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.social.urssaf_declared_ca}
                        onChange={(e) => updateSocial("urssaf_declared_ca", parseFloat(e.target.value))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="urssaf_paid">Cotisations URSSAF payées</Label>
                      <Input
                        id="urssaf_paid"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.social.urssaf_paid}
                        onChange={(e) => updateSocial("urssaf_paid", parseFloat(e.target.value))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="pas_withheld">Prélèvement à la source</Label>
                      <Input
                        id="pas_withheld"
                        type="number"
                        step="100"
                        min="0"
                        value={formData.pas_withheld}
                        onChange={(e) => setFormData(prev => ({ ...prev, pas_withheld: parseFloat(e.target.value) }))}
                      />
                    </div>
                  </CardContent>
                </Card>

                <Button type="submit" size="lg" className="w-full" disabled={loading}>
                  <Calculator className="mr-2 h-5 w-5" />
                  {loading ? "Calcul en cours..." : "Calculer mes impôts"}
                </Button>
              </form>
            </div>

            {/* Results Column */}
            <div className="lg:sticky lg:top-24 lg:h-fit">
              {error && (
                <Card className="border-red-200 bg-red-50 mb-6">
                  <CardHeader>
                    <CardTitle className="text-red-600">Erreur</CardTitle>
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
                      <CardTitle className="text-2xl">Résultats</CardTitle>
                      <CardDescription>Votre situation fiscale calculée</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex justify-between items-center p-4 bg-white rounded-lg">
                        <span className="text-slate-600">Revenu imposable</span>
                        <span className="text-xl font-bold">{formatCurrency(result.impot.revenu_imposable)}</span>
                      </div>

                      <div className="flex justify-between items-center p-4 bg-white rounded-lg">
                        <span className="text-slate-600">Revenu par part</span>
                        <span className="text-xl font-bold">{formatCurrency(result.impot.part_income)}</span>
                      </div>

                      <div className="border-t pt-4">
                        <h3 className="font-semibold text-lg mb-3">Impôt sur le revenu</h3>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-slate-600">IR brut</span>
                            <span className="font-semibold">{formatCurrency(result.impot.impot_brut)}</span>
                          </div>
                          {result.impot.cehr !== undefined && result.impot.cehr > 0 && (
                            <div className="flex justify-between">
                              <span className="text-slate-600">CEHR (hauts revenus)</span>
                              <span className="font-semibold text-orange-600">{formatCurrency(result.impot.cehr)}</span>
                            </div>
                          )}
                          {result.impot.cdhr !== undefined && result.impot.cdhr > 0 && (
                            <div className="flex justify-between">
                              <span className="text-slate-600">CDHR (taux mini 20%)</span>
                              <span className="font-semibold text-red-600">{formatCurrency(result.impot.cdhr)}</span>
                            </div>
                          )}
                          <div className="flex justify-between">
                            <span className="text-slate-600">Impôt total</span>
                            <span className="font-semibold text-violet-600">{formatCurrency(result.impot.impot_net)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-600">TMI</span>
                            <span className="font-semibold">{(result.impot.tmi * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-600">À payer maintenant</span>
                            <span className="font-semibold">{formatCurrency(result.impot.due_now)}</span>
                          </div>
                        </div>
                      </div>

                      <div className="border-t pt-4">
                        <h3 className="font-semibold text-lg mb-3">Cotisations sociales</h3>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-slate-600">URSSAF attendue</span>
                            <span className="font-semibold">{formatCurrency(result.socials.urssaf_expected)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-600">URSSAF payée</span>
                            <span className="font-semibold">{formatCurrency(result.socials.urssaf_paid)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-600">Différence</span>
                            <span className={`font-semibold ${result.socials.delta >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {formatCurrency(result.socials.delta)}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="border-t pt-4">
                        <div className="flex justify-between items-center p-4 bg-violet-600 text-white rounded-lg">
                          <span className="font-semibold text-lg">Charge fiscale totale</span>
                          <span className="text-2xl font-bold">{formatCurrency(result.impot.impot_net + result.socials.urssaf_expected)}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Action Button */}
                  <Link href="/optimizations">
                    <Button size="lg" className="w-full" variant="outline">
                      <TrendingUp className="mr-2 h-5 w-5" />
                      Voir les optimisations possibles
                    </Button>
                  </Link>
                </div>
              ) : (
                <Card className="border-slate-200">
                  <CardHeader>
                    <CardTitle>Résultats</CardTitle>
                    <CardDescription>
                      Remplissez le formulaire et cliquez sur "Calculer" pour voir vos résultats
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="py-12 text-center text-slate-400">
                    <Calculator className="mx-auto h-16 w-16 mb-4 opacity-50" />
                    <p>En attente de calcul...</p>
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
