"use client"

import { AlertTriangle, Info } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

/**
 * Legal disclaimer banner for tax calculation pages.
 * Required for regulatory compliance - displays on all calculation pages.
 */
export function LegalDisclaimerBanner() {
  return (
    <Alert variant="destructive" className="bg-amber-50 border-amber-200 text-amber-900">
      <AlertTriangle className="h-4 w-4 text-amber-600" />
      <AlertTitle className="text-amber-800 font-semibold">
        Avertissement important
      </AlertTitle>
      <AlertDescription className="text-amber-700 text-sm">
        Cet outil fournit des <strong>estimations informatives</strong> uniquement.
        Il ne remplace pas les services d'un expert-comptable ou conseiller fiscal agréé.
        Pour toute décision fiscale engageante, consultez un professionnel qualifié.
      </AlertDescription>
    </Alert>
  )
}

/**
 * Compact disclaimer for page footers.
 */
export function LegalDisclaimerFooter({ lastUpdate }: { lastUpdate?: string }) {
  return (
    <div className="text-xs text-slate-500 border-t pt-4 mt-8">
      <div className="flex items-start gap-2">
        <Info className="h-4 w-4 mt-0.5 shrink-0" />
        <div>
          <p className="mb-1">
            <strong>Mentions légales :</strong> Cet outil est à vocation informative uniquement.
            Les calculs sont basés sur les barèmes fiscaux publics et peuvent ne pas refléter
            votre situation personnelle complète.
          </p>
          <p className="mb-1">
            Pour les revenus supérieurs à 250 000€ (CEHR/CDHR applicable), une consultation
            professionnelle est <strong>fortement recommandée</strong>.
          </p>
          {lastUpdate && (
            <p className="text-slate-400">
              Barèmes fiscaux 2025 - Dernière mise à jour : {lastUpdate}
            </p>
          )}
          <p className="mt-2">
            Ce service n'est pas enregistré auprès de l'ORIAS, l'AMF, ou l'Ordre des Experts-Comptables.
          </p>
        </div>
      </div>
    </div>
  )
}

/**
 * High-net-worth warning for users with income > 250k.
 */
export function HighNetWorthWarning({ rfr }: { rfr: number }) {
  if (rfr < 250000) return null

  return (
    <Alert className="bg-red-50 border-red-200">
      <AlertTriangle className="h-4 w-4 text-red-600" />
      <AlertTitle className="text-red-800">
        Revenus élevés détectés (CEHR/CDHR applicable)
      </AlertTitle>
      <AlertDescription className="text-red-700 text-sm">
        Votre revenu fiscal de référence estimé ({rfr.toLocaleString('fr-FR')}€) dépasse 250 000€.
        La CEHR et potentiellement la CDHR s'appliquent à votre situation.
        <strong className="block mt-2">
          Pour une situation fiscale de cette complexité, consultez obligatoirement
          un expert-comptable ou avocat fiscaliste avant toute décision.
        </strong>
      </AlertDescription>
    </Alert>
  )
}

/**
 * Investment product risk warning.
 */
export function InvestmentRiskWarning() {
  return (
    <Alert className="bg-slate-50 border-slate-200">
      <Info className="h-4 w-4 text-slate-600" />
      <AlertTitle className="text-slate-800">
        Avertissement sur les produits d'investissement
      </AlertTitle>
      <AlertDescription className="text-slate-600 text-sm">
        Les recommandations d'optimisation (PER, LMNP, Girardin, FCPI/FIP) comportent des risques :
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Risque de perte en capital</li>
          <li>Blocage des fonds (PER : jusqu'à la retraite)</li>
          <li>Rendements non garantis</li>
        </ul>
        <strong className="block mt-2">
          Vérifiez l'adéquation à votre situation avec un conseiller en gestion de patrimoine (CGP).
        </strong>
      </AlertDescription>
    </Alert>
  )
}
