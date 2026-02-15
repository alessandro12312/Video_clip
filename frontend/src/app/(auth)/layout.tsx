export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          {/* Brand logo — sorgente animazione post-login. Vedi login-transition-overlay.tsx per documentazione completa */}
          <h1 id="auth-brand-logo" className="text-3xl font-bold"><span className="gradient-text">V</span><span style={{ color: 'var(--gradient-end)' }}>ideo_cli</span><span className="gradient-text-reverse">p</span></h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Gaming Clips Social Network
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
