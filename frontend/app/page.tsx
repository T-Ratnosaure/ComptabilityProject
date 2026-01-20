import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Info } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent flex items-center gap-2">
            🇫🇷 FiscalOptim
            <span className="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-semibold">
              Beta
            </span>
          </h1>
          <div className="flex gap-3">
            <Link href="/dashboard">
              <Button variant="outline">Dashboard</Button>
            </Link>
            <Link href="/simulator">
              <Button>Commencer →</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-violet-600 via-indigo-600 to-blue-600 bg-clip-text text-transparent">
          Estimez vos impôts<br />de freelance en 2 minutes
        </h2>
        <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
          Calculez une estimation de votre impôt, cotisations sociales et explorez
          des scénarios d'optimisation fiscale à étudier avec votre expert-comptable.
        </p>
        <Link href="/simulator">
          <Button size="lg" className="text-lg px-8 py-6 h-auto">
            Estimer mes impôts →
          </Button>
        </Link>
        <p className="text-sm text-slate-500 mt-4">
          Outil informatif uniquement - Ne remplace pas un conseil professionnel
        </p>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-3xl">⚡</span>
                Calcul instantané
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Impôt sur le revenu, TMI, cotisations sociales calculés en temps réel
                selon votre profil fiscal.
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-3xl">💡</span>
                Optimisations IA
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Notre IA analyse votre situation et présente des scénarios d'optimisation
                à explorer (PER, LMNP, changement de régime...).
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-3xl">🔒</span>
                100% confidentiel
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Aucune donnée personnelle n'est sauvegardée. Vos calculs restent privés
                et sécurisés.
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h3 className="text-3xl font-bold mb-4">
            Prêt à optimiser votre fiscalité ?
          </h3>
          <p className="text-xl mb-8 opacity-90">
            Rejoignez des milliers de freelances qui économisent sur leurs impôts.
          </p>
          <Link href="/simulator">
            <Button size="lg" variant="secondary" className="text-lg px-8 py-6 h-auto">
              Commencer maintenant →
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 bg-slate-50">
        <div className="container mx-auto px-4">
          <div className="text-center text-slate-600 mb-4">
            <p className="text-amber-600 font-semibold mb-1">Version Beta - Outil en développement</p>
            <p>© 2025 FiscalOptim - Estimation fiscale pour freelances français</p>
          </div>
          <div className="text-xs text-slate-500 max-w-3xl mx-auto text-center">
            <div className="flex items-center justify-center gap-1 mb-2">
              <Info className="h-3 w-3" />
              <span className="font-semibold">Avertissement légal</span>
            </div>
            <p className="mb-2">
              Cet outil fournit des <strong>estimations informatives à titre éducatif</strong> uniquement.
              Il ne remplace pas les services d'un expert-comptable, avocat fiscaliste ou
              conseiller en gestion de patrimoine agréé.
            </p>
            <p className="mb-2">
              Les scénarios d'investissement présentés ne constituent pas un conseil en investissement.
              Consultez un Conseiller en Investissements Financiers (CIF) agréé ORIAS avant toute décision.
            </p>
            <p className="mb-2">
              Les calculs sont basés sur les barèmes fiscaux publics 2025 et peuvent ne pas
              refléter votre situation personnelle complète.
            </p>
            <p className="text-slate-400">
              Ce service n'est pas enregistré auprès de l'ORIAS, l'AMF, ou l'Ordre des Experts-Comptables.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
