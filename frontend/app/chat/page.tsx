"use client"

import { useState, useRef, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { apiClient, LLMAnalysisRequest, LLMAnalysisResponse, TaxCalculationRequest, TaxCalculationResponse } from "@/lib/api"
import { ArrowLeft, Send, Sparkles, User, Bot, AlertCircle } from "lucide-react"

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
  const [profileData, setProfileData] = useState<TaxCalculationRequest | null>(null)
  const [taxResult, setTaxResult] = useState<TaxCalculationResponse | null>(null)
  const [hasSimulatorData, setHasSimulatorData] = useState(false)
  const [sessionUserId, setSessionUserId] = useState<string>("")

  // Generate or retrieve unique session user ID
  useEffect(() => {
    const storedUserId = sessionStorage.getItem("fiscalOptim_sessionUserId")
    if (storedUserId) {
      setSessionUserId(storedUserId)
    } else {
      const newUserId = `user_${crypto.randomUUID()}`
      sessionStorage.setItem("fiscalOptim_sessionUserId", newUserId)
      setSessionUserId(newUserId)
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  // Charger les données du simulateur depuis sessionStorage
  useEffect(() => {
    const storedProfile = sessionStorage.getItem("fiscalOptim_profileData")
    const storedResult = sessionStorage.getItem("fiscalOptim_taxResult")

    if (storedProfile && storedResult) {
      try {
        setProfileData(JSON.parse(storedProfile))
        setTaxResult(JSON.parse(storedResult))
        setHasSimulatorData(true)
      } catch {
        console.error("Erreur lors du chargement des données du simulateur")
      }
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    // Vérifier si on a des données du simulateur
    if (!hasSimulatorData || !profileData || !taxResult) {
      const errorMessage: Message = {
        id: Date.now().toString() + "_no_data",
        role: "assistant",
        content: "Pour vous donner des conseils personnalisés, veuillez d'abord effectuer une simulation dans l'onglet Simulateur. Vos données seront alors utilisées pour personnaliser mes réponses.",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: "user",
        content: input,
        timestamp: new Date()
      }, errorMessage])
      setInput("")
      return
    }

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
        user_id: sessionUserId,
        conversation_id: conversationId,
        user_question: input,
        profile_data: profileData,
        tax_result: taxResult,
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
          <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent flex items-center gap-2">
            🇫🇷 FiscalOptim
            <span className="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-semibold">
              Beta
            </span>
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
                disabled={!input.trim() || loading || !sessionUserId}
                size="lg"
                aria-label="Envoyer le message"
              >
                <Send className="h-5 w-5" />
              </Button>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Appuyez sur Entrée pour envoyer, Shift+Entrée pour une nouvelle ligne
            </p>
          </CardContent>
        </Card>

        {/* Status Card */}
        {hasSimulatorData ? (
          <Card className="mt-4 border-green-200 bg-green-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-green-900 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500" />
                Données chargées
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-xs text-green-700">
                Vos données de simulation sont chargées. L'assistant utilisera votre situation réelle
                (CA: {profileData?.income?.professional_gross?.toLocaleString("fr-FR")}€,
                Statut: {profileData?.person?.status}) pour personnaliser ses conseils.
              </p>
            </CardContent>
          </Card>
        ) : (
          <Card className="mt-4 border-amber-200 bg-amber-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-amber-900 flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                Aucune donnée de simulation
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-xs text-amber-700">
                Pour des conseils personnalisés, effectuez d'abord une simulation dans l'onglet{" "}
                <Link href="/simulator" className="underline font-medium">
                  Simulateur
                </Link>.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
