"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { apiClient, LLMAnalysisRequest, LLMAnalysisResponse, TaxCalculationRequest, TaxCalculationResponse, OptimizationResponse } from "@/lib/api"
import { Send, Bot, User, X, MessageSquare, Minimize2, Maximize2 } from "lucide-react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

interface ChatPanelProps {
  profileData: TaxCalculationRequest | null
  taxResult: TaxCalculationResponse | null
  optimizationResult: OptimizationResponse | null
  isOpen: boolean
  onToggle: () => void
}

export function ChatPanel({
  profileData,
  taxResult,
  optimizationResult,
  isOpen,
  onToggle
}: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Je suis votre assistant fiscal. Posez-moi vos questions sur vos optimisations ou votre situation fiscale.",
      timestamp: new Date(),
    }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | undefined>(undefined)
  const [isMinimized, setIsMinimized] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      // Construire le contexte avec les optimisations si disponibles
      const optimizationContext = optimizationResult ? {
        recommendations_count: optimizationResult.recommendations.length,
        potential_savings: optimizationResult.potential_savings_total,
        recommendations_summary: optimizationResult.recommendations.map(r => ({
          title: r.title,
          impact: r.impact_estimated,
          category: r.category,
          risk: r.risk,
        })),
      } : undefined

      // Créer les données de profil pour l'API (utiliser des valeurs par défaut si non disponibles)
      const apiProfileData: TaxCalculationRequest = profileData || {
        tax_year: 2025,
        person: { name: "User", nb_parts: 1, status: "micro_bnc" },
        income: { professional_gross: 50000, salary: 0, rental_income: 0, capital_income: 0, deductible_expenses: 0 },
        deductions: { per_contributions: 0, alimony: 0, other_deductions: 0 },
        social: { urssaf_declared_ca: 0, urssaf_paid: 0 },
        pas_withheld: 0,
      }

      // Créer les données de résultat fiscal pour l'API
      const apiTaxResult: TaxCalculationResponse = taxResult || {
        tax_year: 2025,
        impot: {
          revenu_imposable: 33000,
          part_income: 33000,
          impot_brut: 3000,
          impot_net: 3000,
          tmi: 0.11,
          tax_reductions: {},
          per_deduction_applied: 0,
          per_deduction_excess: 0,
          per_plafond_detail: null,
          tranches_detail: [],
          pas_withheld: 0,
          due_now: 3000,
        },
        socials: {
          urssaf_expected: 10900,
          urssaf_paid: 0,
          delta: 10900,
          rate_used: 0.218,
        },
      }

      const request: LLMAnalysisRequest = {
        user_id: "demo_user",
        conversation_id: conversationId,
        user_question: input,
        profile_data: apiProfileData,
        tax_result: apiTaxResult,
        optimization_result: optimizationResult || undefined,
        include_few_shot: true,
        include_context: true,
      }

      const response: LLMAnalysisResponse = await apiClient.analyzeLLM(request)

      if (!conversationId) {
        setConversationId(response.conversation_id)
      }

      const assistantMessage: Message = {
        id: response.message_id,
        role: "assistant",
        content: response.content,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage: Message = {
        id: Date.now().toString() + "_error",
        role: "assistant",
        content: `Erreur: ${err instanceof Error ? err.message : "Erreur inconnue"}. Réessayez.`,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const suggestedQuestions = [
    "Explique-moi cette optimisation",
    "Quels sont les risques ?",
    "Comment mettre en place le PER ?",
    "Est-ce adapté à ma situation ?",
  ]

  if (!isOpen) {
    return (
      <Button
        onClick={onToggle}
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
        size="icon"
      >
        <MessageSquare className="h-6 w-6" />
      </Button>
    )
  }

  return (
    <Card className={`fixed bottom-6 right-6 shadow-2xl border-violet-200 transition-all duration-300 ${
      isMinimized ? "w-80 h-14" : "w-96 h-[500px]"
    }`}>
      {/* Header */}
      <CardHeader className="p-3 border-b bg-gradient-to-r from-violet-600 to-indigo-600 rounded-t-lg">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white text-sm flex items-center gap-2">
            <Bot className="h-4 w-4" />
            Assistant fiscal
          </CardTitle>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-white hover:bg-white/20"
              onClick={() => setIsMinimized(!isMinimized)}
            >
              {isMinimized ? <Maximize2 className="h-3 w-3" /> : <Minimize2 className="h-3 w-3" />}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-white hover:bg-white/20"
              onClick={onToggle}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      {!isMinimized && (
        <>
          {/* Messages */}
          <CardContent className="flex-1 overflow-y-auto p-3 space-y-3 h-[350px]">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-2 ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.role === "assistant" && (
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
                    <Bot className="h-3 w-3 text-white" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-xl px-3 py-2 text-sm ${
                    message.role === "user"
                      ? "bg-violet-600 text-white"
                      : "bg-slate-100 text-slate-900"
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                </div>

                {message.role === "user" && (
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-slate-300 flex items-center justify-center">
                    <User className="h-3 w-3 text-slate-600" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-2 justify-start">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
                  <Bot className="h-3 w-3 text-white" />
                </div>
                <div className="rounded-xl px-3 py-2 bg-slate-100">
                  <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </CardContent>

          {/* Quick suggestions */}
          {messages.length <= 1 && (
            <div className="px-3 pb-2">
              <div className="flex flex-wrap gap-1">
                {suggestedQuestions.map((q, i) => (
                  <Button
                    key={i}
                    variant="outline"
                    size="sm"
                    className="text-xs h-6 px-2"
                    onClick={() => setInput(q)}
                  >
                    {q}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-3 border-t">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Posez votre question..."
                disabled={loading}
                className="flex-1 text-sm h-9"
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                size="sm"
                className="h-9 w-9 p-0"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </>
      )}
    </Card>
  )
}
