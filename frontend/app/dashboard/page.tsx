"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, Calculator, TrendingUp, PieChart as PieChartIcon } from "lucide-react"
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts"

export default function DashboardPage() {
  // Mock data - in production this would come from API/state
  const taxData = {
    revenu_imposable: 28500,
    quotient_familial: 28500,
    impot: {
      impot_brut: 3200,
      impot_net: 3200,
      tmi: 11,
      taux_effectif: 11.2,
    },
    socials: {
      urssaf_expected: 7150,
      difference: -150,
    },
    charge_totale: 10350,
  }

  const incomeBreakdown = [
    { name: "Revenus professionnels", value: 50000, color: "#8B5CF6" },
    { name: "Salaire", value: 0, color: "#6366F1" },
    { name: "Revenus fonciers", value: 0, color: "#3B82F6" },
    { name: "Revenus de capitaux", value: 0, color: "#0EA5E9" },
  ].filter(item => item.value > 0)

  const chargesBreakdown = [
    { name: "Impôt sur le revenu", value: 3200, color: "#EF4444" },
    { name: "Cotisations sociales", value: 7150, color: "#F97316" },
  ]

  const monthlyProjection = [
    { month: "Jan", impot: 267, cotisations: 596 },
    { month: "Fév", impot: 267, cotisations: 596 },
    { month: "Mar", impot: 267, cotisations: 596 },
    { month: "Avr", impot: 267, cotisations: 596 },
    { month: "Mai", impot: 267, cotisations: 596 },
    { month: "Juin", impot: 267, cotisations: 596 },
    { month: "Juil", impot: 267, cotisations: 596 },
    { month: "Août", impot: 267, cotisations: 596 },
    { month: "Sep", impot: 267, cotisations: 596 },
    { month: "Oct", impot: 267, cotisations: 596 },
    { month: "Nov", impot: 267, cotisations: 596 },
    { month: "Déc", impot: 267, cotisations: 596 },
  ]

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 2
    }).format(value / 100)
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-slate-200 rounded-lg shadow-lg">
          <p className="font-semibold">{payload[0].name}</p>
          <p className="text-violet-600">{formatCurrency(payload[0].value)}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 text-slate-600 hover:text-slate-900">
            <ArrowLeft className="h-4 w-4" />
            Accueil
          </Link>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
            🇫🇷 FiscalOptim
          </h1>
          <div className="flex gap-2">
            <Link href="/simulator">
              <Button variant="outline" size="sm">
                <Calculator className="mr-2 h-4 w-4" />
                Simulateur
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
              Tableau de bord fiscal
            </h2>
            <p className="text-slate-600 text-lg">
              Vue d'ensemble de votre situation fiscale 2024
            </p>
          </div>

          {/* Key Metrics */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Revenu imposable</CardDescription>
                <CardTitle className="text-3xl text-violet-600">
                  {formatCurrency(taxData.revenu_imposable)}
                </CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Impôt net</CardDescription>
                <CardTitle className="text-3xl text-red-600">
                  {formatCurrency(taxData.impot.impot_net)}
                </CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>TMI (Tranche marginale)</CardDescription>
                <CardTitle className="text-3xl text-indigo-600">
                  {formatPercent(taxData.impot.tmi)}
                </CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Charge totale</CardDescription>
                <CardTitle className="text-3xl text-slate-900">
                  {formatCurrency(taxData.charge_totale)}
                </CardTitle>
              </CardHeader>
            </Card>
          </div>

          <div className="grid lg:grid-cols-2 gap-6 mb-8">
            {/* Income Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChartIcon className="h-5 w-5 text-violet-600" />
                  Répartition des revenus
                </CardTitle>
                <CardDescription>Sources de revenus</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={incomeBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {incomeBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2">
                  {incomeBreakdown.map((item, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-sm text-slate-600">{item.name}</span>
                      </div>
                      <span className="font-semibold">{formatCurrency(item.value)}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Charges Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChartIcon className="h-5 w-5 text-red-600" />
                  Répartition des charges
                </CardTitle>
                <CardDescription>Impôts et cotisations</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chargesBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chargesBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2">
                  {chargesBreakdown.map((item, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-sm text-slate-600">{item.name}</span>
                      </div>
                      <span className="font-semibold">{formatCurrency(item.value)}</span>
                    </div>
                  ))}
                  <div className="border-t pt-2 flex justify-between items-center">
                    <span className="font-semibold text-slate-900">Total</span>
                    <span className="font-bold text-lg">{formatCurrency(taxData.charge_totale)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Monthly Projection */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-violet-600" />
                Projection mensuelle
              </CardTitle>
              <CardDescription>
                Charges fiscales et sociales mensuelles estimées
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={monthlyProjection}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="month" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px'
                    }}
                    formatter={(value: number) => formatCurrency(value)}
                  />
                  <Legend />
                  <Bar dataKey="impot" name="Impôt sur le revenu" fill="#8B5CF6" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="cotisations" name="Cotisations sociales" fill="#6366F1" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Insights & Actions */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-blue-900">💡 Informations clés</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm text-blue-700">
                  • Votre taux effectif d'imposition est de {formatPercent(taxData.impot.taux_effectif)}
                </p>
                <p className="text-sm text-blue-700">
                  • Vous êtes dans la tranche marginale à {formatPercent(taxData.impot.tmi)}
                </p>
                <p className="text-sm text-blue-700">
                  • Vos cotisations sociales représentent {formatPercent((taxData.socials.urssaf_expected / taxData.charge_totale) * 100)} de vos charges totales
                </p>
              </CardContent>
            </Card>

            <Card className="border-violet-200 bg-gradient-to-br from-violet-50 to-indigo-50">
              <CardHeader>
                <CardTitle className="text-violet-900">🎯 Actions recommandées</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Link href="/optimizations">
                  <Button className="w-full" variant="default">
                    <TrendingUp className="mr-2 h-4 w-4" />
                    Voir les optimisations possibles
                  </Button>
                </Link>
                <Link href="/chat">
                  <Button className="w-full" variant="outline">
                    Discuter avec l'IA fiscale
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
