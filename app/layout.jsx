import { Manrope, Space_Grotesk } from "next/font/google";
import "./globals.css";

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
  weight: ["400", "500", "600", "700", "800"]
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  weight: ["500", "600", "700"]
});

export const metadata = {
  title: "Alvinus Cardova | AI Engineer",
  description:
    "AI Engineer portfolio focused on LLM systems, RAG architecture, computer vision, and MLOps."
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${manrope.variable} ${spaceGrotesk.variable} font-body text-ink antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
