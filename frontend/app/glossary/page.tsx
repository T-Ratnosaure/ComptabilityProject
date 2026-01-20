"use client"

import Link from "next/link"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Info, Search, BookOpen, ArrowLeft } from "lucide-react"

interface GlossaryTerm {
  term: string
  definition: string
  category: string
  related?: string[]
  example?: string
}

const glossaryTerms: GlossaryTerm[] = [
  // Revenus et base imposable
  {
    term: "Chiffre d'Affaires (CA)",
    definition: "Total des recettes encaissées par un freelance ou une entreprise sur une période donnée, avant déduction des charges et frais professionnels.",
    category: "Revenus",
    related: ["BNC", "BIC", "Bénéfice net"],
    example: "Un consultant facturant 5 000€/mois a un CA annuel de 60 000€."
  },
  {
    term: "Bénéfice net",
    definition: "Résultat après déduction de toutes les charges professionnelles du chiffre d'affaires. C'est la base pour le calcul de l'impôt en régime réel.",
    category: "Revenus",
    related: ["Chiffre d'Affaires", "Charges déductibles"],
    example: "CA de 60 000€ - Charges de 15 000€ = Bénéfice net de 45 000€"
  },
  {
    term: "Revenu imposable",
    definition: "Montant des revenus soumis à l'impôt après application des abattements et déductions. En micro-entreprise, c'est le CA après abattement forfaitaire.",
    category: "Revenus",
    related: ["Abattement", "TMI"]
  },
  {
    term: "Revenu Fiscal de Référence (RFR)",
    definition: "Indicateur calculé par l'administration fiscale regroupant l'ensemble des revenus du foyer. Utilisé pour déterminer l'éligibilité à certains dispositifs (CEHR, CDHR, aides sociales).",
    category: "Revenus",
    related: ["CEHR", "CDHR"]
  },

  // Régimes fiscaux
  {
    term: "Micro-BNC",
    definition: "Régime simplifié pour les professions libérales (Bénéfices Non Commerciaux) avec un CA < 77 700€. Abattement forfaitaire de 34% pour frais professionnels.",
    category: "Régimes",
    related: ["BNC", "Abattement", "Régime réel"],
    example: "Consultant IT, médecin, avocat, formateur indépendant."
  },
  {
    term: "Micro-BIC",
    definition: "Régime simplifié pour les activités commerciales et artisanales (Bénéfices Industriels et Commerciaux). Abattement de 50% (services) ou 71% (vente/hébergement).",
    category: "Régimes",
    related: ["BIC", "Abattement"],
    example: "E-commerce, artisan, restaurateur, loueur meublé."
  },
  {
    term: "Régime réel",
    definition: "Régime fiscal où l'on déduit les charges réelles (et non un abattement forfaitaire). Obligatoire au-delà des plafonds micro ou sur option. Plus complexe mais souvent plus avantageux si charges > abattement.",
    category: "Régimes",
    related: ["Charges déductibles", "Micro-BNC", "Micro-BIC"]
  },
  {
    term: "BNC (Bénéfices Non Commerciaux)",
    definition: "Catégorie fiscale pour les revenus des professions libérales, activités intellectuelles et prestations de services non commerciales.",
    category: "Régimes",
    related: ["Micro-BNC", "Profession libérale"]
  },
  {
    term: "BIC (Bénéfices Industriels et Commerciaux)",
    definition: "Catégorie fiscale pour les revenus des activités commerciales, artisanales et industrielles.",
    category: "Régimes",
    related: ["Micro-BIC", "LMNP"]
  },

  // Impôt sur le revenu
  {
    term: "Barème progressif",
    definition: "Système de calcul de l'impôt où le taux augmente par tranches de revenus. En 2025 : 0% jusqu'à 11 497€, puis 11%, 30%, 41% et 45%.",
    category: "Impôt",
    related: ["TMI", "Tranche d'imposition"]
  },
  {
    term: "TMI (Taux Marginal d'Imposition)",
    definition: "Taux d'imposition appliqué à la dernière tranche de revenus. Indique le taux auquel sera imposé chaque euro supplémentaire gagné.",
    category: "Impôt",
    related: ["Barème progressif", "Tranche d'imposition"],
    example: "Avec un revenu imposable de 40 000€, votre TMI est de 30%."
  },
  {
    term: "Quotient familial",
    definition: "Mécanisme qui divise le revenu imposable par le nombre de parts fiscales du foyer, puis multiplie l'impôt résultant par ce même nombre. Avantage plafonné pour les enfants.",
    category: "Impôt",
    related: ["Parts fiscales", "Barème progressif"],
    example: "Couple marié avec 2 enfants = 3 parts fiscales."
  },
  {
    term: "Parts fiscales",
    definition: "Unité de calcul du quotient familial. Célibataire = 1 part, couple = 2 parts, +0.5 part par enfant (1 part à partir du 3ème).",
    category: "Impôt",
    related: ["Quotient familial"]
  },
  {
    term: "PAS (Prélèvement à la Source)",
    definition: "Mode de collecte de l'impôt sur le revenu directement sur les revenus au moment de leur perception. Le taux est personnalisé ou neutre.",
    category: "Impôt",
    related: ["Acompte"]
  },
  {
    term: "Acompte",
    definition: "Pour les indépendants, versement mensuel ou trimestriel de l'impôt calculé sur les revenus de l'année précédente. Régularisation l'année suivante.",
    category: "Impôt",
    related: ["PAS"]
  },

  // Cotisations sociales
  {
    term: "URSSAF",
    definition: "Organisme collectant les cotisations sociales des travailleurs indépendants. Finance la protection sociale (maladie, retraite, allocations familiales).",
    category: "Cotisations",
    related: ["Cotisations sociales", "Micro-entrepreneur"]
  },
  {
    term: "Cotisations sociales",
    definition: "Contributions obligatoires finançant la protection sociale. Pour les micro-entrepreneurs : environ 21.8% (BNC) ou 12.8% (BIC) du CA.",
    category: "Cotisations",
    related: ["URSSAF", "CFP"]
  },
  {
    term: "CFP (Contribution à la Formation Professionnelle)",
    definition: "Cotisation obligatoire permettant d'accéder à des formations. Taux de 0.1% à 0.3% selon l'activité.",
    category: "Cotisations",
    related: ["URSSAF"]
  },
  {
    term: "ACRE",
    definition: "Aide aux Créateurs et Repreneurs d'Entreprise. Exonération partielle de cotisations sociales la première année d'activité (taux réduit de 50%).",
    category: "Cotisations",
    related: ["URSSAF", "Micro-entrepreneur"]
  },

  // Contributions hauts revenus
  {
    term: "CEHR",
    definition: "Contribution Exceptionnelle sur les Hauts Revenus. Taxe additionnelle de 3% (250k-500k€) puis 4% (>500k€) sur le RFR des célibataires. Seuils doublés pour les couples.",
    category: "Hauts revenus",
    related: ["RFR", "CDHR"]
  },
  {
    term: "CDHR",
    definition: "Contribution Différentielle sur les Hauts Revenus (nouveau 2025). Garantit un taux effectif minimum de 20% pour les revenus > 250k€ (célibataire) ou 500k€ (couple).",
    category: "Hauts revenus",
    related: ["CEHR", "RFR"]
  },

  // Optimisation fiscale
  {
    term: "Abattement",
    definition: "Réduction forfaitaire appliquée aux revenus avant calcul de l'impôt. En micro-entreprise : 34% (BNC), 50% (BIC services) ou 71% (BIC vente).",
    category: "Optimisation",
    related: ["Micro-BNC", "Micro-BIC", "Revenu imposable"]
  },
  {
    term: "Charges déductibles",
    definition: "Dépenses professionnelles pouvant être soustraites du chiffre d'affaires en régime réel : loyer bureau, matériel, déplacements, formations, etc.",
    category: "Optimisation",
    related: ["Régime réel", "Bénéfice net"]
  },
  {
    term: "PER (Plan d'Épargne Retraite)",
    definition: "Produit d'épargne permettant de déduire les versements du revenu imposable (jusqu'à 10% des revenus, plafonds selon statut). Épargne bloquée jusqu'à la retraite sauf cas exceptionnels.",
    category: "Optimisation",
    related: ["Déduction fiscale", "TMI"],
    example: "Versement de 5 000€ sur un PER avec TMI 30% = économie d'impôt de 1 500€."
  },
  {
    term: "LMNP",
    definition: "Location Meublée Non Professionnelle. Statut fiscal permettant de louer un bien meublé avec avantages fiscaux importants (amortissement du bien en régime réel).",
    category: "Optimisation",
    related: ["BIC", "Amortissement", "Régime réel"]
  },
  {
    term: "Amortissement",
    definition: "Étalement comptable du coût d'un bien sur sa durée d'utilisation. En LMNP réel, permet de réduire fortement le revenu imposable sans sortie de trésorerie.",
    category: "Optimisation",
    related: ["LMNP", "Régime réel"]
  },
  {
    term: "Girardin Industriel",
    definition: "Dispositif de défiscalisation Outre-mer permettant une réduction d'impôt supérieure à l'investissement (environ 110-120%). Réservé aux contribuables avec IR significatif.",
    category: "Optimisation",
    related: ["Réduction d'impôt"],
    example: "Investissement de 10 000€ → Réduction d'impôt d'environ 11 500€."
  },
  {
    term: "FCPI/FIP",
    definition: "Fonds Commun de Placement dans l'Innovation / Fonds d'Investissement de Proximité. Réduction d'impôt de 18-25% du montant investi, avec risque de perte en capital.",
    category: "Optimisation",
    related: ["Réduction d'impôt"]
  },
  {
    term: "Crédit d'impôt",
    definition: "Somme déduite de l'impôt à payer. Si le crédit dépasse l'impôt dû, l'excédent est remboursé. Différent de la réduction d'impôt (non remboursable).",
    category: "Optimisation",
    related: ["Réduction d'impôt"]
  },
  {
    term: "Réduction d'impôt",
    definition: "Somme déduite de l'impôt à payer, plafonnée au montant de l'impôt (pas de remboursement si la réduction dépasse l'impôt).",
    category: "Optimisation",
    related: ["Crédit d'impôt", "Plafonnement des niches fiscales"]
  },
  {
    term: "Plafonnement des niches fiscales",
    definition: "Limite globale des avantages fiscaux à 10 000€ par an (+ 8 000€ pour Girardin/SOFICA). Au-delà, les réductions ne produisent plus d'effet.",
    category: "Optimisation",
    related: ["Réduction d'impôt", "Girardin Industriel"]
  },

  // Termes administratifs
  {
    term: "Déclaration 2042",
    definition: "Formulaire principal de déclaration des revenus. Les micro-entrepreneurs y reportent leur CA dans les cases spécifiques (5KO, 5KP...).",
    category: "Administratif",
    related: ["Déclaration 2035"]
  },
  {
    term: "Déclaration 2035",
    definition: "Déclaration des bénéfices non commerciaux en régime réel. Détaille les recettes et les charges professionnelles.",
    category: "Administratif",
    related: ["BNC", "Régime réel"]
  },
  {
    term: "Avis d'imposition",
    definition: "Document officiel indiquant le montant de l'impôt dû et le revenu fiscal de référence. Sert de justificatif pour de nombreuses démarches.",
    category: "Administratif",
    related: ["RFR"]
  }
]

