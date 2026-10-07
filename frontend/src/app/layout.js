import './globals.css';

export const metadata = {
  title: 'RAG Laiane | Carregadores de Veículos Elétricos',
  description: 'Sistema RAG didático de notas fiscais e equipamentos de recarga para veículos elétricos (Wallbox, Estações Rápidas DC, FastEmbed e Supabase PGVector).',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>{children}</body>
    </html>
  );
}
