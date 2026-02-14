import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-6xl font-bold gradient-text">404</h1>
      <p className="text-lg text-muted-foreground">Pagina non trovata</p>
      <Link
        href="/home"
        className="mt-4 rounded-lg gradient-bg px-6 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
      >
        Torna alla Home
      </Link>
    </div>
  );
}
