import type { Metadata } from "next";
import "leaflet/dist/leaflet.css";
import { Geist, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist",
});

const ibmMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-ibm-mono",
});

export const metadata: Metadata = {
  title: "AirMind",
  description: "AI-Powered Urban Air Quality Intelligence Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geist.variable} ${ibmMono.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-[#050b16] text-white">
        {children}
      </body>
    </html>
  );
}