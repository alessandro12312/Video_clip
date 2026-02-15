import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const sessionActive = request.cookies.get("session_active");

  if (!sessionActive) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/home/:path*",
    "/esplora/:path*",
    "/carica/:path*",
    "/profilo/:path*",
    "/contest/:path*",
    "/notifiche/:path*",
    "/admin/:path*",
  ],
};
