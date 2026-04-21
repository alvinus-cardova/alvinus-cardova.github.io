/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0f2138",
        ocean: "#0b75d7",
        teal: "#0f8a8a",
        mist: "#e9f2fb"
      },
      boxShadow: {
        glow: "0 22px 60px rgba(12, 58, 111, 0.2)"
      },
      backgroundImage: {
        "hero-gradient":
          "radial-gradient(circle at 8% 12%, rgba(11, 117, 215, 0.22), transparent 28%), radial-gradient(circle at 92% 10%, rgba(15, 138, 138, 0.2), transparent 30%), linear-gradient(180deg, #f4f9ff 0%, #edf6ff 42%, #f7fbff 100%)"
      },
      fontFamily: {
        display: ["var(--font-space-grotesk)"],
        body: ["var(--font-manrope)"]
      }
    }
  },
  plugins: []
};