const categories = [...new Set(glossaryTerms.map(t => t.category))]

export default function GlossaryPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const filteredTerms = glossaryTerms.filter(term => {
    const matchesSearch = searchQuery === "" ||
      term.term.toLowerCase().includes(searchQuery.toLowerCase()) ||
      term.definition.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesCategory = selectedCategory === null || term.category === selectedCategory

    return matchesSearch && matchesCategory
  })

  const groupedTerms = filteredTerms.reduce((acc, term) => {
    if (!acc[term.category]) {
      acc[term.category] = []
    }
    acc[term.category].push(term)
    return acc
  }, {} as Record<string, GlossaryTerm[]>)

  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent flex items-center gap-2">
              <BookOpen className="h-6 w-6 text-violet-600" />
              Glossaire Fiscal
              <span className="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-semibold">
                Beta
              </span>
            </h1>
          </Link>
          <div className="flex gap-3">
            <Link href="/simulator">
              <Button variant="outline">Simulateur</Button>
            </Link>
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-1" />
                Accueil
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Introduction */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
            Comprendre la fiscalité des freelances
          </h2>
          <p className="text-slate-600 max-w-2xl mx-auto">
            Ce glossaire explique les termes fiscaux essentiels pour les travailleurs indépendants en France.
            Utilisez la recherche ou filtrez par catégorie.
          </p>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              type="text"
              placeholder="Rechercher un terme..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              variant={selectedCategory === null ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(null)}
            >
              Tous
            </Button>
            {categories.map(category => (
              <Button
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(category)}
              >
                {category}
              </Button>
            ))}
          </div>
        </div>

        {/* Results count */}
        <p className="text-sm text-slate-500 mb-4">
          {filteredTerms.length} terme{filteredTerms.length > 1 ? 's' : ''} trouvé{filteredTerms.length > 1 ? 's' : ''}
        </p>

        {/* Glossary Terms */}
        {Object.entries(groupedTerms).map(([category, terms]) => (
          <div key={category} className="mb-8">
            <h3 className="text-xl font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-violet-500 rounded-full"></span>
              {category}
            </h3>
            <div className="grid gap-4">
              {terms.map(term => (
                <Card key={term.term} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg text-violet-700">{term.term}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base text-slate-700 mb-2">
                      {term.definition}
                    </CardDescription>
                    {term.example && (
                      <div className="bg-slate-50 rounded-lg p-3 text-sm text-slate-600 mb-2">
                        <span className="font-medium">Exemple :</span> {term.example}
                      </div>
                    )}
                    {term.related && term.related.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        <span className="text-xs text-slate-500">Voir aussi :</span>
                        {term.related.map(related => (
                          <button
                            key={related}
                            onClick={() => setSearchQuery(related)}
                            className="text-xs bg-violet-100 text-violet-700 px-2 py-1 rounded hover:bg-violet-200 transition-colors"
                          >
                            {related}
                          </button>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))}

        {filteredTerms.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-500">Aucun terme trouvé pour "{searchQuery}"</p>
            <Button variant="link" onClick={() => { setSearchQuery(""); setSelectedCategory(null); }}>
              Réinitialiser la recherche
            </Button>
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-12 p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-start gap-2">
            <Info className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-amber-800">
              <p className="font-semibold mb-1">Avertissement</p>
              <p>
                Ce glossaire fournit des définitions simplifiées à titre informatif.
                La législation fiscale évolue régulièrement. Pour des conseils adaptés à votre situation,
                consultez un expert-comptable ou un avocat fiscaliste.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t py-6 bg-slate-50 mt-8">
        <div className="container mx-auto px-4 text-center text-sm text-slate-500">
          <p>© 2025 FiscalOptim - Glossaire fiscal pour freelances français</p>
          <p className="mt-1">
            <Link href="/" className="text-violet-600 hover:underline">Accueil</Link>
            {" • "}
            <Link href="/simulator" className="text-violet-600 hover:underline">Simulateur</Link>
            {" • "}
            <Link href="/optimizations" className="text-violet-600 hover:underline">Optimisations</Link>
          </p>
        </div>
      </footer>
    </div>
  )
}
