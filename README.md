# Alvinus AI Portfolio (Next.js)

Modern portfolio website built with:

- Frontend: Next.js + React
- Styling: Tailwind CSS
- Animation: Framer Motion + GSAP

## Run Locally

1. Install dependencies:

```bash
npm install
```

2. Start dev server:

```bash
npm run dev
```

3. Open `http://localhost:3000`.

## Build

```bash
npm run build
```

This project uses `output: "export"` in `next.config.js`, so the static output is generated in `out/`.

## Project Structure

- `app/` - Next.js App Router pages and global styles
- `components/` - reusable React components (Framer Motion + GSAP)
- `public/images` - image assets used by the portfolio
- `public/files` - downloadable files (CV, papers, resume)

## Notes

- Legacy Jekyll files are still in the repository, but the active frontend is now Next.js.
