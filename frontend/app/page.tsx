import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
            🇫🇷 FiscalOptim
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
          Optimisez vos impôts<br />de freelance en 2 minutes
        </h2>
        <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
          Calculez instantanément votre impôt, cotisations sociales et découvrez
          des optimisations fiscales personnalisées avec l'IA.
        </p>
        <Link href="/simulator">
          <Button size="lg" className="text-lg px-8 py-6 h-auto">
            Calculer mes impôts gratuitement →
          </Button>
        </Link>
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
                Notre IA analyse votre situation et suggère des stratégies d'optimisation
                adaptées (PER, LMNP, changement de régime...).
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
      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-slate-600">
          <p>© 2024 FiscalOptim - Optimisation fiscale pour freelances français</p>
        </div>
      </footer>
    </div>
  )
}
