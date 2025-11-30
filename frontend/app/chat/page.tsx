"use client"

import { useState, useRef, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { apiClient, LLMAnalysisRequest, LLMAnalysisResponse } from "@/lib/api"
import { ArrowLeft, Send, Sparkles, User, Bot } from "lucide-react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Bonjour! Je suis votre assistant fiscal IA. Comment puis-je vous aider à optimiser votre situation fiscale aujourd'hui?",
      timestamp: new Date(),
    }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | undefined>(undefined)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Mock profile and tax data - in production this would come from context/state
  const mockProfileData = {
    tax_year: 2024,
    person: {
      name: "Utilisateur",
      nb_parts: 1,
      status: "micro-entrepreneur",
    },
    income: {
      professional_gross: 50000,
      salary: 0,
      rental_income: 0,
      capital_income: 0,
      deductible_expenses: 5000,
    },
    deductions: {
      per_contributions: 0,
      alimony: 0,
      other_deductions: 0,
    },
    social: {
      urssaf_declared_ca: 50000,
      urssaf_paid: 7000,
    },
    pas_withheld: 0,
  }

  const mockTaxResult = {
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
      const request: LLMAnalysisRequest = {
        user_id: "demo_user",
        conversation_id: conversationId,
        user_question: input,
        profile_data: mockProfileData,
        tax_result: mockTaxResult,
        include_few_shot: true,
        include_context: true,
      }

      const response: LLMAnalysisResponse = await apiClient.analyzeLLM(request)

      // Update conversation ID
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
        content: `Désolé, une erreur s'est produite: ${err instanceof Error ? err.message : "Erreur inconnue"}. Veuillez réessayer.`,
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
    "Comment puis-je réduire mes impôts en tant que micro-entrepreneur ?",
    "Devrais-je passer au régime réel ?",
    "Quels sont les avantages du PER pour ma situation ?",
    "Comment optimiser mes cotisations sociales ?",
  ]

  const handleSuggestion = (question: string) => {
    setInput(question)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 to-white flex flex-col">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/optimizations" className="flex items-center gap-2 text-slate-600 hover:text-slate-900">
            <ArrowLeft className="h-4 w-4" />
            Retour
          </Link>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
            🇫🇷 FiscalOptim
          </h1>
          <div className="w-20" />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 container mx-auto px-4 py-8 flex flex-col max-w-4xl">
        <div className="text-center mb-6">
          <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
            Assistant fiscal IA
          </h2>
          <p className="text-slate-600 text-lg">
            Posez vos questions et obtenez des conseils personnalisés
          </p>
        </div>

        {/* Chat Messages */}
        <Card className="flex-1 flex flex-col mb-4 overflow-hidden">
          <CardContent className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.role === "assistant" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
                    <Bot className="h-5 w-5 text-white" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === "user"
                      ? "bg-violet-600 text-white"
                      : "bg-slate-100 text-slate-900"
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  <p className={`text-xs mt-2 ${message.role === "user" ? "text-violet-100" : "text-slate-500"}`}>
                    {message.timestamp.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}
                  </p>
                </div>

                {message.role === "user" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center">
                    <User className="h-5 w-5 text-slate-600" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-3 justify-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
                  <Bot className="h-5 w-5 text-white" />
                </div>
                <div className="max-w-[80%] rounded-2xl px-4 py-3 bg-slate-100">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </CardContent>
        </Card>

        {/* Suggested Questions */}
        {messages.length <= 1 && (
          <div className="mb-4">
            <p className="text-sm text-slate-600 mb-2">Questions suggérées:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((question, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSuggestion(question)}
                  className="text-xs"
                >
                  <Sparkles className="mr-1 h-3 w-3" />
                  {question}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <Card>
          <CardContent className="p-4">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Posez votre question fiscale..."
                disabled={loading}
                className="flex-1"
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                size="lg"
              >
                <Send className="h-5 w-5" />
              </Button>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Appuyez sur Entrée pour envoyer, Shift+Entrée pour une nouvelle ligne
            </p>
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="mt-4 border-blue-200 bg-blue-50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-blue-900">💡 Conseil</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-xs text-blue-700">
              Pour des conseils plus précis, assurez-vous d'avoir calculé vos impôts dans le simulateur.
              L'IA utilisera ces données pour personnaliser ses recommandations.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
