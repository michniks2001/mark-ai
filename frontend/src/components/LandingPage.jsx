import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

export default function LandingPage() {
  const [repoUrl, setRepoUrl] = useState("")
  const [audience, setAudience] = useState("")
  const [error, setError] = useState("")

  function handleSubmit(e) {
    e.preventDefault()
    const isGithub = /^(https?:\/\/)?(www\.)?github\.com\/.+/.test(repoUrl)
    if (!isGithub) {
      setError("Enter a valid GitHub repository URL")
      return
    }
    setError("")
    console.log({ repoUrl, audience })
  }

  return (
    <div className="min-h-dvh flex flex-col">
      <header className="border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <a href="#" className="font-semibold text-purple-700">MarkAI</a>
          <nav className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
            <a href="#features" className="hover:text-purple-700">Features</a>
            <a href="#how-it-works" className="hover:text-purple-700">How it works</a>
            <a href="#cta" className="hover:text-purple-700">Start</a>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <section className="relative isolate bg-gradient-to-b from-amber-50 to-white">
          <div className="container mx-auto px-4 py-16 md:py-24 grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <div className="mb-4">
              <span className="inline-flex items-center rounded-full border border-amber-200 bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">AI + GitHub</span>
            </div>
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight">Turn your repo into a winning pitch deck</h1>
            <p className="mt-4 text-lg text-slate-600">Paste a GitHub link, pick a target audience, and get a curated, on-brand deck tailored to what you're marketing.</p>

            <Card className="mt-8 bg-white/80 shadow-sm" id="cta">
              <CardHeader>
                <CardTitle>Get started</CardTitle>
                <CardDescription>We'll analyze your repository and tailor messaging to your audience.</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="grid gap-4" aria-describedby={error ? "form-error" : undefined}>
                  <div className="grid gap-2">
                    <Label htmlFor="repoUrl">GitHub Repository URL</Label>
                    <Input
                      id="repoUrl"
                      type="url"
                      inputMode="url"
                      placeholder="https://github.com/org/repo"
                      value={repoUrl}
                      onChange={(e) => setRepoUrl(e.target.value)}
                      required
                      aria-invalid={!!error}
                      aria-describedby={error ? "form-error" : undefined}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="audience">Target Audience</Label>
                    <Textarea
                      id="audience"
                      placeholder="e.g., enterprise buyers in fintech, seed-stage investors, open-source contributors"
                      value={audience}
                      onChange={(e) => setAudience(e.target.value)}
                      rows={4}
                    />
                  </div>
                  {error ? (
                    <p id="form-error" role="alert" className="text-sm text-destructive">{error}</p>
                  ) : null}
                  <div className="flex items-center gap-3">
                    <Button type="submit" className="bg-purple-600 hover:bg-purple-700 text-white shadow-md">Generate pitch deck</Button>
                    <Button variant="outline" asChild className="border-slate-300 text-slate-700 hover:bg-slate-50">
                      <a href="#features">Learn more</a>
                    </Button>
                    <p className="text-sm text-slate-500">No signup required.</p>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          <div className="relative">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div className="h-3 w-3 rounded-full bg-red-400" />
                <div className="h-3 w-3 rounded-full bg-yellow-400" />
                <div className="h-3 w-3 rounded-full bg-green-400" />
              </div>
              <div className="mt-6 grid gap-4">
                <div className="h-4 w-40 rounded bg-amber-100" />
                <div className="h-3 w-64 rounded bg-amber-50" />
                <div className="h-3 w-56 rounded bg-amber-50" />
                <div className="h-48 rounded-xl border border-slate-200 bg-white" />
              </div>
            </div>
          </div>
          </div>
        </section>

        <section id="features" className="container mx-auto px-4 py-12 md:py-16">
          <div className="grid md:grid-cols-3 gap-6">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold">Repo-aware content</h3>
              <p className="mt-2 text-sm text-slate-600">Auto-extracts product value, features, and proof from README, code, and issues.</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold">Audience-tailored</h3>
              <p className="mt-2 text-sm text-slate-600">Messaging and structure adapt to investors, buyers, or contributors.</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold">Polished exports</h3>
              <p className="mt-2 text-sm text-slate-600">Export as slides or PDF with clean visuals and consistent branding.</p>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="container mx-auto px-4 pb-16">
          <ol className="grid md:grid-cols-3 gap-6">
            <li className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-sm text-muted-foreground">Step 1</p>
              <p className="mt-1 font-semibold">Paste your GitHub URL</p>
            </li>
            <li className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-sm text-muted-foreground">Step 2</p>
              <p className="mt-1 font-semibold">Describe your target audience</p>
            </li>
            <li className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-sm text-muted-foreground">Step 3</p>
              <p className="mt-1 font-semibold">Generate and refine your deck</p>
            </li>
          </ol>
        </section>
      </main>

      <footer className="border-t">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} Pitchcraft</p>
          <div className="flex items-center gap-4">
            <a href="#" className="hover:text-purple-700">Privacy</a>
            <a href="#" className="hover:text-purple-700">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
